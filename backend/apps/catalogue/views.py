"""Vues du catalogue."""
from decimal import Decimal, InvalidOperation

from django.core.cache import cache
from django.core.paginator import EmptyPage, Paginator
from django.db.models import CharField, F, Q, TextField
from django.contrib.postgres.lookups import TrigramSimilar
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import APIException, NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import EstAdministrateur
from apps.accounts.serializers import ErreurSerializer

from .models import Annonce, Categorie
from .permissions import EstProprietaireAnnonce, PeutConsulterAnnonce
from .serializers import (
    AnnonceCreationSerializer,
    AnnonceDetailSerializer,
    AnnonceModificationSerializer,
    AnnonceSerializer,
    CategorieEcritureSerializer,
    CategorieSerializer,
    ListeAnnoncesSerializer,
)

# Django ne déclare pas automatiquement ce lookup pour les champs texte.
# Son enregistrement rend disponible l'opérateur PostgreSQL ``%``, qui peut
# utiliser l'index GIN ``idx_annonces_titre_trgm`` de la migration initiale.
CharField.register_lookup(TrigramSimilar)
TextField.register_lookup(TrigramSimilar)


# Seule la première page du tri par défaut est mise en cache. Les autres pages
# restent suffisamment variables pour être consultées directement en base.
PREMIERE_PAGE_ANNONCES_CACHE_KEY = "catalogue:annonces:actives:premiere-page"


def invalider_cache_annonces_publiques():
    """Invalide la liste publique mémorisée après une mutation d'annonce."""
    cache.delete(PREMIERE_PAGE_ANNONCES_CACHE_KEY)


def filtrer_annonces_publiques(queryset, params):
    """Applique les filtres combinables à un queryset déjà limité aux annonces actives.

    La recherche trigramme exploite l'extension ``pg_trgm`` et son index GIN
    sur le titre. Le ``icontains`` conserve en parallèle les correspondances
    exactes dans le titre comme dans la description.
    """
    q = params.get("q")
    categorie_id = params.get("categorie_id")
    ville = params.get("ville")
    prix_min = params.get("prix_min")
    prix_max = params.get("prix_max")
    etat = params.get("etat")
    type_vente = params.get("type_vente")

    filtres_actifs = any(
        valeur not in (None, "")
        for valeur in (q, categorie_id, ville, prix_min, prix_max, etat, type_vente)
    )
    if q:
        # ``trigram_similar`` s'appuie sur l'opérateur PostgreSQL ``%``,
        # compatible avec l'index GIN ``idx_annonces_titre_trgm``.
        queryset = queryset.filter(
            Q(titre__icontains=q)
            | Q(description__icontains=q)
            | Q(titre__trigram_similar=q)
            | Q(description__trigram_similar=q)
        )
    if categorie_id:
        try:
            categorie = Categorie.objects.get(pk=int(categorie_id))
        except (TypeError, ValueError) as exc:
            raise ValidationError("categorie_id doit être un entier.") from exc
        except Categorie.DoesNotExist as exc:
            raise ValidationError("La catégorie indiquée n'existe pas.") from exc
        # Un parent inclut ses enfants directs ; le modèle limite déjà
        # l'arborescence à ces deux niveaux.
        categories = [categorie.id]
        if categorie.parent_id is None:
            categories.extend(categorie.enfants.values_list("id", flat=True))
        queryset = queryset.filter(categorie_id__in=categories)
    if ville:
        queryset = queryset.filter(ville__iexact=ville)
    try:
        if prix_min:
            queryset = queryset.filter(prix__gte=Decimal(prix_min))
        if prix_max:
            queryset = queryset.filter(prix__lte=Decimal(prix_max))
    except (InvalidOperation, TypeError) as exc:
        raise ValidationError("prix_min et prix_max doivent être des nombres.") from exc
    if prix_min and prix_max and Decimal(prix_min) > Decimal(prix_max):
        raise ValidationError("prix_min ne peut pas être supérieur à prix_max.")
    if etat:
        if etat not in Annonce.Etat.values:
            raise ValidationError("etat doit valoir neuf ou occasion.")
        queryset = queryset.filter(etat=etat)
    if type_vente:
        if type_vente not in Annonce.TypeVente.values:
            raise ValidationError("type_vente doit valoir fixe ou enchere.")
        queryset = queryset.filter(type_vente=type_vente)
    return queryset, filtres_actifs


