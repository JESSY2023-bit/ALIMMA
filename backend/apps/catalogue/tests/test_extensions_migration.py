from pathlib import Path


def test_extensions_migration_only_activates_pg_trgm():
    migrations_directory = Path(__file__).parents[1] / "migrations"
    extensions_migration = migrations_directory / "0001_enable_extensions.py"
    extensions_content = extensions_migration.read_text(encoding="utf-8")

    assert "pg_trgm" in extensions_content
    assert "CREATE EXTENSION" in extensions_content
    for migration_file in migrations_directory.glob("*.py"):
        assert "postgis" not in migration_file.read_text(encoding="utf-8").lower()
