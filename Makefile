.PHONY: check up down logs migrate ingest psql help convert load verify batch migrate2 match

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

# convert JSON -> CSV
# Usage: make convert IN=data/batch_001.json OUT=data/batch_001.csv
convert:
	@if [ -z "$(IN)" ] || [ -z "$(OUT)" ]; then echo "Usage: make convert IN=... OUT=..."; exit 1; fi
	$(DC) run --rm etl bash -lc "python etl/convert_json_to_csv.py $(IN) $(OUT)"

# load CSV -> Postgres (via Docker)
# Usage: make load CSV=data/batch_001.csv
load:
	@if [ -z "$(CSV)" ]; then echo "Usage: make load CSV=..."; exit 1; fi
	$(DC) up -d db
	$(DC) exec -T db psql -U bankmatch -d bankmatch -f /migrations/0001_init.sql
	$(DC) run --rm etl bash -lc "python etl/ingest_csv.py --dsn postgres://bankmatch:bankmatch@db:5432/bankmatch --csv $(CSV)"

# verify counts after load
verify:
	$(DC) exec -T db psql -U bankmatch -d bankmatch -c "SELECT count(*) AS banks FROM banks; SELECT count(*) AS products FROM products;"

# one-click: JSON -> CSV -> ingest -> verify
# Usage: make batch IN=data/batch_001.json OUT=data/batch_001.csv
batch:
	@if [ -z "$(IN)" ] || [ -z "$(OUT)" ]; then echo "Usage: make batch IN=... OUT=..."; exit 1; fi
	$(MAKE) convert IN=$(IN) OUT=$(OUT)
	$(MAKE) load CSV=$(OUT)
	$(MAKE) verify

# Apply matching schema migration
migrate2:
	$(DC) exec -T db psql -U bankmatch -d bankmatch -f /migrations/0002_match_schema.sql
	@echo "✅ Match schema migration applied"

# Example usage with customer-id:
# make match CID=1
match:
	@if [ -z "$(CID)" ]; then echo "Usage: make match CID=<customer_id>"; exit 1; fi
	$(DC) run --rm etl bash -lc "python etl/match_customer.py --dsn postgres://bankmatch:bankmatch@db:5432/bankmatch --customer-id $(CID) --top 10"
