param(
  [Parameter(Mandatory=$true)] [string]$InJson,
  [Parameter(Mandatory=$true)] [string]$OutCsv
)

$dc = "docker compose -f infra/compose.yaml"

# Convert
iex "$dc run --rm etl bash -lc 'python etl/convert_json_to_csv.py $InJson $OutCsv'"
if ($LASTEXITCODE -ne 0) { Write-Error "Conversion failed"; exit 1 }

# Load
iex "$dc up -d db"
iex "$dc exec -T db psql -U bankmatch -d bankmatch -f /migrations/0001_init.sql"
iex "$dc run --rm etl bash -lc 'python etl/ingest_csv.py --dsn postgres://bankmatch:bankmatch@db:5432/bankmatch --csv $OutCsv'"
if ($LASTEXITCODE -ne 0) { Write-Error "Ingest failed"; exit 1 }

# Verify
iex "$dc exec -T db psql -U bankmatch -d bankmatch -c 'SELECT count(*) AS banks FROM banks; SELECT count(*) AS products FROM products;'"
