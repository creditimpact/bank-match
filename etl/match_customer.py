#!/usr/bin/env python3
"""Match customer profiles to bank products based on eligibility, underwriting,
and deal/collateral criteria.

The script can take a ``--customer-id`` referencing ``customer_profiles`` in the
DB or accept inline parameters describing the customer. It performs three
filtering stages and ranks surviving products with a simple score.

Example (Dockerised):
    docker compose -f infra/compose.yaml run --rm etl bash -lc \
      "python etl/match_customer.py --dsn postgres://bankmatch:bankmatch@db:5432/bankmatch \
       --customer-id 1 --top 10"
"""
from __future__ import annotations

import argparse
import json
from typing import Dict, List, Tuple, Any

import psycopg2
from psycopg2.extras import RealDictCursor

# Weights for scoring (very lightweight heuristic)
W_FICO = 0.25
W_DSCR = 0.25
W_AMOUNT = 0.25
W_NEG_DAYS = 0.25


def parse_csv(value: Any) -> List[str]:
    """Split comma-separated strings into a list of trimmed tokens."""
    if not value:
        return []
    return [v.strip() for v in str(value).split(",") if v.strip()]


def fetch_customer(conn, customer_id: int) -> Dict[str, Any]:
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM customer_profiles WHERE id = %s", (customer_id,))
    row = cur.fetchone()
    if not row:
        raise SystemExit(f"Customer id {customer_id} not found")
    return dict(row)


