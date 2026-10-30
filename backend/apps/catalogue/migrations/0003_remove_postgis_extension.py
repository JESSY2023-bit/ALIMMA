"""Retire PostGIS, resté présent après la migration historique d'extensions."""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("catalogue", "0002_categories_annonces"),
    ]

    operations = [
        migrations.RunSQL(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'annonces' AND column_name = 'localisation'
                ) THEN
                    ALTER TABLE annonces
                        ADD COLUMN IF NOT EXISTS latitude NUMERIC(9, 6),
                        ADD COLUMN IF NOT EXISTS longitude NUMERIC(9, 6);
                    EXECUTE '
                        UPDATE annonces
                        SET latitude = ST_Y(localisation::geometry)::numeric(9, 6),
                            longitude = ST_X(localisation::geometry)::numeric(9, 6)
                        WHERE localisation IS NOT NULL
                    ';
                    DROP INDEX IF EXISTS idx_annonces_localisation;
                    ALTER TABLE annonces DROP COLUMN localisation;
                END IF;
            END $$;

            CREATE INDEX IF NOT EXISTS idx_annonces_coordinates
                ON annonces (latitude, longitude);
            DROP EXTENSION IF EXISTS postgis_tiger_geocoder;
            DROP EXTENSION IF EXISTS postgis_topology;
            DROP EXTENSION IF EXISTS postgis;
            """,
            migrations.RunSQL.noop,
        ),
    ]
