#!/usr/bin/env python3
"""Convert research JSON output to normalized CSV.

Usage:
    python etl/convert_json_to_csv.py input.json output.csv

The input JSON is expected to be a list of dictionaries describing loan
products gathered from research prompts. The script normalizes this data to the
extended CSV schema required by the ingestion pipeline. Missing fields are
filled with "Unknown/Not disclosed" and the CSV columns are written in a fixed
order.
"""
from __future__ import annotations

import argparse
import json
import csv
from typing import Any, Dict, List

# Fixed schema/column order
COLUMNS: List[str] = [
    "bank_legal_name",
    "fdic_certificate",
    "website",
    "lending_footprint",
    "excluded_states",
    "product_type",
    "purpose_allowed",
    "min_loan_amount_usd",
    "max_loan_amount_usd",
    "rate_structure",
    "interest_rate_min",
    "interest_rate_max",
    "rate_floor_or_spread",
    "introductory_rate",
    "loan_term_months_min",
    "loan_term_months_max",
    "amortization_type",
    "min_years_in_business",
    "min_annual_revenue_usd",
    "min_personal_credit_score",
    "min_dscr",
    "other_financial_ratios",
    "collateral_required",
    "eligible_collateral_types",
    "max_ltv_real_estate",
    "max_ltv_equipment",
    "max_ltv_receivables",
    "max_ltv_inventory",
    "personal_guarantee",
    "guarantee_type",
    "origination_fee",
    "annual_fee",
    "other_fees",
    "prepayment_penalty",
    "decision_timeline_prequal_days",
    "decision_timeline_underwriting_days",
    "average_time_to_fund_days",
    "industry_restrictions",
    "special_conditions",
    "source_url",
    "last_verified",
]

FALLBACK_VALUE = "Unknown/Not disclosed"


def load_json(path: str) -> List[Dict[str, Any]]:
    """Load JSON from *path* and ensure it is a list of dicts."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:  # pragma: no cover - simple error path
        raise SystemExit(f"Failed to read JSON from {path}: {exc}")

    if isinstance(data, dict):
        # Occasionally the JSON might be wrapped; try to use values if possible
        # but fall back to treating as a single record
        if len(data) == 1 and isinstance(next(iter(data.values())), list):
            data = next(iter(data.values()))
        else:
            data = [data]

    if not isinstance(data, list):
        raise SystemExit("Input JSON must be a list of objects")

    # Ensure each element is a dict
    cleaned = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise SystemExit(f"Element at index {idx} is not an object")
        cleaned.append(item)
    return cleaned


def normalize_record(rec: Dict[str, Any]) -> Dict[str, str]:
    """Return a normalized record with all COLUMNS present."""
    normalized: Dict[str, str] = {}
    for col in COLUMNS:
        val = rec.get(col)
        if val is None or val == "":
            normalized[col] = FALLBACK_VALUE
        else:
            # Convert lists/dicts to JSON strings to avoid CSV issues
            if isinstance(val, (list, dict)):
                normalized[col] = json.dumps(val)
            else:
                normalized[col] = str(val)
    return normalized


def convert_json_to_csv(input_path: str, output_path: str) -> int:
    """Read *input_path*, write CSV to *output_path*, and return row count."""
    records = load_json(input_path)
    rows = [normalize_record(rec) for rec in records]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


def main(argv: List[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Convert research JSON to CSV")
    ap.add_argument("input", help="Path to input JSON file")
    ap.add_argument("output", help="Path to output CSV file")
    args = ap.parse_args(argv)

    count = convert_json_to_csv(args.input, args.output)
    print(f"Converted {count} products into {args.output}")


if __name__ == "__main__":
    main()
