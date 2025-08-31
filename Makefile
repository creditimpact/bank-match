.PHONY: up down logs api fmt

up:
\tdocker compose -f infra/compose.yaml up -d --build

down:
\tdocker compose -f infra/compose.yaml down

logs:
\tdocker compose -f infra/compose.yaml logs -f

api:
\tcurl http://localhost:8000/health || powershell -Command "Invoke-WebRequest -UseBasicParsing http://localhost:8000/health"

fmt:
\t@echo "placeholder for formatters"
