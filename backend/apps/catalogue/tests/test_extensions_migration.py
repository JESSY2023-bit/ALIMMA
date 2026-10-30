from pathlib import Path


def test_extensions_migration_keeps_pg_trgm_and_removes_postgis():
    extensions_migration = (
        Path(__file__).parents[1] / "migrations" / "0001_enable_extensions.py"
    )
    replacement_migration = (
        Path(__file__).parents[1]
        / "migrations"
        / "0003_remove_postgis_extension.py"
    )

    extensions_content = extensions_migration.read_text(encoding="utf-8")
    assert "pg_trgm" in extensions_content
    assert "postgis" not in extensions_content
    replacement_content = replacement_migration.read_text(encoding="utf-8")
    assert "DROP EXTENSION IF EXISTS postgis_tiger_geocoder" in replacement_content
    assert "DROP EXTENSION IF EXISTS postgis_topology" in replacement_content
    assert "DROP EXTENSION IF EXISTS postgis" in replacement_content
