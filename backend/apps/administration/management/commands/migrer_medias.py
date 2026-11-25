"""Migre les médias conservés localement vers le stockage Django configuré."""
from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.accounts.models import Utilisateur
from apps.catalogue.models import AnnonceImage
from config.media import enregistrer_image, nom_media_depuis_url


class Command(BaseCommand):
    """Copie les URL locales persistées vers le stockage objet sans doublon."""

    help = "Migre les images locales vers le stockage média actuellement configuré."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-root",
            type=Path,
            default=settings.MEDIA_ROOT,
            help="Répertoire local historique contenant les fichiers média.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Affiche les fichiers concernés sans copier ni modifier la base.",
        )
        parser.add_argument(
            "--source-media-url",
            default="/media/",
            help="Préfixe URL historique du stockage local (défaut : /media/).",
        )

    def _copier(self, source_storage, nom_source, dossier, dry_run):
        """Lit une image locale, la convertit en WebP et retourne son URL cible."""
        if not source_storage.exists(nom_source):
            raise CommandError(f"Fichier média introuvable : {nom_source}")
        if dry_run:
            return None
        with source_storage.open(nom_source, "rb") as fichier:
            return enregistrer_image(fichier, dossier)

    def handle(self, *args, **options):
        """Migre d'abord les annonces, puis les photos de profil encore locales."""
        source_root = options["source_root"].resolve()
        dry_run = options["dry_run"]
        source_media_url = options["source_media_url"]
        if not source_root.is_dir():
            raise CommandError(f"Répertoire source introuvable : {source_root}")
        if settings.MEDIA_BACKEND == "local" and not dry_run:
            self.stderr.write(
                "MEDIA_BACKEND=local : la destination est locale. "
                "Configurez s3 avant la migration."
            )

        source_storage = FileSystemStorage(location=source_root, base_url=source_media_url)
        annonces_migrees = 0
        profils_migres = 0

        with transaction.atomic():
            for image in AnnonceImage.objects.select_related("annonce").iterator():
                nom_source = nom_media_depuis_url(image.url, source_media_url)
                if nom_source is None:
                    continue
                url = self._copier(
                    source_storage,
                    nom_source,
                    f"annonces/{image.annonce_id}",
                    dry_run,
                )
                annonces_migrees += 1
                if not dry_run:
                    image.url = url
                    image.save(update_fields=["url"])

            for utilisateur in Utilisateur.objects.exclude(photo_url__isnull=True).iterator():
                nom_source = nom_media_depuis_url(utilisateur.photo_url, source_media_url)
                if nom_source is None:
                    continue
                url = self._copier(
                    source_storage,
                    nom_source,
                    f"profils/{utilisateur.id}",
                    dry_run,
                )
                profils_migres += 1
                if not dry_run:
                    utilisateur.photo_url = url
                    utilisateur.save(update_fields=["photo_url", "updated_at"])

        mode = "Simulation" if dry_run else "Migration"
        self.stdout.write(
            self.style.SUCCESS(
                f"{mode} terminée : {annonces_migrees} image(s) d'annonce, "
                f"{profils_migres} photo(s) de profil."
            )
        )
