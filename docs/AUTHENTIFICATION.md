# Authentification JWT

Cette API utilise une paire de jetons JWT : un access token de courte durée et
un refresh token destiné à obtenir une nouvelle paire lorsque l'access token
expire.

## Flux

1. Créer un compte avec `POST /v1/auth/inscription`.
2. Se connecter avec `POST /v1/auth/login` pour recevoir `access_token` et
   `refresh_token` lorsque la 2FA est désactivée (cas MVP).
3. Envoyer l'access token avec chaque route protégée :
   `Authorization: Bearer <access_token>`.
4. Lorsque l'access token expire, appeler `POST /v1/auth/refresh` avec le
   refresh token. Cette route retourne une **nouvelle paire** et blackliste le
   refresh token consommé.
5. À la déconnexion, appeler `POST /v1/auth/logout` avec l'access token et le
   refresh token : ce dernier est blacklisté et ne peut plus être renouvelé.

Durées de vie : access token **30 minutes**, refresh token **7 jours**.

```bash
# Inscription
curl -X POST http://localhost:8000/v1/auth/inscription \
  -H 'Content-Type: application/json' \
  -d '{"nom":"Alice Ngono","telephone":"+237670000001", "password":"mot-de-passe-solide"}'

# Connexion
curl -X POST http://localhost:8000/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"identifiant":"+237670000001", "password":"mot-de-passe-solide"}'

# Appel protégé
curl http://localhost:8000/v1/utilisateurs/moi \
  -H 'Authorization: Bearer <access_token>'

# Rotation : remplacer les deux jetons stockés par ceux de la réponse
curl -X POST http://localhost:8000/v1/auth/refresh \
  -H 'Content-Type: application/json' \
  -d '{"refresh_token":"<refresh_token>"}'

# Déconnexion
curl -X POST http://localhost:8000/v1/auth/logout \
  -H 'Authorization: Bearer <access_token>' \
  -H 'Content-Type: application/json' \
  -d '{"refresh_token":"<refresh_token>"}'
```

## Réponses 401

Les erreurs suivent toujours le format `{ "code", "message" }`.

| Code | Cas | Action frontend |
| --- | --- | --- |
| `NOT_AUTHENTICATED` | Aucun access token sur une route protégée. | Si un refresh token existe, tenter un refresh ; sinon rediriger vers `/auth/login`. |
| `TOKEN_NOT_VALID` | Access token invalide ou expiré. | Lancer un refresh unique ; si celui-ci échoue, supprimer les jetons et rediriger vers `/auth/login`. |
| `AUTHENTICATION_FAILED` | Identifiants invalides, compte suspendu, refresh expiré, invalide ou blacklisté. | Ne pas réessayer le même refresh ; supprimer les jetons et rediriger vers `/auth/login`. Pour le login, afficher le message générique reçu. |

Les codes ci-dessus sont ceux fournis par `config.exceptions.api_exception_handler` ;
le backend ne distingue pas publiquement un compte suspendu d'identifiants
incorrects, ni un refresh blacklisté d'un refresh invalide.

## Stockage et concurrence

- Conserver l'access token en mémoire (par exemple dans le state Redux).
- Conserver le refresh token dans `localStorage` pour survivre à la fermeture
  de l'application.
- Ne jamais mettre un token dans une URL, dans les logs ou dans un message
  d'erreur affiché à l'utilisateur.
- Au démarrage de l'application, si un refresh token existe, appeler
  `/auth/refresh` avant de considérer l'utilisateur connecté.
- Si plusieurs requêtes reçoivent un `401` simultanément, ne lancer qu'un seul
  refresh ; mettre les autres requêtes en attente de son résultat. En cas
  d'échec, rejeter la file, supprimer les jetons et rediriger vers
  `/auth/login`.

Le MVP utilise le header Bearer. Une migration vers un cookie `httpOnly` est
prévue lorsqu'un domaine personnalisé same-site sera en place ; elle n'est pas
implémentée actuellement.

## CORS

`CORS_ALLOWED_ORIGINS` côté backend doit contenir l'URL exacte du frontend,
par exemple `http://localhost:5173` ou `https://app.example.cm`. Aucun
credential CORS n'est requis tant que l'authentification utilise le header
Bearer plutôt qu'un cookie.
