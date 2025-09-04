# Underwriting Matching Engine GAP Report

## 1. Repo Inventory
- **app/** – Python requirements for ETL scripts.
- **apps/api/** – FastAPI service with health and root endpoints.
- **data/** – Sample data and templates used in demos.
- **db/** – SQL migrations defining bank/product and matching schemas.
- **etl/** – CSV conversion, ingestion, and rudimentary matching script with tests.
- **infra/** – Docker compose file for Postgres and ETL container.
- **scripts/** – Developer utility scripts.
- *(New)* **src/** – placeholder for parsers, features, scoring modules.

## 2. Current vs Target Matrix
| Component | Exists? | Quality | Gaps | Immediate Fix |
|-----------|--------|--------|------|---------------|
| Ingestion (PDF/Plaid) | Partial | Low | Only CSV→DB via scripts; no API integrations | Implement API connectors, robust error handling |
| OCR/Parsing | No | – | No PDF/tax parsers | Add bank statement/tax parsers |
| Normalization & Validation | Partial | Med | CSV validation only; no schema enforcement | Introduce Pydantic models & JSON schema |
| Feature Engineering | No | – | KPIs not computed | Add financial feature module |
| Lender Credit Box | Partial | Low | SQL tables but no config abstraction | YAML/JSON schema for lender criteria |
| Scoring & Rules Engine | Partial | Low | Simple heuristics in `match_customer.py`; no reusable engine | Create modular rules engine |
| Matching & Ranking | Yes | Med | Heuristic scoring only | Integrate with rules engine & weights |
| Explainability | No | – | No rationale tracking | Add reasons in rules engine |
| Export/Reporting | No | – | No underwriting package generation | Build reporting module |
| API, Auth, Audit Logs | Minimal | Low | Bare health endpoint; no auth/logging | Expand API with auth and audit trails |
| Data Model/DB Schemas | Yes | Med | Lacks relationships for lenders, criteria versioning | Extend schema for credit boxes |
| Tests | Yes | Low | Only ETL scripts covered | Add unit tests for new modules |
| Security/Compliance | No | – | No PII handling, secrets mgmt | Implement encryption, access controls |

## 3. Data Flow
1. **Document/API upload** – client submits bank or tax docs (not yet implemented).
2. **Parsing/OCR** – extract transactions and financials from PDFs.
3. **Normalization & Validation** – map to canonical schema, validate types/units.
4. **Feature Engineering** – compute KPIs such as revenue, DSCR, balances.
5. **Rules/Scoring** – evaluate against lender credit boxes, produce scores.
6. **Matching & Ranking** – select best lenders/programs for the client.
7. **Export/Reporting** – generate underwriting summary for brokers/lenders.

## 4. Lender Credit Box (Schema + Samples)
- See `schemas/lender_credit_box.schema.json` for proposed schema.
- Sample lender configs in `configs/lenders.sample.yaml` illustrate SBA and equipment lenders with eligibility criteria.

## 5. KPIs & Ratios (Formulas + Edge Cases)
- **avg_daily_balance** = sum(daily balances) / N; handle empty lists.
- **month_over_month_revenue** = (M_i - M_{i-1}) / M_{i-1}; guard against division by zero.
- **inflows_outflows** = sum deposits vs withdrawals; classify transfers.
- **nsf_count** = count of negative balance days; clarify overlapping fees.
- **dscr** = EBITDA / annual_debt_service; return `None` when debt service is 0.
- **add_backs** = interest + depreciation + amortization + owner_comp adjustments.

## 6. Scoring & Matching (Code/Pseudocode)
- Rules engine evaluates hard filters then soft-score rules:
```python
from src.scoring.rules_engine import Rule, RulesEngine
engine = RulesEngine([
    Rule("personal_fico", ">=", 660, hard=True),
    Rule("dscr", ">=", 1.15, weight=50, hard=False),
    Rule("years_in_business", ">=", 2, weight=50, hard=False)
])
result = engine.evaluate(metrics)
```
- TODO: support weighted scorecard, rationale tracking, config-driven rules.

## 7. Security & Compliance Gaps
- No encryption or secrets management.
- No authentication/authorization around API or data access.
- Missing audit logs, PII redaction, or consent flows.
- Need error logging, data retention policies, and secure storage of documents.

## 8. Testing Plan (with Sample Tests)
- Existing tests cover ETL utilities only.
- New unit tests added for rules engine and financial features.
- Future tests:
  - Parser fixtures with synthetic PDFs.
  - Integration tests for matching against sample credit boxes.
  - Security tests for auth and permission checks.
