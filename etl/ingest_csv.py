#!/usr/bin/env python3
import argparse, sys
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dateutil.parser import isoparse

REQUIRED_COLS = [
    "bank_legal_name","fdic_certificate","lending_footprint","product_type",
    "min_loan_amount_usd","max_loan_amount_usd","rate_structure",
    "source_url","last_verified"
]

def validate_df(df: pd.DataFrame):
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    # coerce dates
    try:
        df["last_verified"] = df["last_verified"].apply(lambda x: isoparse(str(x)).date())
    except Exception as e:
        raise ValueError(f"Invalid last_verified date: {e}")
    return df

def upsert_bank(cur, rows):
    # (fdic_certificate, legal_name, website, footprint)
    sql = """
    INSERT INTO banks (fdic_certificate, legal_name, website, lending_footprint)
    VALUES %s
    ON CONFLICT (fdic_certificate) DO UPDATE
    SET legal_name = EXCLUDED.legal_name,
        website = COALESCE(EXCLUDED.website, banks.website),
        lending_footprint = COALESCE(EXCLUDED.lending_footprint, banks.lending_footprint)
    RETURNING id, fdic_certificate
    """
    execute_values(cur, sql, rows, page_size=100)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dsn", required=True)
    ap.add_argument("--csv", required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.csv).fillna("")
    df = validate_df(df)

    conn = psycopg2.connect(args.dsn)
    conn.autocommit = False
    cur = conn.cursor()

    # Upsert banks
    bank_rows = df[["fdic_certificate","bank_legal_name","website","lending_footprint"]].drop_duplicates()
    upsert_bank(cur, [(r.fdic_certificate, r.bank_legal_name, r.website, r.lending_footprint) for r in bank_rows.itertuples()])

    # Map fdic -> bank_id
    cur.execute("SELECT id, fdic_certificate FROM banks")
    id_map = {fdic: bid for bid, fdic in cur.fetchall()}

    # Insert products
    prod_cols = [
        "fdic_certificate","product_type","min_loan_amount_usd","max_loan_amount_usd","rate_structure",
        "min_years_in_business","min_annual_revenue_usd","min_personal_credit_score","min_dscr",
        "max_ltv_real_estate","max_ltv_equipment","max_ltv_receivables","max_ltv_inventory",
        "personal_guarantee","collateral_required","industry_restrictions",
        "decision_timeline_prequal_days","decision_timeline_underwriting_days","last_verified"
    ]
    def to_num(v):
        try:
            return float(v) if str(v).strip() != "" else None
        except:
            return None

    prod_values = []
    for r in df[prod_cols].itertuples(index=False):
        fdic = r[0]
        bank_id = id_map.get(fdic)
        if not bank_id:
            raise RuntimeError(f"Bank not found for FDIC {fdic}")
        vals = [
            bank_id, r[1], to_num(r[2]), to_num(r[3]), r[4],
            to_num(r[5]), to_num(r[6]), to_num(r[7]), to_num(r[8]),
            to_num(r[9]), to_num(r[10]), to_num(r[11]), to_num(r[12]),
            r[13] or "Unknown", r[14] or "Unknown", r[15] or "",
            int(r[16]) if str(r[16]).isdigit() else None,
            int(r[17]) if str(r[17]).isdigit() else None,
            r[18]
        ]
        prod_values.append(vals)

    execute_values(cur, """
    INSERT INTO products (
      bank_id, product_type, min_loan_amount_usd, max_loan_amount_usd, rate_structure,
      min_years_in_business, min_annual_revenue_usd, min_personal_credit_score, min_dscr,
      max_ltv_real_estate, max_ltv_equipment, max_ltv_receivables, max_ltv_inventory,
      personal_guarantee, collateral_required, industry_restrictions,
      decision_timeline_prequal_days, decision_timeline_underwriting_days, last_verified
    ) VALUES %s
    """, prod_values, page_size=100)

    # Insert sources (product-level, same URL per row for now)
    cur.execute("SELECT id FROM products ORDER BY id DESC LIMIT %s", (len(prod_values),))
    inserted_ids = [row[0] for row in cur.fetchall()][::-1]  # naive mapping for demo
    src_values = [(pid, url, None, None, None) for pid, url in zip(inserted_ids, df["source_url"].tolist())]
    execute_values(cur, """
    INSERT INTO sources (product_id, source_url, evidence_type, title, date_accessed)
    VALUES %s
    """, src_values, page_size=100)

    conn.commit()
    print(f"Loaded {len(prod_values)} products from {args.csv}")
    cur.close(); conn.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr); sys.exit(1)
