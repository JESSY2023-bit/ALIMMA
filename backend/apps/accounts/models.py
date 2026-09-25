"""Modèles utilisateurs conformes au schéma PostgreSQL ALIMMA."""
import secrets
import string
from decimal import Decimal

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import check_password, make_password
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


def generate_referral_code():
    """Génère un code de parrainage aléatoire de douze caractères."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(12))


class RoleUtilisateurField(models.CharField):
    """Champ PostgreSQL reposant sur l'énumération ``role_utilisateur``."""

    def db_type(self, connection):
        return "role_utilisateur"


class UtilisateurManager(BaseUserManager):
    """Manager dont l'identifiant principal est le téléphone."""

    def _new_referral_code(self):
        """Produit un code qui n'existe pas encore en base."""
        while True:
            code = generate_referral_code()
            if not self.filter(code_parrainage=code).exists():
                return code

    def create_user(self, telephone, password=None, **extra_fields):
        """Crée un utilisateur avec un mot de passe bcrypt et un code unique."""
        if not telephone:
            raise ValueError("Le téléphone est obligatoire.")
        if not password:
            raise ValueError("Le mot de passe est obligatoire.")
        if extra_fields.get("email"):
            extra_fields["email"] = self.normalize_email(extra_fields["email"])
        extra_fields.setdefault("role", Utilisateur.Role.UTILISATEUR)
        extra_fields.setdefault("code_parrainage", self._new_referral_code())
        utilisateur = self.model(telephone=telephone, **extra_fields)
        utilisateur.set_password(password)
        utilisateur.save(using=self._db)
        return utilisateur

    def create_superuser(self, telephone, password=None, **extra_fields):
        """Crée un administrateur compatible avec les commandes Django."""
        extra_fields["role"] = Utilisateur.Role.ADMINISTRATEUR
        extra_fields["est_actif"] = True
        return self.create_user(telephone, password, **extra_fields)


class Utilisateur(models.Model):
    """Compte ALIMMA authentifié avec le téléphone comme identifiant."""

    class Role(models.TextChoices):
        UTILISATEUR = "utilisateur", "Utilisateur"
        VENDEUR_PRO = "vendeur_pro", "Vendeur pro"
        MODERATEUR = "moderateur", "Modérateur"
        LIVREUR = "livreur", "Livreur"
        ADMINISTRATEUR = "administrateur", "Administrateur"

    nom = models.CharField(max_length=150)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    telephone = models.CharField(max_length=20, unique=True)
    password_hash = models.CharField(max_length=255)
    role = RoleUtilisateurField(
        max_length=20,
        choices=Role.choices,
        default=Role.UTILISATEUR,
    )
    photo_url = models.TextField(null=True, blank=True)
    note_moyenne = models.DecimalField(
        max_digits=2, decimal_places=1, default=Decimal("0.0"),
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    nb_avis = models.IntegerField(default=0)
    points_parrainage = models.IntegerField(default=0)
    code_parrainage = models.CharField(
        max_length=12,
        unique=True,
        default=generate_referral_code,
    )
    parraine_par = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="filleuls",
    )
    deux_fa_active = models.BooleanField(default=False)
    est_actif = models.BooleanField(default=True)
    derniere_connexion = models.DateTimeField(null=True, blank=True)
    date_inscription = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "telephone"
    REQUIRED_FIELDS = ["nom"]
    objects = UtilisateurManager()

    class Meta:
        db_table = "utilisateurs"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(note_moyenne__gte=0, note_moyenne__lte=5),
                name="utilisateurs_note_moyenne_entre_0_et_5",
            )
        ]

    def __str__(self):
        return self.telephone

    @property
    def is_active(self):
        """Expose le nom attendu par Django sans ajouter de colonne au schéma."""
        return self.est_actif

    @property
    def is_staff(self):
        return self.role == self.Role.ADMINISTRATEUR

    @property
    def is_superuser(self):
        return self.role == self.Role.ADMINISTRATEUR

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_username(self):
        return self.telephone

    def set_password(self, raw_password):
        """Stocke uniquement un hash bcrypt dans ``password_hash``."""
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        """Vérifie un mot de passe sans jamais exposer le hash."""
        return check_password(raw_password, self.password_hash)

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class Parrainage(models.Model):
    """Lien de parrainage appliqué lors de l'inscription d'un filleul."""

    parrain = models.ForeignKey(
        Utilisateur,
        on_delete=models.DO_NOTHING,
        related_name="parrainages",
    )
    filleul = models.OneToOneField(
        Utilisateur,
        on_delete=models.DO_NOTHING,
        related_name="parrainage_recu",
    )
    recompense_utilisee = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "parrainages"
