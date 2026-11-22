"""Tests transactionnels de création de commandes COD."""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier

import pytest
from django.db import close_old_connections, connections
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import Utilisateur
from apps.catalogue.models import Annonce, Categorie
from apps.commandes.models import CodePromo, Commande, Livraison, Paiement
from apps.commandes.services_commandes import ConflitCommande, creer_commande


def headers(utilisateur):
    """Construit l'en-tête JWT de l'acheteur ou du vendeur de test."""
    return {"HTTP_AUTHORIZATION": f"Bearer {AccessToken.for_user(utilisateur)}"}


@pytest.fixture
def acteurs(db):
    """Crée le vendeur et deux acheteurs concurrents potentiels."""
    vendeur = Utilisateur.objects.create_user(
        nom="Vendeur commande", telephone="+237670000501", password="mot-de-passe-solide"
    )
    acheteur = Utilisateur.objects.create_user(
        nom="Acheteur commande", telephone="+237670000502", password="mot-de-passe-solide"
    )
    autre_acheteur = Utilisateur.objects.create_user(
        nom="Autre acheteur", telephone="+237670000503", password="mot-de-passe-solide"
    )
    return vendeur, acheteur, autre_acheteur


@pytest.fixture
def annonce(db, acteurs):
    """Fournit une annonce active pouvant être commandée une seule fois."""
    categorie = Categorie.objects.create(nom="Commande", slug="commande")
    return Annonce.objects.create(
        vendeur=acteurs[0],
        categorie=categorie,
        titre="Téléphone à commander",
        description="Produit disponible.",
        prix="10000.00",
        ville="Douala",
        statut=Annonce.Statut.ACTIVE,
    )


def corps(annonce_id, **complement):
    """Retourne le corps conforme à ``CommandeCreateRequest``."""
    resultat = {
        "annonce_id": annonce_id,
        "mode_paiement": "cod",
        "adresse_livraison": "Bonapriso, rue 1",
        "ville_livraison": "Douala",
    }
    resultat.update(complement)
    return resultat


@pytest.mark.django_db
def test_commande_cod_valide_cree_toutes_les_entites(client, acteurs, annonce):
    """Une commande COD confirme l'achat et crée paiement, livraison et QR unique."""
    response = client.post(
        "/v1/commandes",
        corps(annonce.id),
        content_type="application/json",
        **headers(acteurs[1]),
    )

    annonce.refresh_from_db()
    commande = Commande.objects.get()
    assert response.status_code == 201
    assert commande.acheteur == acteurs[1]
    assert commande.vendeur == acteurs[0]
    assert commande.statut == Commande.Statut.CONFIRMEE
    assert commande.montant_total == 10000
    assert commande.paiement.methode == Commande.ModePaiement.COD
    assert commande.paiement.statut == Paiement.Statut.EN_ATTENTE
    assert commande.livraison.statut == Livraison.Statut.PREPAREE
    assert commande.livraison.qr_code
    assert annonce.statut == Annonce.Statut.VENDUE


@pytest.mark.django_db
def test_commande_deja_vendue_et_second_acheteur_recoivent_409(client, acteurs, annonce):
    """La seconde tentative observe l'état vendu après le verrouillage initial."""
    premiere = client.post(
        "/v1/commandes", corps(annonce.id), content_type="application/json", **headers(acteurs[1])
    )
    seconde = client.post(
        "/v1/commandes", corps(annonce.id), content_type="application/json", **headers(acteurs[2])
    )

    assert premiere.status_code == 201
    assert seconde.status_code == 409
    assert Commande.objects.count() == 1


@pytest.mark.django_db(transaction=True)
def test_commandes_concurrentes_ne_peuvent_vendre_une_annonce_qu_une_fois(
    acteurs, annonce
):
    """Le verrou SQL laisse une transaction aboutir et rejette l'autre avec 409."""
    barriere = Barrier(2)
    donnees = corps(annonce.id)

    def tenter_commande(acheteur_id):
        """Exécute l'achat dans une connexion dédiée afin de tester le verrou réel."""
        close_old_connections()
        acheteur = Utilisateur.objects.get(pk=acheteur_id)
        barriere.wait()
        try:
            creer_commande(acheteur=acheteur, donnees=donnees)
            return 201
        except ConflitCommande:
            return 409
        finally:
            # Les connexions créées dans les threads ne sont pas gérées par
            # le cycle de vie de la connexion du thread principal pytest.
            # Leur fermeture explicite évite de bloquer la suppression de la
            # base de test PostgreSQL en fin de session.
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as executant:
        resultats = list(
            executant.map(tenter_commande, (acteurs[1].id, acteurs[2].id))
        )

    assert sorted(resultats) == [201, 409]
    assert Commande.objects.count() == 1


