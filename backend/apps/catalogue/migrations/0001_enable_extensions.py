"""Active les extensions PostgreSQL requises par le schéma cible."""
from django.db import migrations


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.RunSQL("CREATE EXTENSION IF NOT EXISTS postgis;", migrations.RunSQL.noop),
        migrations.RunSQL("CREATE EXTENSION IF NOT EXISTS pg_trgm;", migrations.RunSQL.noop),
    ]
