import csv

def test_schema_min_cols_present():
    with open("data/templates/products_template.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        row = next(reader)
        assert "fdic_certificate" in row and row["fdic_certificate"]
        assert "bank_legal_name" in row and row["bank_legal_name"]
        assert "last_verified" in row and row["last_verified"]
