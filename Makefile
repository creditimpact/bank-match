.PHONY: up down migrate ingest
up:
	docker compose -f infra/compose.yaml up -d
down:
	docker compose -f infra/compose.yaml down -v
migrate:
	psql "postgres://bankmatch:bankmatch@localhost:5432/bankmatch" -f db/migrations/0001_init.sql
ingest:
	python etl/ingest_csv.py --dsn "postgres://bankmatch:bankmatch@localhost:5432/bankmatch" --csv data/templates/products_template.csv
