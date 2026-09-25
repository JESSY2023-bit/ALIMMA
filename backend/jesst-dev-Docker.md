docker compose up -d          # démarrer en arrière-plan
docker compose down           # tout arrêter
docker compose logs -f backend  # voir les logs d'un service en continu
docker compose exec backend python manage.py migrate   # exécuter une commande dans le conteneur
docker compose build --no-cache backend  # reconstruire l'image si tu changes le Dockerfile ou requirements