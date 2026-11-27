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
# Origine affichée dans Swagger ; ne pas ajouter /v1, déjà présent dans les chemins.
API_PUBLIC_URL=https://alimma.onrender.com

# Le développement garde les fichiers en local. En production Render, utilisez
# un bucket Cloudflare R2 ou AWS S3 afin de survivre aux redéploiements.
MEDIA_BACKEND=local
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

## Durcissement API et observabilité

En production Render, configurez les variables suivantes dans le service
backend. `NUM_PROXIES=1` autorise l'application à utiliser l'adresse réelle
transmise par le proxy Render dans `X-Forwarded-For`; ne définissez jamais
cette valeur si l'application est exposée directement à Internet.

```dotenv
NUM_PROXIES=1
THROTTLE_INSCRIPTION_RATE=5/hour
THROTTLE_LOGIN_RATE=10/minute
THROTTLE_OTP_RATE=3/hour
THROTTLE_PUBLICATION_RATE=20/day
THROTTLE_PUBLIC_RATE=120/minute
THROTTLE_ANON_RATE=120/minute
THROTTLE_USER_RATE=1000/day
LOG_LEVEL=INFO
DJANGO_ENV=production
SENTRY_DSN=https://cle-publique@o0.ingest.sentry.io/projet
SENTRY_TRACES_SAMPLE_RATE=0.05
```

Une valeur vide de `SENTRY_DSN` désactive complètement Sentry. Les journaux
sont produits au format JSON sur stdout et comprennent `request_id`; le client
peut fournir `X-Request-ID` (128 caractères maximum) pour corréler une action,
sinon l'API en génère un et le retourne dans l'en-tête de réponse. Les limites
peuvent être adaptées à la charge sans redéploiement du code; une réponse 429
utilise toujours `{ "code": "RATE_LIMITED", "message": "..." }`.

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

# Créer le premier administrateur ALIMMA (mot de passe demandé de façon sûre)
docker compose --env-file infra/.env -f infra/docker-compose.yml \
  exec backend python manage.py creer_administrateur \
  --telephone +237699000001 --nom "Administrateur ALIMMA"
```

L'administration Django est disponible sur `http://127.0.0.1:8000/admin/`
après création d'un administrateur.

## Créer le premier administrateur

Le rôle métier `administrateur` est le seul niveau d'administration : il donne
automatiquement accès à `/admin/` et aux routes `/v1/admin/*`. La commande
`creer_administrateur` normalise un téléphone camerounais local (`699000001`
devient `+237699000001`), demande le mot de passe de manière interactive et
conserve une trace dans `journal_moderation`.

N'utilisez pas `createsuperuser` : cette commande Django ne normalise pas le
téléphone et peut créer un compte incapable de se connecter avec l'API ALIMMA.
Ne passez jamais un mot de passe dans la ligne de commande. La variable
`ALIMMA_ADMIN_PASSWORD` est réservée à une automatisation ponctuelle en CI ou
dans un script sécurisé ; ne l'ajoutez ni à un fichier `.env`, ni à l'historique
du shell.

### Local avec Docker

Depuis la racine du dépôt, simulez d'abord l'opération, puis créez le compte :

```powershell
docker compose --env-file infra/.env -f infra/docker-compose.yml exec backend `
  python manage.py creer_administrateur --telephone 699000001 `
  --nom "Administrateur ALIMMA" --dry-run

docker compose --env-file infra/.env -f infra/docker-compose.yml exec backend `
  python manage.py creer_administrateur --telephone 699000001 `
  --nom "Administrateur ALIMMA"
```

Pour promouvoir avec confirmation un compte existant, ajoutez `--promouvoir`.
Pour demander un nouveau mot de passe, ajoutez `--reinitialiser-mot-de-passe`.
La sortie masque systématiquement le téléphone et n'affiche jamais le mot de
passe ni son hash.

### Production Neon depuis un poste local

Le plan Render gratuit ne propose pas d'onglet **Shell**. Exécutez donc la
commande depuis votre PC, dans `backend/`, avec le code correspondant exactement
à la version déployée. Ne lancez pas `migrate` depuis le poste local.

1. Depuis Neon, copiez l'URL de connexion dans une variable temporaire, puis
   faites une sauvegarde avant toute opération :

   ```powershell
   $env:DATABASE_URL = "postgresql://..." # URL Neon, non versionnée
   $date = Get-Date -Format yyyy-MM-dd-HHmm
   pg_dump --format=custom --file="alimma-$date.dump" $env:DATABASE_URL
   ```

