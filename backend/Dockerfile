FROM python:3.12-slim

WORKDIR /app

# Dépendances système nécessaires à psycopg2 (driver PostgreSQL) et PostGIS
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev gdal-bin \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/dev.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]