class ConflitCategorie(APIException):
    """Signale une suppression impossible sans la transformer en erreur serveur."""

    status_code = status.HTTP_409_CONFLICT
    default_code = "CONFLICT"
    default_detail = "La catégorie ne peut pas être supprimée."


class ConflitAnnonce(APIException):
    """Signale une transition interdite de l'état métier d'une annonce."""

    status_code = status.HTTP_409_CONFLICT
    default_code = "CONFLICT"
    default_detail = "Cette action n'est pas autorisée pour l'état actuel de l'annonce."


class AnnoncesView(APIView):
    """Publie une annonce authentifiée et liste seulement les annonces validées."""

    def get_permissions(self):
        """Rend la liste publique et réserve la publication aux comptes connectés."""
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(
        tags=["Annonces"],
        auth=[],
        responses={200: ListeAnnoncesSerializer, 422: ErreurSerializer},
        operation_id="annonces_list",
        summary="Lister les annonces publiquement visibles",
    )
    def get(self, request):
        """Retourne uniquement les annonces actives dans le format de pagination public."""
        try:
            page = int(request.query_params.get("page", 1))
            par_page = int(request.query_params.get("par_page", 20))
        except (TypeError, ValueError) as exc:
            raise ValidationError(
                "Les paramètres page et par_page doivent être des entiers."
            ) from exc
        if page < 1 or not 1 <= par_page <= 100:
            raise ValidationError(
                "page doit être positif et par_page doit être compris entre 1 et 100."
            )

        tri = request.query_params.get("tri", "date_publication")
        ordres = {
            "date_publication": ("-date_publication", "-id"),
            "prix_asc": ("prix", "id"),
            "prix_desc": ("-prix", "-id"),
        }
        if tri not in ordres:
            raise ValidationError("tri doit valoir date_publication, prix_asc ou prix_desc.")

        annonces = Annonce.objects.filter(statut=Annonce.Statut.ACTIVE)
        annonces, filtres_actifs = filtrer_annonces_publiques(annonces, request.query_params)

        # Le cache est réservé au cas le plus consulté, sans risquer de servir
        # une page associée à un tri ou à une taille de page différente.
        utiliser_cache = (
            page == 1 and par_page == 20 and tri == "date_publication" and not filtres_actifs
        )
        if utiliser_cache:
            reponse_cachee = cache.get(PREMIERE_PAGE_ANNONCES_CACHE_KEY)
            if reponse_cachee is not None:
                return Response(reponse_cachee)

        annonces = (
            annonces.select_related("vendeur", "categorie")
            .prefetch_related("images")
            .order_by(*ordres[tri])
        )
        paginator = Paginator(annonces, par_page)
        try:
            page_obj = paginator.page(page)
        except EmptyPage as exc:
            # Une page hors plage reste une liste vide, ce qui simplifie la
            # navigation côté client sans dévoiler d'annonces non actives.
            if page > paginator.num_pages and paginator.count:
                donnees = []
            else:
                raise ValidationError("La page demandée est invalide.") from exc
        else:
            donnees = AnnonceSerializer(page_obj.object_list, many=True).data

        resultat = {
            "data": donnees,
            "pagination": {
                "page": page,
                "par_page": par_page,
                "total": paginator.count,
                "total_pages": paginator.num_pages,
            },
        }
        if utiliser_cache:
            cache.set(PREMIERE_PAGE_ANNONCES_CACHE_KEY, resultat, timeout=300)
        return Response(resultat)

    @extend_schema(
        tags=["Annonces"],
        request={"multipart/form-data": AnnonceCreationSerializer},
        responses={201: AnnonceSerializer, 401: ErreurSerializer, 422: ErreurSerializer},
        operation_id="annonces_create",
        summary="Publier une nouvelle annonce",
    )
    def post(self, request):
        """Crée une annonce toujours soumise à la modération initiale."""
        serializer = AnnonceCreationSerializer(
            data=request.data,
            context={"vendeur": request.user},
        )
        serializer.is_valid(raise_exception=True)
        annonce = serializer.save()
        invalider_cache_annonces_publiques()
        return Response(AnnonceSerializer(annonce).data, status=status.HTTP_201_CREATED)


