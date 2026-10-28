from pathlib import Path


def test_extensions_migrations_activate_pg_trgm_et_postgis():
    """Les index de recherche et la géolocalisation activent leurs extensions."""
    migrations_directory = Path(__file__).parents[1] / "migrations"
    extensions_migration = migrations_directory / "0001_enable_extensions.py"
    localisation_migration = migrations_directory / "0004_annonce_localisation_images.py"
    extensions_content = extensions_migration.read_text(encoding="utf-8")
    localisation_content = localisation_migration.read_text(encoding="utf-8")

    assert "pg_trgm" in extensions_content
    assert "CREATE EXTENSION" in extensions_content
    assert "CreateExtension(\"postgis\")" in localisation_content
    assert "idx_annonces_localisation_gist" in localisation_content
