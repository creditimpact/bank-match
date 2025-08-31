# bank-match

פלטפורמה להתאמת לקוחות למוצרי הלוואות בנקאיים בארה"ב.

## Quickstart (Docker-only)

**Prereqs:** Install Docker Desktop (Mac/Win) or Docker Engine + Compose (Linux).

```bash
# 1) Optional environment check
./scripts/dev/check_env.sh

# 2) Start Postgres in Docker
make up

# 3) Apply DB migrations (runs psql inside the db container)
make migrate

# 4) Load sample data (runs Python inside a container; no local pip needed)
make ingest

# 5) (Optional) open a psql shell in the db container
make psql

# 6) Tear down
make down
```

**If you prefer local Python:** create a venv and `pip install -r app/requirements.txt` then run `etl/ingest_csv.py` with a local DSN.

Troubleshooting:

* `docker: command not found` → Install Docker Desktop and restart your shell.
* `psql: not found` → Not needed locally anymore; we run it inside the container.
* Ingest fails with pandas/psycopg → rerun `make ingest` (it reinstalls inside the container).