2. Définissez seulement dans ce terminal les paramètres Neon nécessaires à
   Django. Remplacez chaque valeur par celles de **Connection Details** Neon :

   ```powershell
   $env:POSTGRES_DB = "nom_base_neon"
   $env:POSTGRES_USER = "utilisateur_neon"
   $env:POSTGRES_PASSWORD = "mot_de_passe_neon"
   $env:POSTGRES_HOST = "hote-neon"
   $env:POSTGRES_PORT = "5432"
   $env:POSTGRES_SSLMODE = "require"
   $env:DJANGO_SETTINGS_MODULE = "config.settings.dev"
   ```

3. Vérifiez que le code déployé correspond à la base, sans appliquer de
   migration, puis simulez la création :

   ```powershell
   py manage.py showmigrations --plan
   py manage.py creer_administrateur --telephone 699000001 `
     --nom "Administrateur ALIMMA" --dry-run
   ```

4. Si le plan ne montre aucune migration non appliquée et que la simulation est
   correcte, relancez sans `--dry-run`. Le terminal demande le mot de passe deux
   fois sans l'afficher :

   ```powershell
   py manage.py creer_administrateur --telephone 699000001 `
     --nom "Administrateur ALIMMA"
   ```

5. Fermez le terminal après l'opération, ou supprimez toutes les variables :

   ```powershell
   Remove-Item Env:DATABASE_URL, Env:POSTGRES_DB, Env:POSTGRES_USER, `
     Env:POSTGRES_PASSWORD, Env:POSTGRES_HOST, Env:POSTGRES_PORT, `
     Env:POSTGRES_SSLMODE, Env:DJANGO_SETTINGS_MODULE
   ```

Sous bash, l'équivalent temporaire est :

```bash
export POSTGRES_DB='nom_base_neon' POSTGRES_USER='utilisateur_neon'
export POSTGRES_PASSWORD='mot_de_passe_neon' POSTGRES_HOST='hote-neon'
export POSTGRES_PORT=5432 POSTGRES_SSLMODE=require
python manage.py showmigrations --plan
python manage.py creer_administrateur --telephone 699000001 --nom 'Administrateur ALIMMA' --dry-run
python manage.py creer_administrateur --telephone 699000001 --nom 'Administrateur ALIMMA'
unset POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD POSTGRES_HOST POSTGRES_PORT POSTGRES_SSLMODE
```

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

## Stockage persistant des images (Cloudflare R2 ou AWS S3)

Le disque d'un service Render est éphémère. En production, configurez un
bucket S3 compatible et utilisez `MEDIA_BACKEND=s3`. Pour Cloudflare R2,
créez un jeton avec les droits de lecture/écriture sur le bucket, puis ajoutez
ces variables dans Render :

```dotenv
MEDIA_BACKEND=s3
AWS_STORAGE_BUCKET_NAME=alimma-medias
AWS_S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
# Domaine public R2/Cloudflare CDN, sans https:// ni slash final.
AWS_S3_CUSTOM_DOMAIN=media.exemple.com
AWS_QUERYSTRING_AUTH=False
```

`AWS_S3_CUSTOM_DOMAIN` est facultatif : sans lui, l'URL du bucket est utilisée.
Les fichiers sont convertis en WebP, stockés sous des UUID non devinables dans
`annonces/<id>/` ou `profils/<id>/`.

### Migration des médias existants

Après avoir configuré le backend S3 et déployé le code, copiez les fichiers
locaux encore accessibles vers le bucket. Vérifiez d'abord l'opération :

```bash
python manage.py migrer_medias --source-root /chemin/vers/media --dry-run
```

Puis exécutez-la sans `--dry-run` :

```bash
python manage.py migrer_medias --source-root /chemin/vers/media
```

La commande ne traite que les URL locales `/media/` et devient idempotente dès
que les URL de base ont été remplacées par celles du stockage objet.
Utilisez `--source-media-url` si vos anciennes URL locales n'emploient pas ce
préfixe.

## Worker RQ et notifications

Les SMS et e-mails transactionnels sont traités hors requête HTTP par RQ. En
local, Compose démarre trois processus : `backend`, `worker` (file `default`)
et `scheduler`. Le scheduler enregistre le traitement idempotent des échéances
de commande toutes les cinq minutes.

