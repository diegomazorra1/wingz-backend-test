COMPOSE_FILE := docker-compose.local.yml
DJANGO_SERVICE := django

.PHONY: help build up down prune logs manage migrate createsuperuser test

help:
	@echo "Available commands:"
	@echo "  make build            Build local Docker images"
	@echo "  make up               Start local containers"
	@echo "  make down             Stop local containers"
	@echo "  make prune            Stop containers and remove volumes"
	@echo "  make logs             Follow Django logs"
	@echo "  make manage CMD='...' Run a Django management command"
	@echo "  make migrate          Run database migrations"
	@echo "  make createsuperuser  Create a Django superuser"
	@echo "  make test             Run tests"

build:
	docker compose -f $(COMPOSE_FILE) build

up:
	docker compose -f $(COMPOSE_FILE) up -d --remove-orphans

down:
	docker compose -f $(COMPOSE_FILE) down

prune:
	docker compose -f $(COMPOSE_FILE) down -v

logs:
	docker compose -f $(COMPOSE_FILE) logs -f $(DJANGO_SERVICE)

manage:
	docker compose -f $(COMPOSE_FILE) run --rm $(DJANGO_SERVICE) python ./manage.py $(CMD)

migrate:
	docker compose -f $(COMPOSE_FILE) run --rm $(DJANGO_SERVICE) python ./manage.py migrate

createsuperuser:
	docker compose -f $(COMPOSE_FILE) run --rm $(DJANGO_SERVICE) python ./manage.py createsuperuser

test:
	docker compose -f $(COMPOSE_FILE) run --rm $(DJANGO_SERVICE) pytest
