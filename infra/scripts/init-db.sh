#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)

docker compose -f "$ROOT_DIR/infra/docker-compose.yml" up -d postgres
docker compose -f "$ROOT_DIR/infra/docker-compose.yml" exec postgres \
  psql -U "${POSTGRES_USER:-alimma}" -d "${POSTGRES_DB:-alimma}" \
  -f /dev/stdin < "$ROOT_DIR/docs/schema.sql"