@pytest.mark.django_db
def test_commande_refuse_auto_achat_et_mobile_money(client, acteurs, annonce):
    """Le vendeur ne peut pas s'acheter et Mobile Money est explicitement indisponible."""
    auto_achat = client.post(
        "/v1/commandes", corps(annonce.id), content_type="application/json", **headers(acteurs[0])
    )
    mobile_money = client.post(
        "/v1/commandes",
        corps(annonce.id, mode_paiement="mobile_money", operateur="mtn"),
        content_type="application/json",
        **headers(acteurs[1]),
    )

    assert auto_achat.status_code == 422
    assert mobile_money.status_code == 501
    assert Commande.objects.count() == 0


@pytest.mark.django_db
def test_creation_commande_exige_un_jwt(client, annonce):
    """Un visiteur anonyme ne peut pas créer de commande."""
    response = client.post(
        "/v1/commandes", corps(annonce.id), content_type="application/json"
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_commande_inexistante_et_corps_invalide_renvoient_des_erreurs_normalisees(
    client, acteurs
):
    """Les absences et erreurs de corps restent exploitables par le frontend."""
    inexistante = client.post(
        "/v1/commandes", corps(999999), content_type="application/json", **headers(acteurs[1])
    )
    quantite_invalide = client.post(
        "/v1/commandes",
        corps(1, quantite=0),
        content_type="application/json",
        **headers(acteurs[1]),
    )
    mode_invalide = client.post(
        "/v1/commandes",
        corps(1, mode_paiement="carte"),
        content_type="application/json",
        **headers(acteurs[1]),
    )
    operateur_invalide = client.post(
        "/v1/commandes",
        corps(1, operateur="invalide"),
        content_type="application/json",
        **headers(acteurs[1]),
    )
    incomplet = client.post(
        "/v1/commandes",
        {"annonce_id": 1},
        content_type="application/json",
        **headers(acteurs[1]),
    )

    assert inexistante.status_code == 404
    assert inexistante.json()["code"] == "NOT_FOUND"
    for response in (quantite_invalide, mode_invalide, operateur_invalide, incomplet):
        assert response.status_code == 422
        assert response.json()["code"] == "VALIDATION_ERROR"
        assert response.json()["message"]


@pytest.mark.django_db
def test_liste_commandes_filtre_le_compte_connecte(client, acteurs, annonce):
    """La route documentée retourne uniquement les achats ou ventes demandés."""
    client.post(
        "/v1/commandes", corps(annonce.id), content_type="application/json", **headers(acteurs[1])
    )

    achats = client.get("/v1/commandes?role=acheteur", **headers(acteurs[1]))
    ventes = client.get("/v1/commandes?role=vendeur", **headers(acteurs[0]))
    interdit = client.get("/v1/commandes?role=invalide", **headers(acteurs[1]))

    assert achats.status_code == 200
    assert ventes.status_code == 200
    assert achats.json()[0]["acheteur_id"] == acteurs[1].id
    assert ventes.json()[0]["vendeur_id"] == acteurs[0].id
    assert interdit.status_code == 422


@pytest.mark.django_db
def test_code_promo_inexistant_et_long_est_ignore_sans_erreur_serveur(client, acteurs, annonce):
    """Un code promo est indépendant du champ de parrainage limité à 12 caractères."""
    code_long = "PROMOTION-VALIDE-PLUS-LONGUE"
    maintenant = timezone.now()
    CodePromo.objects.create(
        code=code_long,
        type=CodePromo.Type.GLOBALE,
        reduction_montant="500.00",
        date_debut=maintenant - timedelta(days=1),
        date_fin=maintenant + timedelta(days=1),
    )

    valide = client.post(
        "/v1/commandes", corps(annonce.id, code_promo=code_long),
        content_type="application/json", **headers(acteurs[1])
    )
    commande = Commande.objects.get()
    assert valide.status_code == 201
    assert valide.json()["montant_total"] == 9500.0
    assert commande.code_parrainage_utilise is None

    autre = Annonce.objects.create(
        vendeur=acteurs[0],
        categorie=annonce.categorie,
        titre="Annonce sans promo", description="Disponible.", prix="10000.00",
        ville="Douala", statut=Annonce.Statut.ACTIVE,
    )
    invalide = client.post(
        "/v1/commandes", corps(autre.id, code_promo="INEXISTANT"),
        content_type="application/json", **headers(acteurs[2])
    )
    assert invalide.status_code == 201
    assert "ignoré" in invalide.json()["message"]


@pytest.mark.django_db
def test_code_promo_valide_expire_et_plafonne(client, acteurs, annonce):
    """Seul un code valide réduit le total et incrémente son compteur d'usage."""
    maintenant = timezone.now()
    promo = CodePromo.objects.create(
        code="REDUC10",
        type=CodePromo.Type.GLOBALE,
        reduction_pct="10.00",
        date_debut=maintenant - timedelta(days=1),
        date_fin=maintenant + timedelta(days=1),
        usage_max=1,
    )
    response = client.post(
        "/v1/commandes",
        corps(annonce.id, code_promo=promo.code),
        content_type="application/json",
        **headers(acteurs[1]),
    )
    promo.refresh_from_db()

    assert response.status_code == 201
    assert response.json()["montant_total"] == 9000.0
    assert promo.usage_actuel == 1

    autre = Annonce.objects.create(
        vendeur=acteurs[0],
        categorie=annonce.categorie,
        titre="Autre téléphone",
        description="Disponible.",
        prix="10000.00",
        ville="Douala",
        statut=Annonce.Statut.ACTIVE,
    )
    plafonne = client.post(
        "/v1/commandes",
        corps(autre.id, code_promo=promo.code),
        content_type="application/json",
        **headers(acteurs[2]),
    )

    assert plafonne.status_code == 201
    assert plafonne.json()["montant_total"] == 10000.0
    assert "ignoré" in plafonne.json()["message"]


@pytest.mark.django_db
def test_code_promo_expire_est_ignore_sans_bloquer(client, acteurs, annonce):
    """Un code expiré laisse l'achat aboutir mais informe le client."""
    maintenant = timezone.now()
    CodePromo.objects.create(
        code="EXPIRE",
        type=CodePromo.Type.GLOBALE,
        reduction_montant="500.00",
        date_debut=maintenant - timedelta(days=2),
        date_fin=maintenant - timedelta(days=1),
    )

    response = client.post(
        "/v1/commandes",
        corps(annonce.id, code_promo="EXPIRE"),
        content_type="application/json",
        **headers(acteurs[1]),
    )

    assert response.status_code == 201
    assert response.json()["montant_total"] == 10000.0
    assert "ignoré" in response.json()["message"]


@pytest.mark.django_db
def test_code_promo_inactif_futur_ou_reserve_a_un_autre_vendeur_est_ignore(
    client, acteurs, annonce
):
    """Les règles de validité d'un code promo n'empêchent pas la commande COD."""
    maintenant = timezone.now()
    autre_vendeur = Utilisateur.objects.create_user(
        nom="Autre vendeur", telephone="+237670000504", password="mot-de-passe-solide"
    )
    codes = (
        CodePromo.objects.create(
            code="INACTIF", type=CodePromo.Type.GLOBALE, est_actif=False,
            reduction_montant="500.00", date_debut=maintenant - timedelta(days=1),
            date_fin=maintenant + timedelta(days=1),
        ),
        CodePromo.objects.create(
            code="FUTUR", type=CodePromo.Type.GLOBALE, reduction_montant="500.00",
            date_debut=maintenant + timedelta(days=1), date_fin=maintenant + timedelta(days=2),
        ),
        CodePromo.objects.create(
            code="BOUTIQUE", type=CodePromo.Type.BOUTIQUE, vendeur=autre_vendeur,
            reduction_montant="500.00", date_debut=maintenant - timedelta(days=1),
            date_fin=maintenant + timedelta(days=1),
        ),
    )

    for numero, promo in enumerate(codes, start=1):
        autre = Annonce.objects.create(
            vendeur=acteurs[0], categorie=annonce.categorie,
            titre=f"Annonce promo {numero}", description="Disponible.", prix="10000.00",
            ville="Douala", statut=Annonce.Statut.ACTIVE,
        )
        response = client.post(
            "/v1/commandes", corps(autre.id, code_promo=promo.code),
            content_type="application/json", **headers(acteurs[1]),
        )
        assert response.status_code == 201
        assert response.json()["montant_total"] == 10000.0
        assert "ignoré" in response.json()["message"]


@pytest.mark.django_db
def test_echec_livraison_declenche_le_rollback(client, acteurs, annonce, monkeypatch):
    maintenant = timezone.now()
    promo = CodePromo.objects.create(
        code="ROLLBACK", type=CodePromo.Type.GLOBALE, reduction_montant="500.00",
        date_debut=maintenant - timedelta(days=1), date_fin=maintenant + timedelta(days=1),
    )
    """Un échec en cours de transaction ne conserve aucune donnée partielle."""
    def echec_creation(**kwargs):
        raise RuntimeError("Erreur simulée du service de livraison")

    monkeypatch.setattr(
        "apps.commandes.services_commandes.Livraison.objects.create", echec_creation
    )

    with pytest.raises(RuntimeError):
        client.post(
            "/v1/commandes",
            corps(annonce.id, code_promo=promo.code),
            content_type="application/json",
            **headers(acteurs[1]),
        )

    annonce.refresh_from_db()
    assert Commande.objects.count() == 0
    assert Paiement.objects.count() == 0
    assert Livraison.objects.count() == 0
    assert annonce.statut == Annonce.Statut.ACTIVE
    promo.refresh_from_db()
    assert promo.usage_actuel == 0
