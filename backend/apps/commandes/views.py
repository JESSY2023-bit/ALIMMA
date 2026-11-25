"""Vues authentifiées de gestion du panier Redis."""
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers import ErreurSerializer
from apps.catalogue.models import Annonce

from .serializers import (
    CommandeCreationSerializer,
    CommandeSerializer,
    MotifCommandeSerializer,
    PanierArticleEcritureSerializer,
    PanierQuantiteSerializer,
    PanierSerializer,
)
from .etats import transitionner
from .models import Commande, HistoriqueStatutCommande
from .services_commandes import creer_commande
from .services import construire_panier, enregistrer_contenu, lire_contenu


def reponse_panier(utilisateur_id):
    """Sérialise le panier recalculé avant de le remettre au renderer JSON."""
    panier = construire_panier(utilisateur_id)
    return Response(PanierSerializer(panier).data)


class PanierView(APIView):
    """Lit ou vide le panier du compte authentifié."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Panier & Commandes"],
        responses={200: PanierSerializer, 401: ErreurSerializer},
        operation_id="panier_retrieve",
        summary="Consulter mon panier",
    )
    def get(self, request):
        """Retourne les montants recalculés depuis les annonces actives."""
        return reponse_panier(request.user.id)

    @extend_schema(
        tags=["Panier & Commandes"],
        responses={204: None, 401: ErreurSerializer},
        operation_id="panier_destroy",
        summary="Vider mon panier",
    )
    def delete(self, request):
        """Supprime uniquement la clé Redis du panier authentifié."""
        enregistrer_contenu(request.user.id, {})
        return Response(status=status.HTTP_204_NO_CONTENT)


class PanierArticlesView(APIView):
    """Ajoute une annonce active au panier du compte authentifié."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Panier & Commandes"],
        request=PanierArticleEcritureSerializer,
        responses={
            200: PanierSerializer,
            401: ErreurSerializer,
            404: ErreurSerializer,
            422: ErreurSerializer,
        },
        operation_id="panier_articles_create",
        summary="Ajouter un article au panier",
    )
    def post(self, request):
        """Ajoute ou cumule la quantité sans accepter un prix provenant du client."""
        serializer = PanierArticleEcritureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        annonce_id = serializer.validated_data["annonce_id"]
        try:
            annonce = Annonce.objects.get(pk=annonce_id, statut=Annonce.Statut.ACTIVE)
        except Annonce.DoesNotExist as exc:
            raise NotFound("Annonce active introuvable.") from exc
        if annonce.vendeur_id == request.user.id:
            raise ValidationError("Vous ne pouvez pas ajouter votre propre annonce au panier.")
        contenu = lire_contenu(request.user.id)
        cle = str(annonce_id)
        contenu[cle] = contenu.get(cle, 0) + serializer.validated_data["quantite"]
        enregistrer_contenu(request.user.id, contenu)
        return reponse_panier(request.user.id)