class AnnoncesCarteView(APIView):
    """Recherche les annonces actives autour d'un point géographique."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Recherche"],
        auth=[],
        responses={200: AnnonceSerializer(many=True), 422: ErreurSerializer},
        operation_id="annonces_carte_list",
        summary="Rechercher des annonces sur une carte",
    )
    def get(self, request):
        """Utilise ST_DWithin sur la colonne GEOGRAPHY indexée GiST."""
        try:
            latitude = Decimal(request.query_params["lat"])
            longitude = Decimal(request.query_params["lng"])
            rayon_km = Decimal(request.query_params.get("rayon_km", "10"))
        except (KeyError, InvalidOperation, TypeError) as exc:
            raise ValidationError(
                "lat, lng et rayon_km doivent être des nombres valides."
            ) from exc
        if not -90 <= latitude <= 90 or not -180 <= longitude <= 180 or rayon_km <= 0:
            raise ValidationError("lat, lng ou rayon_km est hors des limites autorisées.")
        if rayon_km > Decimal("100"):
            raise ValidationError("rayon_km ne peut pas dépasser 100 km.")

        annonces = Annonce.objects.filter(statut=Annonce.Statut.ACTIVE).extra(
            where=[
                "ST_DWithin(localisation, "
                "ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, %s)"
            ],
            params=[str(longitude), str(latitude), str(rayon_km * 1000)],
        )
        annonces = (
            annonces.select_related("vendeur", "categorie")
            .prefetch_related("images")
            .order_by("-date_publication", "-id")
        )
        return Response(AnnonceSerializer(annonces, many=True).data)


class MesAnnoncesView(APIView):
    """Liste les annonces du compte connecté, y compris celles non publiques."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Annonces"],
        responses={200: AnnonceSerializer(many=True), 401: ErreurSerializer},
        operation_id="utilisateurs_moi_annonces_list",
        summary="Lister mes annonces",
    )
    def get(self, request):
        """Expose aussi nb_vues au vendeur via le sérialiseur d'annonce."""
        annonces = (
            Annonce.objects.filter(vendeur=request.user)
            .select_related("vendeur", "categorie")
            .prefetch_related("images")
            .order_by("-created_at", "-id")
        )
        return Response(AnnonceSerializer(annonces, many=True).data)


