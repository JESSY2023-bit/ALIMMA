#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)

docker compose -f "$ROOT_DIR/infra/docker-compose.yml" up -d postgres
echo "PostgreSQL est prêt. Exécutez 'python manage.py migrate' depuis backend/."
