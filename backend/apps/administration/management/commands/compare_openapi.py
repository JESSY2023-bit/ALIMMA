"""Compare le schéma OpenAPI produit par Django avec le contrat de référence."""
from pathlib import Path

import yaml
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from drf_spectacular.generators import SchemaGenerator


class Command(BaseCommand):
    """Signale les écarts structurels entre le schéma généré et le contrat ALIMMA."""

    help = "Compare le schéma généré avec docs/openapi.yaml."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reference",
            type=Path,
            default=Path(settings.BASE_DIR).parent / "docs" / "openapi.yaml",
            help="Chemin vers le contrat OpenAPI de référence.",
        )
        parser.add_argument(
            "--fail-on-diff",
            action="store_true",
            help="Retourne un code d'échec lorsque des écarts sont détectés.",
        )

    @staticmethod
    def _names(items):
        """Retourne les noms déclarés dans une collection OpenAPI."""
        return {item["name"] for item in items or [] if "name" in item}

    @staticmethod
    def _operations(schema):
        """Construit l'ensemble ``(chemin, méthode)`` des opérations exposées."""
        methods = {"get", "post", "put", "patch", "delete", "head", "options"}
        return {
            (path, method.lower())
            for path, path_item in (schema.get("paths") or {}).items()
            for method in path_item
            if method.lower() in methods
        }

    @staticmethod
    def _report_set_difference(label, expected, generated, differences):
        """Ajoute les éléments attendus absents et les éléments inattendus."""
        for item in sorted(expected - generated):
            differences.append(f"{label} absent : {item}")
        for item in sorted(generated - expected):
            differences.append(f"{label} inattendu : {item}")

    def handle(self, *args, **options):
        reference_path = options["reference"]
        if not reference_path.is_file():
            raise CommandError(f"Contrat OpenAPI introuvable : {reference_path}")

        with reference_path.open(encoding="utf-8") as reference_file:
            reference = yaml.safe_load(reference_file) or {}
        generated = SchemaGenerator().get_schema(request=None, public=True)
        differences = []

        for field in ("title", "version", "description"):
            expected = (reference.get("info") or {}).get(field)
            actual = (generated.get("info") or {}).get(field)
            if expected != actual:
                differences.append(
                    f"info.{field} diffère : attendu={expected!r}, généré={actual!r}"
                )

        self._report_set_difference(
            "Tag", self._names(reference.get("tags")), self._names(generated.get("tags")), differences
        )
        self._report_set_difference(
            "Opération", self._operations(reference), self._operations(generated), differences
        )
        self._report_set_difference(
            "Schéma composant",
            set((reference.get("components") or {}).get("schemas") or {}),
            set((generated.get("components") or {}).get("schemas") or {}),
            differences,
        )
        self._report_set_difference(
            "Schéma de sécurité",
            set((reference.get("components") or {}).get("securitySchemes") or {}),
            set((generated.get("components") or {}).get("securitySchemes") or {}),
            differences,
        )

        if not differences:
            self.stdout.write(self.style.SUCCESS("Aucun écart OpenAPI détecté."))
            return

        self.stdout.write(self.style.WARNING("Écarts OpenAPI détectés :"))
        for difference in differences:
            self.stdout.write(f"- {difference}")
        if options["fail_on_diff"]:
            raise CommandError(f"{len(differences)} écart(s) OpenAPI détecté(s).")