class PanierArticleDetailView(APIView):
    """Modifie ou retire une ligne de panier identifiée par son annonce."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Panier & Commandes"],
        request=PanierQuantiteSerializer,
        responses={
            200: PanierSerializer,
            401: ErreurSerializer,
            404: ErreurSerializer,
            422: ErreurSerializer,
        },
        operation_id="panier_articles_partial_update",
        summary="Modifier la quantité d'un article",
    )
    def patch(self, request, annonce_id):
        """Remplace la quantité d'une ligne existante par une valeur strictement positive."""
        serializer = PanierQuantiteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contenu = lire_contenu(request.user.id)
        cle = str(annonce_id)
        if cle not in contenu:
            raise NotFound("Cet article n'est pas dans votre panier.")
        contenu[cle] = serializer.validated_data["quantite"]
        enregistrer_contenu(request.user.id, contenu)
        return reponse_panier(request.user.id)

    @extend_schema(
        tags=["Panier & Commandes"],
        responses={204: None, 401: ErreurSerializer, 404: ErreurSerializer},
        operation_id="panier_articles_destroy",
        summary="Retirer un article du panier",
    )
    def delete(self, request, annonce_id):
        """Retire une seule ligne sans toucher aux autres articles Redis."""
        contenu = lire_contenu(request.user.id)
        try:
            del contenu[str(annonce_id)]
        except KeyError as exc:
            raise NotFound("Cet article n'est pas dans votre panier.") from exc
        enregistrer_contenu(request.user.id, contenu)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommandesView(APIView):
    """Liste ou crée les commandes auxquelles participe le compte connecté."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Panier & Commandes"],
        parameters=[
            OpenApiParameter("role", OpenApiTypes.STR, enum=["acheteur", "vendeur"]),
            OpenApiParameter("statut", OpenApiTypes.STR, enum=Commande.Statut.values),
        ],
        responses={
            200: CommandeSerializer(many=True),
            401: ErreurSerializer,
            422: ErreurSerializer,
        },
        operation_id="commandes_list",
        summary="Lister mes commandes",
    )
    def get(self, request):
        """Retourne les achats et ventes du compte, filtrables par rôle et statut."""
        role = request.query_params.get("role")
        statut = request.query_params.get("statut")

        if role not in (None, "acheteur", "vendeur"):
            raise ValidationError({"role": "La valeur doit être acheteur ou vendeur."})
        if statut and statut not in Commande.Statut.values:
            raise ValidationError({"statut": "Statut de commande invalide."})

        commandes = Commande.objects.order_by("-created_at").select_related(
            "annonce", "acheteur", "vendeur", "livraison"
        ).prefetch_related(
            Prefetch(
                "historique_statuts",
                queryset=HistoriqueStatutCommande.objects.select_related("acteur"),
            )
        )
        if role == "acheteur":
            commandes = commandes.filter(acheteur=request.user)
        elif role == "vendeur":
            commandes = commandes.filter(vendeur=request.user)
        else:
            commandes = commandes.filter(Q(acheteur=request.user) | Q(vendeur=request.user))
        if statut:
            commandes = commandes.filter(statut=statut)
        return Response(CommandeSerializer(commandes, many=True).data)

    @extend_schema(
        tags=["Panier & Commandes"],
        request=CommandeCreationSerializer,
        responses={
            201: CommandeSerializer,
            401: ErreurSerializer,
            404: ErreurSerializer,
            409: ErreurSerializer,
            422: ErreurSerializer,
        },
        operation_id="commandes_create",
        summary="Passer une commande d'achat direct",
    )
    def post(self, request):
        """Crée la commande, le paiement et la livraison dans une transaction atomique."""
        serializer = CommandeCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        commande, message = creer_commande(
            acheteur=request.user,
            donnees=serializer.validated_data,
        )
        donnees_reponse = CommandeSerializer(commande).data
        if message:
            donnees_reponse["message"] = message
        return Response(donnees_reponse, status=status.HTTP_201_CREATED)


def commande_visible_pour(utilisateur, commande_id):
    """Retourne une commande visible ou une 404 afin de ne pas révéler son existence."""
    queryset = Commande.objects.select_related(
        "annonce", "acheteur", "vendeur", "livraison"
    ).prefetch_related(
        Prefetch(
            "historique_statuts",
            queryset=HistoriqueStatutCommande.objects.select_related("acteur"),
        )
    )
    if getattr(utilisateur, "role", None) in {"moderateur", "administrateur"}:
        return get_object_or_404(queryset, pk=commande_id)
    filtres = (
        Q(acheteur=utilisateur)
        | Q(vendeur=utilisateur)
        | Q(livraison__livreur=utilisateur)
    )
    return get_object_or_404(queryset, filtres, pk=commande_id)


class CommandeDetailView(APIView):
    """Expose le suivi d'une commande à ses seuls participants métier."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Panier & Commandes"],
        responses={200: CommandeSerializer, 401: ErreurSerializer, 404: ErreurSerializer},
        operation_id="commandes_retrieve",
        summary="Consulter le détail et l'historique d'une commande",
    )
    def get(self, request, id):
        """Retourne la commande si l'acteur peut légitimement en suivre l'état."""
        return Response(CommandeSerializer(commande_visible_pour(request.user, id)).data)


class CommandeActionView(APIView):
    """Délègue les actions HTTP à la machine d'états transactionnelle."""

    permission_classes = [IsAuthenticated]
    actions = {
        "accepter": Commande.Statut.ACCEPTEE,
        "refuser": Commande.Statut.ANNULEE,
        "annuler": Commande.Statut.ANNULEE,
        "expedier": Commande.Statut.EXPEDIEE,
        "confirmer-reception": Commande.Statut.TERMINEE,
    }

    @extend_schema(
        tags=["Panier & Commandes"],
        request=MotifCommandeSerializer,
        responses={
            200: CommandeSerializer,
            401: ErreurSerializer,
            404: ErreurSerializer,
            409: ErreurSerializer,
            422: ErreurSerializer,
        },
        summary="Faire évoluer une commande dans son cycle d'achat direct",
    )
    def post(self, request, id, action):
        """Valide le motif du refus puis applique la transition demandée."""
        commande = commande_visible_pour(request.user, id)
        motif = None
        if action == "refuser":
            serializer = MotifCommandeSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            motif = serializer.validated_data["motif"]
        commande = transitionner(commande, self.actions[action], request.user, motif)
        # La transition recharge l'objet verrouillé ; ce nouveau chargement
        # préserve le format complet, notamment l'historique fraîchement créé.
        return Response(CommandeSerializer(commande_visible_pour(request.user, commande.id)).data)
