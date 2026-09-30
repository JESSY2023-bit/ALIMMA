# Configuration CI/CD

ALIMMA utilise GitHub Actions pour la vérification continue, Render pour le
déploiement du backend Django et Vercel pour le déploiement du frontend React.
Les URL de webhooks sont des secrets : ne les ajoutez jamais dans un fichier
versionné ou dans le code source.

## 1. Créer le webhook Render

1. Connectez-vous au tableau de bord [Render](https://dashboard.render.com/).
2. Ouvrez le service Web qui héberge le backend ALIMMA.
3. Ouvrez **Settings**.
4. Dans la section **Deploy Hook**, créez ou copiez l’URL du hook de
   déploiement.
5. Conservez cette URL : elle sera enregistrée dans GitHub sous le nom
   `RENDER_DEPLOY_HOOK_URL`.

## 2. Créer le webhook Vercel

1. Connectez-vous au tableau de bord [Vercel](https://vercel.com/dashboard).
2. Ouvrez le projet frontend ALIMMA.
3. Ouvrez **Project Settings**, puis **Git**.
4. Dans **Deploy Hooks**, créez un hook associé à la branche `main`, ou copiez
   son URL s’il existe déjà.
5. Conservez cette URL : elle sera enregistrée dans GitHub sous le nom
   `VERCEL_DEPLOY_HOOK_URL`.

## 3. Enregistrer les secrets dans GitHub

1. Ouvrez le dépôt ALIMMA sur GitHub.
2. Accédez à **Settings** > **Secrets and variables** > **Actions**.
3. Cliquez sur **New repository secret**.
4. Créez le secret `RENDER_DEPLOY_HOOK_URL` et collez l’URL Render.
5. Créez le secret `VERCEL_DEPLOY_HOOK_URL` et collez l’URL Vercel.

## Fonctionnement des workflows

- `ci-backend.yml` se lance sur les push et pull requests qui modifient
  `backend/`. Il lance Flake8 et les tests Django avec un seuil de couverture
  de 70 %.
- `ci-frontend.yml` se lance sur les push et pull requests qui modifient
  `frontend/`. Il installe les dépendances, lance ESLint, Vitest et le build
  Vite.
- `deploy.yml` ne se lance que pour un push sur `main`. Il déclenche en
  parallèle les hooks de déploiement Render et Vercel. Il ne se déclenche pas
  sur la branche `develop`.

## Prérequis frontend

Le workflow frontend exécute `npm run test`. Le projet doit donc définir ce
script et installer Vitest avant la première exécution de CI. Par exemple :

```json
{
  "scripts": {
    "test": "vitest run"
  }
}
```

Installez ensuite Vitest dans le dossier `frontend` avec `npm install -D vitest`.
