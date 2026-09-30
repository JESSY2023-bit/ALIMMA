# Installation et déploiement d'ALIMMA

Ce document décrit l'installation locale du backend ALIMMA et le démarrage
avec Docker Compose. L'API est une application Django 5/DRF utilisant
PostgreSQL 16 avec PostGIS et Redis.

> `docs/schema.sql` est un document de conception. Ne l'exécutez pas : les
> tables et extensions sont créées exclusivement par les migrations Django.

## Prérequis

- Git ;
- Docker Desktop avec Docker Compose v2 ;
- Python 3.12 et `pip` pour une exécution hors Docker ;
- PostgreSQL n'est pas requis localement si Docker est utilisé ;
- Node.js est requis seulement lorsque le projet frontend React est présent.

Vérifiez Docker :

```bash
docker --version
docker compose version
```

Sous Windows, démarrez Docker Desktop avant les commandes suivantes.

## Variables d'environnement

Deux fichiers sont utilisés :

- `infra/.env` définit les variables interpolées par Docker Compose ;
- `backend/.env` définit les variables lues par Django.

Ils sont ignorés par Git. Créez-les à partir des exemples :

```bash
cp infra/.env.example infra/.env
cp backend/.env.example backend/.env
```

Pour un démarrage Docker, adaptez au minimum `backend/.env` ainsi :

```dotenv
DJANGO_SETTINGS_MODULE=config.settings.dev
DJANGO_SECRET_KEY=remplacez-par-une-cle-longue-et-aleatoire
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=alimma
POSTGRES_USER=alimma
POSTGRES_PASSWORD=choisissez-un-mot-de-passe-fort
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
FEATURE_2FA_ENABLED=false
```

Les valeurs `POSTGRES_DB`, `POSTGRES_USER` et `POSTGRES_PASSWORD` de
`backend/.env` doivent correspondre à celles de `infra/.env`. Le port hôte
par défaut est `5433` afin d'éviter un conflit avec un PostgreSQL local ; il
reste `5432` à l'intérieur du réseau Docker.

Ne versionnez jamais les fichiers `.env` ni une clé Django ou un mot de passe
de production.

## Démarrage avec Docker

Depuis la racine du dépôt :

```bash
docker compose --env-file infra/.env -f infra/docker-compose.yml \
  up -d --build postgres redis backend
```

Consultez l'état et les journaux :

```bash
docker compose --env-file infra/.env -f infra/docker-compose.yml ps
docker compose --env-file infra/.env -f infra/docker-compose.yml logs -f backend
```

Appliquez ensuite les migrations :

```bash
docker compose --env-file infra/.env -f infra/docker-compose.yml \
  exec backend python manage.py migrate
```

Vérifiez l'installation :

```bash
docker compose --env-file infra/.env -f infra/docker-compose.yml \
  exec backend python manage.py check

docker compose --env-file infra/.env -f infra/docker-compose.yml \
  exec backend python -m pytest
```

L'API est alors disponible sur `http://127.0.0.1:8000/v1/` et Swagger UI sur
`http://127.0.0.1:8000/v1/docs/`.

Pour arrêter les services :

```bash
docker compose --env-file infra/.env -f infra/docker-compose.yml down
```

Pour supprimer aussi les données locales PostgreSQL et Redis :

```bash
docker compose --env-file infra/.env -f infra/docker-compose.yml down -v
```

> Cette dernière commande est destructive : elle efface les volumes de
> développement.

## Démarrage hors Docker

Lancez PostgreSQL/PostGIS et Redis, puis configurez `backend/.env` avec :

```dotenv
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5433
REDIS_URL=redis://127.0.0.1:6379/1
```

Installez les dépendances et démarrez Django :

```bash
cd backend
py -m pip install -r requirements/dev.txt
py manage.py migrate
py manage.py check
py -m pytest
py manage.py runserver
```

Sous macOS/Linux, remplacez `py` par `python3` si nécessaire.

## Commandes utiles

```bash
# Générer puis comparer le contrat OpenAPI avec docs/openapi.yaml
cd backend
py manage.py compare_openapi

# Faire échouer la commande si un écart existe (CI)
py manage.py compare_openapi --fail-on-diff

# Ouvrir un shell Django dans Docker
docker compose --env-file infra/.env -f infra/docker-compose.yml \
  exec backend python manage.py shell

# Créer un administrateur Django
docker compose --env-file infra/.env -f infra/docker-compose.yml \
  exec backend python manage.py createsuperuser
```

L'administration Django est disponible sur `http://127.0.0.1:8000/admin/`
après création d'un administrateur.

## Frontend

Le fichier `infra/docker-compose.yml` référence un service `frontend` qui
attend un dossier `frontend/`, son `Dockerfile` et son `.env`. Ce dossier
n'est pas présent dans ce dépôt à ce jour. Démarrez donc explicitement
`postgres`, `redis` et `backend` comme dans la commande ci-dessus, ou ajoutez
le projet frontend avant d'exécuter un `docker compose up` complet.

## Préparation de la production

La configuration Compose actuelle est conçue pour le développement : elle
monte le code en volume et lance `python manage.py runserver`. Ne l'exposez
pas directement sur Internet.

Avant un déploiement public, prévoyez au minimum :

1. une configuration `config.settings.prod` avec une `DJANGO_SECRET_KEY`
   aléatoire de plus de 32 caractères et `DJANGO_ALLOWED_HOSTS` renseigné ;
2. des mots de passe PostgreSQL forts, stockés dans un gestionnaire de secrets ;
3. Redis non exposé au réseau public ;
4. Gunicorn comme serveur WSGI et un reverse proxy TLS (Nginx, Caddy ou un
   load balancer) ;
5. des volumes persistants, des sauvegardes PostgreSQL testées et une politique
   de restauration ;
6. `python manage.py migrate` exécuté à chaque livraison avant le démarrage des
   nouvelles instances ;
7. `python manage.py check --deploy` et `python -m pytest` dans la pipeline CI ;
8. l'alignement du proxy : l'API réelle est servie sous `/v1/`. Le fichier Nginx
   actuel route `/api/`, il doit être adapté avant mise en production.

Après déploiement, vérifiez au minimum :

```bash
curl -i http://votre-domaine.example/v1/schema/
curl -i http://votre-domaine.example/v1/docs/
```

## Dépannage

| Symptôme | Vérification / solution |
| --- | --- |
| `docker: command not found` | Installez Docker Desktop puis rouvrez le terminal. |
| Erreur de connexion PostgreSQL | Vérifiez `POSTGRES_*` dans les deux fichiers `.env`, puis `docker compose ... ps`. |
| Le port 5432 est déjà occupé | Conservez `POSTGRES_PORT=5433` dans `infra/.env` et `backend/.env` pour un lancement hors Docker. |
| Django ne joint pas PostgreSQL dans Docker | Utilisez `POSTGRES_HOST=postgres` et `POSTGRES_PORT=5432` dans `backend/.env`. |
| Django ne joint pas Redis dans Docker | Utilisez `REDIS_URL=redis://redis:6379/1` dans `backend/.env`. |
| Échec après modification de `AUTH_USER_MODEL` | Recréez seulement la base de développement avec `docker compose ... down -v`, puis relancez les migrations. |
