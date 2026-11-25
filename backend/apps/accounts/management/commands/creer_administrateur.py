"""Crée ou promeut de manière sûre le premier administrateur ALIMMA."""
import getpass
import os

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Utilisateur
from apps.accounts.utils import normaliser_telephone
from apps.administration.models import JournalModeration


class Command(BaseCommand):
    """Gère la création, promotion et réinitialisation d'un administrateur."""

    help = "Crée ou promeut un administrateur ALIMMA de façon traçable."

    def add_arguments(self, parser):
        """Déclare les options sans exposer le mot de passe dans le shell."""
        parser.add_argument("--telephone", required=True)
        parser.add_argument("--nom")
        parser.add_argument("--email")
        parser.add_argument("--promouvoir", action="store_true")
        parser.add_argument("--reinitialiser-mot-de-passe", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    @staticmethod
    def _masquer_telephone(telephone):
        """Retourne un numéro utilisable dans les logs sans révéler son contenu."""
        chiffres = telephone.lstrip("+")
        return f"+{chiffres[:3]} {chiffres[3]}•• ••• ••{chiffres[-2:]}"

    @staticmethod
    def _normaliser_email(email):
        """Prépare une adresse optionnelle et refuse les valeurs manifestement invalides."""
        if not email:
            return None
        email = email.strip().lower()
        if "@" not in email:
            raise CommandError("L'adresse e-mail fournie est invalide.")
        return email

    def _lire_mot_de_passe(self, utilisateur):
        """Obtient puis valide un secret fort sans jamais l'afficher."""
        mot_de_passe = os.environ.get("ALIMMA_ADMIN_PASSWORD")
        if mot_de_passe is None:
            mot_de_passe = getpass.getpass("Mot de passe administrateur : ")
            confirmation = getpass.getpass("Confirmez le mot de passe : ")
            if mot_de_passe != confirmation:
                raise CommandError("Les deux mots de passe ne correspondent pas.")
        if len(mot_de_passe) < 12:
            raise CommandError(
                "Le mot de passe administrateur doit contenir au moins 12 caractères."
            )
        try:
            validate_password(mot_de_passe, user=utilisateur)
        except ValidationError as exc:
            raise CommandError(" ".join(exc.messages)) from exc
        return mot_de_passe

    def _journaliser(self, administrateur, action, details):
        """Écrit une trace minimale, sans secret ni hash dans le journal métier."""
        JournalModeration.objects.create(
            moderateur=administrateur,
            action=action,
            cible_type="utilisateur",
            cible_id=administrateur.id,
            details=details,
        )

    def handle(self, *args, **options):
        """Applique l'opération demandée de manière atomique et rejouable."""
        try:
            telephone = normaliser_telephone(options["telephone"])
        except ValueError as exc:
            raise CommandError(str(exc)) from exc
        email = self._normaliser_email(options.get("email"))
        nom = (options.get("nom") or "").strip()
        masquer = self._masquer_telephone(telephone)
        dry_run = options["dry_run"]

        with transaction.atomic():
            utilisateur = (
                Utilisateur.objects.select_for_update().filter(telephone=telephone).first()
            )

            if utilisateur is None:
                if not nom:
                    raise CommandError("L'option --nom est obligatoire lors de la création.")
                if email and Utilisateur.objects.filter(email__iexact=email).exists():
                    raise CommandError("Cette adresse e-mail est déjà utilisée.")
                if dry_run:
                    self.stdout.write(f"Simulation : création de l'administrateur {masquer}.")
                    return
                candidat = Utilisateur(nom=nom, telephone=telephone, email=email)
                mot_de_passe = self._lire_mot_de_passe(candidat)
                utilisateur = Utilisateur.objects.create_superuser(
                    telephone=telephone,
                    password=mot_de_passe,
                    nom=nom,
                    email=email,
                )
                self._journaliser(
                    utilisateur,
                    "creation_administrateur",
                    "Administrateur créé par la commande de bootstrap.",
                )
                self.stdout.write(self.style.SUCCESS(f"Administrateur créé : {masquer}."))
                return

            est_administrateur = utilisateur.role == Utilisateur.Role.ADMINISTRATEUR
            if not est_administrateur and not options["promouvoir"]:
                raise CommandError(
                    "Ce numéro appartient déjà à un compte non administrateur. "
                    "Utilisez --promouvoir pour confirmer la promotion."
                )

            reinitialiser = options["reinitialiser_mot_de_passe"]
            if dry_run:
                if est_administrateur and not reinitialiser:
                    self.stdout.write(f"Simulation : {masquer} est déjà administrateur.")
                elif est_administrateur:
                    self.stdout.write(
                        f"Simulation : réinitialisation du mot de passe de {masquer}."
                    )
                else:
                    self.stdout.write(f"Simulation : promotion de {masquer} en administrateur.")
                return

            if not est_administrateur:
                utilisateur.role = Utilisateur.Role.ADMINISTRATEUR
                utilisateur.est_actif = True
                utilisateur.save(update_fields=["role", "est_actif", "updated_at"])
                self._journaliser(
                    utilisateur,
                    "promotion_administrateur",
                    "Compte promu administrateur par la commande de bootstrap.",
                )

            if reinitialiser:
                mot_de_passe = self._lire_mot_de_passe(utilisateur)
                utilisateur.set_password(mot_de_passe)
                utilisateur.updated_at = timezone.now()
                utilisateur.save(update_fields=["password_hash", "updated_at"])
                self._journaliser(
                    utilisateur,
                    "reinitialisation_mdp_administrateur",
                    "Mot de passe administrateur réinitialisé par la commande de bootstrap.",
                )

            if est_administrateur and not reinitialiser:
                self.stdout.write(f"Aucune action : {masquer} est déjà administrateur.")
            elif reinitialiser:
                self.stdout.write(self.style.SUCCESS(f"Administrateur mis à jour : {masquer}."))
            else:
                self.stdout.write(self.style.SUCCESS(f"Administrateur promu : {masquer}."))
