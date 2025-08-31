.PHONY: check up down logs migrate ingest psql help

DC := docker compose -f infra/compose.yaml

help:
	@echo "Targets:"
	@echo "  make check    - verify docker/compose availability"
	@echo "  make up       - start Postgres"
	@echo "  make migrate  - run SQL migrations inside the db container"
	@echo "  make ingest   - run CSV -> Postgres ingestion via ETL container"
	@echo "  make logs     - tail db logs"
	@echo "  make down     - stop and remove containers/volumes"

check:
	@command -v docker >/dev/null 2>&1 || { echo >&2 "❌ Docker not installed. Install Docker Desktop and retry."; exit 1; }
	@docker compose version >/dev/null 2>&1 || { echo >&2 "❌ docker compose not available. Update Docker Desktop."; exit 1; }
	@echo "✅ Docker OK"

up: check
	$(DC) up -d db
	@echo "⏳ Waiting for Postgres to be healthy..."; sleep 3
	$(DC) ps

logs:
	$(DC) logs -f db

migrate:
	# run migration inside the db container using psql from the Postgres image
	$(DC) exec -T db psql -U bankmatch -d bankmatch -f /migrations/0001_init.sql
	@echo "✅ Migrations applied"

ingest:
	# run ETL inside the python container; install deps in-container, then run script
	$(DC) run --rm etl "pip install -r app/requirements.txt && python etl/ingest_csv.py --dsn postgres://bankmatch:bankmatch@db:5432/bankmatch --csv data/templates/products_template.csv"

psql:
	$(DC) exec -it db psql -U bankmatch -d bankmatch

down:
	$(DC) down -v
