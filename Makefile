COMPOSE = docker compose -f infra/docker-compose.yml

.PHONY: dev down logs migrate shell test build

dev:
	$(COMPOSE) up

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

migrate:
	$(COMPOSE) exec backend python manage.py migrate

shell:
	$(COMPOSE) exec backend python manage.py shell

test:
	$(COMPOSE) exec backend pytest --cov=apps

build:
	$(COMPOSE) build --no-cache