def fetch_products(conn, product_type: str) -> List[Dict[str, Any]]:
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT p.id, b.legal_name AS bank_name, p.product_type,
               p.min_loan_amount_usd, p.max_loan_amount_usd,
               b.lending_footprint AS bank_footprint,
               e.allowed_entities, e.allowed_industries, e.excluded_industries,
               e.geographic_footprint, e.excluded_states,
               e.min_years_in_business, e.min_annual_revenue_usd,
               e.requires_existing_relationship,
               u.min_personal_credit_score, u.min_business_credit_score, u.min_dscr,
               u.min_current_ratio, u.max_debt_to_equity, u.cashflow_positive_required,
               u.negative_balance_days_avg, u.negative_balance_longest_streak,
               u.negative_balance_max_overdraft_usd,
               c.purpose_allowed AS deal_purpose_allowed,
               c.collateral_required, c.eligible_collateral_types,
               c.max_ltv_real_estate, c.max_ltv_equipment,
               c.max_ltv_receivables, c.max_ltv_inventory,
               c.personal_guarantee, c.guarantee_type,
               c.decision_timeline_prequal_days,
               c.decision_timeline_underwriting_days,
               c.average_time_to_fund_days, c.special_conditions
        FROM products p
        JOIN banks b ON p.bank_id = b.id
        LEFT JOIN product_eligibility e ON e.product_id = p.id
        LEFT JOIN product_underwriting u ON u.product_id = p.id
        LEFT JOIN product_collateral c ON c.product_id = p.id
        WHERE p.product_type = %s
        """,
        (product_type,),
    )
    return [dict(r) for r in cur.fetchall()]


# ---------- Filtering helpers ----------

def passes_eligibility(product: Dict[str, Any], cust: Dict[str, Any]) -> Tuple[bool, str]:
    """Return True if *product* passes eligibility for *cust*."""
    # Entity type
    allowed_entities = parse_csv(product.get("allowed_entities"))
    if allowed_entities and cust.get("entity_type") not in allowed_entities:
        return False, f"entity {cust.get('entity_type')} not allowed"

    # Industry checks
    allowed_ind = parse_csv(product.get("allowed_industries"))
    excluded_ind = parse_csv(product.get("excluded_industries"))
    industry = cust.get("industry", "")
    if allowed_ind and industry not in allowed_ind:
        return False, f"industry {industry} not allowed"
    if excluded_ind and industry in excluded_ind:
        return False, f"industry {industry} excluded"

    # Geographic footprint
    footprint = product.get("geographic_footprint") or product.get("bank_footprint")
    states = parse_csv(footprint)
    if states and cust.get("state") not in states:
        return False, f"state {cust.get('state')} not in footprint"
    excluded_states = parse_csv(product.get("excluded_states"))
    if excluded_states and cust.get("state") in excluded_states:
        return False, f"state {cust.get('state')} excluded"

    # Years in business
    min_years = product.get("min_years_in_business")
    if min_years is not None and cust.get("years_in_business", 0) < float(min_years):
        return False, "insufficient years in business"

    # Revenue
    min_rev = product.get("min_annual_revenue_usd")
    if min_rev is not None and cust.get("annual_revenue_usd", 0) < float(min_rev):
        return False, "insufficient revenue"

    # Relationship requirement
    if product.get("requires_existing_relationship"):
        return False, "requires existing relationship"

    return True, "passed"


def passes_underwriting(product: Dict[str, Any], cust: Dict[str, Any]) -> Tuple[bool, str]:
    """Return True if underwriting thresholds are met."""
    fico = product.get("min_personal_credit_score")
    if fico is not None and cust.get("personal_credit_score", 0) < float(fico):
        return False, "personal credit below minimum"

    bscore = product.get("min_business_credit_score")
    if bscore is not None and cust.get("business_credit_score", 0) < float(bscore):
        return False, "business credit below minimum"

    dscr = product.get("min_dscr")
    if dscr is not None and cust.get("dscr", 0) < float(dscr):
        return False, "DSCR below minimum"

    cur_ratio = product.get("min_current_ratio")
    if cur_ratio is not None and cust.get("current_ratio", 0) < float(cur_ratio):
        return False, "current ratio below minimum"

    dte = product.get("max_debt_to_equity")
    if dte is not None and cust.get("debt_to_equity", 0) > float(dte):
        return False, "debt-to-equity above maximum"

    if product.get("cashflow_positive_required") and not cust.get("cashflow_positive"):
        return False, "requires positive cashflow"

    ndays = product.get("negative_balance_days_avg")
    if ndays is not None and cust.get("negative_balance_days_avg", 0) > float(ndays):
        return False, "too many negative balance days"

    nstreak = product.get("negative_balance_longest_streak")
    if nstreak is not None and cust.get("negative_balance_longest_streak", 0) > float(nstreak):
        return False, "negative balance streak too long"

    nmax = product.get("negative_balance_max_overdraft_usd")
    if nmax is not None and cust.get("negative_balance_max_overdraft_usd", 0) > float(nmax):
        return False, "overdraft amount too large"

    return True, "passed"


def passes_deal(product: Dict[str, Any], cust: Dict[str, Any]) -> Tuple[bool, str]:
    """Return True if requested deal fits product constraints."""
    amt = cust.get("requested_amount_usd")
    min_amt = product.get("min_loan_amount_usd")
    max_amt = product.get("max_loan_amount_usd")
    if min_amt is not None and amt is not None and float(amt) < float(min_amt):
        return False, "amount below minimum"
    if max_amt is not None and amt is not None and float(amt) > float(max_amt):
        return False, "amount above maximum"

    purposes = parse_csv(product.get("deal_purpose_allowed"))
    if purposes and cust.get("use_of_proceeds") not in purposes:
        return False, f"purpose {cust.get('use_of_proceeds')} not allowed"

    return True, "passed"


def compute_score(product: Dict[str, Any], cust: Dict[str, Any]) -> float:
    """Compute a simple fit score for ranking purposes."""
    score = 0.0
    fico = product.get("min_personal_credit_score")
    if fico is not None and cust.get("personal_credit_score") is not None:
        score += W_FICO * (cust["personal_credit_score"] - float(fico)) / 100.0

    dscr = product.get("min_dscr")
    if dscr is not None and cust.get("dscr") is not None:
        score += W_DSCR * (cust["dscr"] - float(dscr))

    min_amt = product.get("min_loan_amount_usd")
    max_amt = product.get("max_loan_amount_usd")
    req = cust.get("requested_amount_usd")
    if None not in (min_amt, max_amt, req) and float(max_amt) > float(min_amt):
        mid = (float(max_amt) + float(min_amt)) / 2.0
        half = (float(max_amt) - float(min_amt)) / 2.0
        fit = 1 - abs(float(req) - mid) / half
        score += W_AMOUNT * max(fit, 0)

    ndays = product.get("negative_balance_days_avg")
    if ndays is not None and cust.get("negative_balance_days_avg") is not None:
        score += W_NEG_DAYS * (float(ndays) - cust["negative_balance_days_avg"]) / max(float(ndays), 1)

    return score


def match_products(conn, customer: Dict[str, Any], top: int) -> List[Dict[str, Any]]:
    products = fetch_products(conn, customer["requested_product_type"])
    results: List[Dict[str, Any]] = []
    for p in products:
        ok, _ = passes_eligibility(p, customer)
        if not ok:
            continue
        ok, _ = passes_underwriting(p, customer)
        if not ok:
            continue
        ok, _ = passes_deal(p, customer)
        if not ok:
            continue
        score = compute_score(p, customer)
        results.append({
            "bank": p["bank_name"],
            "product_id": p["id"],
            "score": round(score, 4),
            "min_amount": p.get("min_loan_amount_usd"),
            "max_amount": p.get("max_loan_amount_usd"),
        })
    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top]


def main(argv: List[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Match customer to bank products")
    ap.add_argument("--dsn", required=True, help="Postgres DSN")
    ap.add_argument("--customer-id", type=int)
    ap.add_argument("--state")
    ap.add_argument("--industry")
    ap.add_argument("--entity-type")
    ap.add_argument("--years", type=float, dest="years_in_business")
    ap.add_argument("--revenue", type=float, dest="annual_revenue_usd")
    ap.add_argument("--fico", type=float, dest="personal_credit_score")
    ap.add_argument("--business-score", type=float, dest="business_credit_score")
    ap.add_argument("--dscr", type=float)
    ap.add_argument("--current-ratio", type=float)
    ap.add_argument("--dte", type=float, dest="debt_to_equity")
    ap.add_argument("--cashflow-positive", action="store_true")
    ap.add_argument("--neg-days", type=float, dest="negative_balance_days_avg")
    ap.add_argument("--neg-streak", type=float, dest="negative_balance_longest_streak")
    ap.add_argument("--neg-max", type=float, dest="negative_balance_max_overdraft_usd")
    ap.add_argument("--requested-product-type")
    ap.add_argument("--requested-amount", type=float, dest="requested_amount_usd")
    ap.add_argument("--use-of-proceeds")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    conn = psycopg2.connect(args.dsn)

    if args.customer_id:
        customer = fetch_customer(conn, args.customer_id)
    else:
        required = [
            "state", "industry", "entity_type", "years_in_business",
            "annual_revenue_usd", "personal_credit_score", "dscr",
            "requested_product_type", "requested_amount_usd", "use_of_proceeds"
        ]
        missing = [f for f in required if getattr(args, f) is None]
        if missing:
            raise SystemExit(f"Missing required flags: {', '.join(missing)}")
        customer = {
            "state": args.state,
            "industry": args.industry,
            "entity_type": args.entity_type,
            "years_in_business": args.years_in_business,
            "annual_revenue_usd": args.annual_revenue_usd,
            "personal_credit_score": args.personal_credit_score,
            "business_credit_score": args.business_credit_score,
            "dscr": args.dscr,
            "current_ratio": args.current_ratio,
            "debt_to_equity": args.debt_to_equity,
            "cashflow_positive": args.cashflow_positive,
            "negative_balance_days_avg": args.negative_balance_days_avg,
            "negative_balance_longest_streak": args.negative_balance_longest_streak,
            "negative_balance_max_overdraft_usd": args.negative_balance_max_overdraft_usd,
            "requested_product_type": args.requested_product_type,
            "requested_amount_usd": args.requested_amount_usd,
            "use_of_proceeds": args.use_of_proceeds,
        }

    matches = match_products(conn, customer, args.top)

    if args.json:
        print(json.dumps(matches, indent=2))
    else:
        if not matches:
            print("No matches found")
        else:
            print(f"Found {len(matches)} match(es):")
            print(f"{'Bank':30} {'ProductID':10} {'Score':6} {'Amount Range'}")
            for m in matches:
                rng = f"{m['min_amount']} - {m['max_amount']}"
                print(f"{m['bank'][:30]:30} {m['product_id']:10} {m['score']:<6} {rng}")

    conn.close()


if __name__ == "__main__":
    main()
