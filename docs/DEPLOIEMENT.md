# Installation et déploiement d'ALIMMA

Ce document décrit l'installation locale du backend ALIMMA et le démarrage
avec Docker Compose. L'API est une application Django 5/DRF utilisant
PostgreSQL 16 et Redis.

> `docs/schema.sql` est un document de conception. Ne l'exécutez pas : les
> tables et extensions sont créées exclusivement par les migrations Django.

## Prérequis

- Git ;
- Docker Desktop avec Docker Compose v2 ;
- Python 3.12 et `pip` pour une exécution hors Docker ;
- PostgreSQL n'est pas requis localement si Docker est utilisé ;
- Node.js est requis pour exécuter le frontend React hors Docker.

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
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=alimma
POSTGRES_USER=alimma
POSTGRES_PASSWORD=choisissez-un-mot-de-passe-fort
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_SSLMODE=prefer

REDIS_URL=redis://redis:6379/1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
FEATURE_2FA_ENABLED=false
```

Les valeurs `POSTGRES_DB`, `POSTGRES_USER` et `POSTGRES_PASSWORD` de
`backend/.env` doivent correspondre à celles de `infra/.env`. Le port hôte
par défaut est `5433` afin d'éviter un conflit avec un PostgreSQL local ; il
reste `5432` à l'intérieur du réseau Docker. Compose fournit toutefois
toujours `POSTGRES_HOST=postgres`, `POSTGRES_PORT=5432` et
`POSTGRES_SSLMODE=prefer` au conteneur backend.

## Base de production Neon

La base de production est hébergée par **Neon**, en région `us-east-2`.
Dans le tableau de bord Neon, ouvrez votre projet, sélectionnez la branche de
production puis relevez les valeurs affichées dans **Connection Details**.
Dans les variables d'environnement du service backend Render, créez :

```dotenv
POSTGRES_DB=nom_de_base_neon
POSTGRES_USER=utilisateur_neon
POSTGRES_PASSWORD=mot_de_passe_neon
POSTGRES_HOST=hote-neon
POSTGRES_PORT=5432
POSTGRES_SSLMODE=require
```

Copiez les valeurs réelles depuis Neon, sans les commiter. Le backend lit ces
variables `POSTGRES_*`; `POSTGRES_SSLMODE=require` active TLS pour Neon.
Sur Render, conservez **ALLOWED_HOSTS** et supprimez **DJANGO_ALLOWED_HOSTS** :
en production, seule `ALLOWED_HOSTS` est lue.

Pour la base Docker locale, `POSTGRES_SSLMODE=prefer` reste le défaut afin de
fonctionner avec ou sans TLS.

### Sauvegarde Neon

Installez les outils clients PostgreSQL en version **18 ou supérieure**, puis
vérifiez la version :

```bash
pg_dump --version
```

Avec l'URL de connexion complète copiée depuis Neon, créez une sauvegarde au
format PostgreSQL personnalisé :

Sous macOS/Linux :

```bash
pg_dump --format=custom --file="alimma-$(date +%F).dump" "$DATABASE_URL"
```

Sous PowerShell :

```powershell
$backupDate = Get-Date -Format yyyy-MM-dd
pg_dump --format=custom --file="alimma-$backupDate.dump" $env:DATABASE_URL
```

Conservez le fichier de sauvegarde dans un stockage chiffré distinct de Neon.
Pour restaurer dans une base cible vide :

```bash
pg_restore --clean --if-exists --no-owner --dbname="$DATABASE_URL" alimma-AAAA-MM-JJ.dump
```

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

Lancez PostgreSQL et Redis, puis configurez `backend/.env` avec :

```dotenv
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5433
POSTGRES_SSLMODE=prefer
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

Le frontend React est disponible dans `frontend/`. Créez sa configuration
locale puis lancez l'ensemble des services :

```bash
cp frontend/.env.example frontend/.env
docker compose --env-file infra/.env -f infra/docker-compose.yml up -d --build
```

Le client est alors disponible sur `http://127.0.0.1:5173/`. En Docker,
`VITE_API_URL=/v1` est relayé par le proxy Vite vers le service `backend` : le
navigateur n'appelle donc pas directement le port 8000.

## Lien frontend Vercel / backend Render

Une URL `localhost` ne fonctionne que sur votre ordinateur. Dans Vercel,
ouvrez **Project Settings** > **Environment Variables** et créez la variable
suivante pour les environnements **Production** et **Preview** :

```dotenv
VITE_API_URL=https://votre-service.onrender.com/v1
```

Remplacez l'exemple par l'URL HTTPS publique exacte de votre Web Service
Render. Après la sauvegarde, redéployez Vercel : les variables `VITE_*` sont
intégrées au build, elles ne sont pas lues dynamiquement par le navigateur.

Dans Render, définissez également `CORS_ALLOWED_ORIGINS` avec les origines
Vercel autorisées, sans chemin `/v1`, par exemple :

```dotenv
CORS_ALLOWED_ORIGINS=https://alimma.vercel.app,https://alimma-git-develop-votre-compte.vercel.app
```

## Préparation de la production

La configuration Compose actuelle est conçue pour le développement : elle
monte le code en volume et lance `python manage.py runserver`. Ne l'exposez
pas directement sur Internet.

Avant un déploiement public, prévoyez au minimum :

1. une configuration `config.settings.prod` avec une `DJANGO_SECRET_KEY`
   aléatoire de plus de 32 caractères et `ALLOWED_HOSTS` renseigné ;
2. les variables `POSTGRES_*` Neon, stockées dans les secrets Render, avec
   `POSTGRES_SSLMODE=require` ;
3. Redis non exposé au réseau public ;
4. Gunicorn comme serveur WSGI, fourni par le service backend Render ;
5. des volumes persistants, des sauvegardes PostgreSQL testées et une politique
   de restauration ;
6. `python manage.py migrate` exécuté à chaque livraison avant le démarrage des
   nouvelles instances ;
7. `python manage.py check --deploy` et `python -m pytest` dans la pipeline CI ;
8. déployez le backend sur Render et le frontend sur Vercel. Ces plateformes
   gèrent le HTTPS et le routage public ; aucun Nginx autogéré ni Compose de
   production n'est nécessaire.

Après déploiement, vérifiez au minimum :

```bash
curl -i http://votre-domaine.example/v1/schema/
curl -i http://votre-domaine.example/v1/docs/
```

## Dépannage

| Symptôme | Vérification / solution |
| --- | --- |
| `docker: command not found` | Installez Docker Desktop puis rouvrez le terminal. |
| Erreur de connexion PostgreSQL locale | Vérifiez `POSTGRES_*` dans `infra/.env`, puis `docker compose ... ps`. |
| Le port 5432 est déjà occupé | Conservez `POSTGRES_PORT=5433` dans `infra/.env` et `backend/.env` pour un lancement hors Docker. |
| Django ne joint pas PostgreSQL dans Docker | Utilisez `POSTGRES_HOST=postgres` et `POSTGRES_PORT=5432` dans `backend/.env`. |
| Django ne joint pas Redis dans Docker | Utilisez `REDIS_URL=redis://redis:6379/1` dans `backend/.env`. |
| Échec après modification de `AUTH_USER_MODEL` | Recréez seulement la base de développement avec `docker compose ... down -v`, puis relancez les migrations. |