class AnnonceDetailView(APIView):
    """Modifie ou retire logiquement une annonce pour son seul propriétaire."""

    def get_permissions(self):
        """Laisse le détail actif public, mais réserve ses mutations au vendeur."""
        if self.request.method == "GET":
            return [AllowAny(), PeutConsulterAnnonce()]
        return [IsAuthenticated(), EstProprietaireAnnonce()]

    @staticmethod
    def get_annonce(id):
        """Charge l'annonce ciblée sans filtrer son statut pour son vendeur."""
        try:
            return Annonce.objects.prefetch_related("images").get(pk=id)
        except Annonce.DoesNotExist as exc:
            raise NotFound("Annonce introuvable.") from exc

    @extend_schema(
        tags=["Annonces"],
        auth=[],
        responses={200: AnnonceDetailSerializer, 404: ErreurSerializer},
        operation_id="annonces_retrieve",
        summary="Consulter le détail public d'une annonce active",
    )
    def get(self, request, id):
        """Expose les annonces actives, ou les brouillons aux rôles autorisés."""
        try:
            annonce = (
                Annonce.objects.select_related("vendeur", "categorie")
                .prefetch_related("images")
                .get(pk=id)
            )
        except Annonce.DoesNotExist as exc:
            raise NotFound("Annonce introuvable.") from exc

        # Une annonce non active ne doit pas révéler son existence à un
        # visiteur. Ce contrôle est réalisé ici (plutôt que dans la permission)
        # afin d'éviter la réponse 401 automatique de DRF pour un anonyme.
        if annonce.statut != Annonce.Statut.ACTIVE and not request.user.is_authenticated:
            raise NotFound("Annonce introuvable.")

        # La permission objet laisse les annonces actives publiques et masque
        # les autres aux comptes qui ne sont ni vendeur, ni modérateur/admin.
        try:
            self.check_object_permissions(request, annonce)
        except PermissionDenied as exc:
            # Une 404 ne révèle pas qu'une annonce privée existe réellement.
            raise NotFound("Annonce introuvable.") from exc

        # L'adresse IP est le facteur de déduplication retenu au MVP. Redis
        # garantit une fenêtre de 24 h sans bloquer la réponse de détail.
        adresse_ip = request.META.get("REMOTE_ADDR", "inconnue")
        cle_vue = f"annonce:{annonce.id}:vue:{adresse_ip}"
        if cache.add(cle_vue, "1", timeout=24 * 60 * 60):
            Annonce.objects.filter(pk=annonce.pk).update(nb_vues=F("nb_vues") + 1)
            annonce.refresh_from_db(fields=["nb_vues"])
        return Response(AnnonceDetailSerializer(annonce).data)

    @extend_schema(
        tags=["Annonces"],
        request={"multipart/form-data": AnnonceModificationSerializer},
        responses={
            200: AnnonceSerializer,
            401: ErreurSerializer,
            403: ErreurSerializer,
            404: ErreurSerializer,
            409: ErreurSerializer,
            422: ErreurSerializer,
        },
        operation_id="annonces_partial_update",
        summary="Modifier sa propre annonce",
    )
    def patch(self, request, id):
        """Met à jour une annonce sauf lorsqu'elle a déjà été déclarée vendue."""
        annonce = self.get_annonce(id)
        self.check_object_permissions(request, annonce)
        if annonce.statut == Annonce.Statut.VENDUE:
            raise ConflitAnnonce("Une annonce vendue ne peut plus être modifiée.")
        serializer = AnnonceModificationSerializer(annonce, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        annonce = serializer.save()
        invalider_cache_annonces_publiques()
        annonce = Annonce.objects.select_related("vendeur", "categorie").prefetch_related(
            "images"
        ).get(pk=annonce.pk)
        return Response(AnnonceSerializer(annonce).data)

    @extend_schema(
        tags=["Annonces"],
        responses={
            204: None,
            401: ErreurSerializer,
            403: ErreurSerializer,
            404: ErreurSerializer,
            409: ErreurSerializer,
        },
        operation_id="annonces_destroy",
        summary="Supprimer logiquement sa propre annonce",
    )
    def delete(self, request, id):
        """Marque l'annonce comme expirée sans supprimer son historique en base."""
        annonce = self.get_annonce(id)
        self.check_object_permissions(request, annonce)
        if annonce.statut == Annonce.Statut.VENDUE:
            raise ConflitAnnonce("Une annonce vendue ne peut plus être supprimée.")
        annonce.statut = Annonce.Statut.EXPIREE
        annonce.save(update_fields=["statut", "updated_at"])
        invalider_cache_annonces_publiques()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PauseAnnonceView(APIView):
    """Bascule une annonce du vendeur entre les états active et en pause."""

    permission_classes = [IsAuthenticated, EstProprietaireAnnonce]
    # APIView n'infère pas automatiquement le schéma ; cet attribut permet à
    # drf-spectacular de documenter la représentation retournée sans warning.
    serializer_class = AnnonceSerializer

    @extend_schema(
        tags=["Annonces"],
        responses={
            200: AnnonceSerializer,
            401: ErreurSerializer,
            403: ErreurSerializer,
            404: ErreurSerializer,
            409: ErreurSerializer,
        },
        operation_id="annonces_pause",
        summary="Mettre en pause ou réactiver sa propre annonce",
    )
    def post(self, request, id):
        """Retire une annonce active du catalogue, ou la réactive si elle est en pause."""
        annonce = AnnonceDetailView.get_annonce(id)
        self.check_object_permissions(request, annonce)
        if annonce.statut == Annonce.Statut.ACTIVE:
            annonce.statut = Annonce.Statut.EN_PAUSE
        elif annonce.statut == Annonce.Statut.EN_PAUSE:
            annonce.statut = Annonce.Statut.ACTIVE
        else:
            raise ConflitAnnonce("Seule une annonce active ou en pause peut être basculée.")
        annonce.save(update_fields=["statut", "updated_at"])
        invalider_cache_annonces_publiques()
        annonce = Annonce.objects.select_related("vendeur", "categorie").prefetch_related(
            "images"
        ).get(pk=annonce.pk)
        return Response(AnnonceSerializer(annonce).data)


class CategoriesAdministrationView(APIView):
    """Expose l'arborescence publiquement et limite sa création aux administrateurs."""

    def get_permissions(self):
        """Déclare une permission explicite pour chaque méthode de la route."""
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), EstAdministrateur()]

    @extend_schema(
        tags=["Administration"],
        auth=[],
        responses={200: CategorieSerializer(many=True)},
        summary="Lister les catégories et sous-catégories",
    )
    def get(self, request):
        """Retourne les seules racines avec leurs enfants directs préchargés."""
        categories = Categorie.objects.filter(parent__isnull=True).prefetch_related("enfants")
        categories = categories.order_by("ordre_affichage", "nom", "id")
        return Response(CategorieSerializer(categories, many=True).data)

    @extend_schema(
        tags=["Administration"],
        request=CategorieEcritureSerializer,
        responses={
            201: CategorieSerializer,
            401: ErreurSerializer,
            403: ErreurSerializer,
            422: ErreurSerializer,
        },
        summary="Créer une catégorie ou sous-catégorie",
    )
    def post(self, request):
        """Crée une racine ou une sous-catégorie dans la profondeur autorisée."""
        serializer = CategorieEcritureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        categorie = serializer.save()
        return Response(CategorieSerializer(categorie).data, status=status.HTTP_201_CREATED)


