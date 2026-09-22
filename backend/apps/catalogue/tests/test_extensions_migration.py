from pathlib import Path


def test_extensions_migration_declares_postgresql_extensions():
    migration = Path(__file__).parents[1] / "migrations" / "0001_enable_extensions.py"
    content = migration.read_text(encoding="utf-8")
    assert "postgis" in content
    assert "pg_trgm" in content
