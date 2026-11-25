"""Utilitaires communs de conversion et d'enregistrement des médias."""
from io import BytesIO
from uuid import uuid4

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image


def convertir_en_webp(fichier):
    """Convertit un fichier image validé en WebP pour uniformiser le stockage."""
    fichier.seek(0)
    with Image.open(fichier) as image:
        image.load()
        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGBA" if "transparency" in image.info else "RGB")
        contenu = BytesIO()
        image.save(contenu, format="WEBP", quality=85, method=6)
    fichier.seek(0)
    return ContentFile(contenu.getvalue())


def enregistrer_image(fichier, dossier):
    """Enregistre une image WebP sous un nom opaque et retourne son URL publique."""
    nom = f"{dossier}/{uuid4().hex}.webp"
    chemin = default_storage.save(nom, convertir_en_webp(fichier))
    return default_storage.url(chemin)


def nom_media_depuis_url(url, media_url):
    """Extrait un chemin relatif local depuis une URL média historique."""
    if not url or not url.startswith(media_url):
        return None
    return url.removeprefix(media_url).lstrip("/")