```bash
docker compose --env-file infra/.env -f infra/docker-compose.yml up -d --build
docker compose --env-file infra/.env -f infra/docker-compose.yml logs -f worker
```

Par défaut, `SMS_PROVIDER=console` écrit un événement de simulation dans les
logs du worker : aucun SMS n'est facturé. Pour un agrégateur local, configurez
les secrets uniquement dans Render ou dans `backend/.env` non versionné :

```dotenv
RQ_REDIS_URL=redis://.../2
RQ_ASYNC=true
SMS_PROVIDER=http
SMS_API_URL=https://fournisseur.exemple/api/messages
SMS_API_KEY=secret_fourni_par_l_agregateur
SMS_SENDER=ALIMMA
SMS_COST_FCFA=25
DEFAULT_FROM_EMAIL=no-reply@votre-domaine.cm
```

Ne placez jamais `SMS_API_KEY`, les numéros destinataires ou le texte complet
des messages dans les logs. Chaque tentative est tracée en base dans
`notifications`, avec son fournisseur, son coût et son statut.

### Render

Créez un **Background Worker** Render utilisant le même dépôt, environnement
et `REDIS_URL` que le backend. Sa commande de démarrage est :

```bash
python manage.py rqworker default
```

Créez un second Background Worker pour le scheduler :

```bash
python manage.py planifier_echeances && python manage.py rqscheduler
```

Les deux services doivent recevoir les mêmes variables `POSTGRES_*`,
`REDIS_URL`/`RQ_REDIS_URL`, `DJANGO_SETTINGS_MODULE=config.settings.prod` et
les secrets SMS/e-mail nécessaires.

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

## Rollback

Un déploiement automatique ne démarre qu'après une CI GitHub Actions réussie
sur `main`. Si une régression atteint malgré tout la production, commencez par
vérifier l'état de la base : un rollback de code ne restaure jamais les données
ni le schéma PostgreSQL.

### Rétablir une version applicative Render

1. Ouvrez le service backend dans Render, puis **Deploys**.
2. Sélectionnez le dernier déploiement réussi et cliquez sur **Rollback**.
3. Vérifiez `/v1/schema/`, `/v1/docs/` et le parcours concerné.

Render réutilise l'artefact du déploiement cible ; son rollback depuis le
tableau de bord désactive aussi l'auto-déploiement. Ne le réactivez qu'après
avoir corrigé la cause. Si le déploiement voulu n'est plus dans l'historique,
utilisez **Manual Deploy** puis **Deploy a specific commit** avec le SHA Git
connu comme stable.

Pour le frontend Vercel, ouvrez le déploiement stable dans le tableau de bord
et utilisez **Promote to Production**, ou redéployez le commit Git stable.

### Restaurer Neon avec prudence

Avant toute restauration, créez une sauvegarde `pg_dump` de l'état courant et
mettez Render en maintenance ou désactivez ses déploiements automatiques.
Dans Neon, créez d'abord une branche depuis le point antérieur à l'incident
(branche ou point dans le temps/PITR), puis contrôlez son schéma et ses données.
Pointez temporairement un environnement de vérification vers cette branche.
Seulement après validation, basculez les variables `POSTGRES_*` de Render vers
l'endpoint de la branche restaurée et redéployez le backend.

Cette séquence évite d'écraser des données récentes par erreur et permet de
vérifier qu'une ancienne version du code reste compatible avec le schéma après
migration.

## Dépannage

| Symptôme | Vérification / solution |
| --- | --- |
| `docker: command not found` | Installez Docker Desktop puis rouvrez le terminal. |
| Erreur de connexion PostgreSQL locale | Vérifiez `POSTGRES_*` dans `infra/.env`, puis `docker compose ... ps`. |
| Le port 5432 est déjà occupé | Conservez `POSTGRES_PORT=5433` dans `infra/.env` et `backend/.env` pour un lancement hors Docker. |
| Django ne joint pas PostgreSQL dans Docker | Utilisez `POSTGRES_HOST=postgres` et `POSTGRES_PORT=5432` dans `backend/.env`. |
| Django ne joint pas Redis dans Docker | Utilisez `REDIS_URL=redis://redis:6379/1` dans `backend/.env`. |
| Échec après modification de `AUTH_USER_MODEL` | Recréez seulement la base de développement avec `docker compose ... down -v`, puis relancez les migrations. |