class CategorieAdministrationDetailView(APIView):
    """Modifie ou supprime une catégorie pour le seul rôle administrateur."""

    permission_classes = [IsAuthenticated, EstAdministrateur]

    @staticmethod
    def get_categorie(id):
        """Retourne la catégorie demandée avec une erreur API normalisée si absente."""
        try:
            return Categorie.objects.get(pk=id)
        except Categorie.DoesNotExist as exc:
            raise NotFound("Catégorie introuvable.") from exc

    @extend_schema(
        tags=["Administration"],
        request=CategorieEcritureSerializer,
        responses={
            200: CategorieSerializer,
            401: ErreurSerializer,
            403: ErreurSerializer,
            404: ErreurSerializer,
            422: ErreurSerializer,
        },
        summary="Modifier une catégorie",
    )
    def patch(self, request, id):
        """Met à jour une catégorie, son parent et son slug généré si requis."""
        categorie = self.get_categorie(id)
        serializer = CategorieEcritureSerializer(categorie, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        categorie = serializer.save()
        return Response(CategorieSerializer(categorie).data)

    @extend_schema(
        tags=["Administration"],
        responses={
            204: None,
            401: ErreurSerializer,
            403: ErreurSerializer,
            404: ErreurSerializer,
            409: ErreurSerializer,
        },
        summary="Supprimer une catégorie vide",
    )
    def delete(self, request, id):
        """Supprime seulement une catégorie sans enfant ni annonce rattachée."""
        categorie = self.get_categorie(id)
        if categorie.enfants.exists():
            raise ConflitCategorie("Cette catégorie possède des sous-catégories.")
        if Annonce.objects.filter(categorie=categorie).exists():
            raise ConflitCategorie("Cette catégorie possède des annonces rattachées.")
        categorie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
