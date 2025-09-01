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

### Batch import (JSON → CSV → DB)

**Option A (Make):**
```bash
make batch IN=data/batch_001.json OUT=data/batch_001.csv
```

**Option B (Windows PowerShell):**

```powershell
\.\scripts\dev\batch.ps1 -InJson data\batch_001.json -OutCsv data\batch_001.csv
```

The command will:

- convert JSON → CSV with the extended 42-column schema,
- ingest into Postgres in Docker,
- print bank/product counts for verification.

### Quick demo (matching)

```bash
make up
make migrate
make migrate2
# load sample criteria and customers
docker compose -f infra/compose.yaml exec -T db psql -U bankmatch -d bankmatch -f data/sample_criteria.sql
docker compose -f infra/compose.yaml exec -T db psql -U bankmatch -d bankmatch -f data/sample_customer.sql
make match CID=1
```

The `match` command filters products by eligibility, underwriting, and deal
constraints, returning the best-ranked matches for the given customer profile.
