import csv
import json
import sys
from pathlib import Path

# Ensure repository root is on sys.path for direct module import
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))
from etl.convert_json_to_csv import COLUMNS, FALLBACK_VALUE, convert_json_to_csv


def test_convert_json_to_csv(tmp_path: Path):
    data = [{
        "bank_legal_name": "Example Bank",
        "fdic_certificate": "99999",
        "source_url": "https://example.com/loan",
        "last_verified": "2024-01-01",
        # leave out other fields to trigger fallback
    }]
    inp = tmp_path / "input.json"
    inp.write_text(json.dumps(data), encoding="utf-8")
    outp = tmp_path / "output.csv"

    count = convert_json_to_csv(str(inp), str(outp))
    assert count == 1 and outp.exists()

    with outp.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == COLUMNS
        row = next(reader)
        # Provided fields should be preserved
        assert row["bank_legal_name"] == "Example Bank"
        assert row["fdic_certificate"] == "99999"
        # Missing fields should be replaced with fallback value
        assert row["website"] == FALLBACK_VALUE
        assert row["industry_restrictions"] == FALLBACK_VALUE
