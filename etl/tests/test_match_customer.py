import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from etl.match_customer import (
    passes_eligibility,
    passes_underwriting,
    passes_deal,
    compute_score,
)


def make_product():
    return {
        "id": 1,
        "bank_name": "Sample Bank",
        "allowed_entities": "LLC,S-Corp",
        "allowed_industries": "Restaurants,Retail",
        "excluded_industries": "Cannabis",
        "geographic_footprint": "CA,NY",
        "excluded_states": "NV",
        "min_years_in_business": 2,
        "min_annual_revenue_usd": 100000,
        "requires_existing_relationship": False,
        "min_personal_credit_score": 680,
        "min_business_credit_score": 650,
        "min_dscr": 1.2,
        "min_current_ratio": 1.1,
        "max_debt_to_equity": 3.0,
        "cashflow_positive_required": True,
        "negative_balance_days_avg": 3,
        "negative_balance_longest_streak": 5,
        "negative_balance_max_overdraft_usd": 5000,
        "min_loan_amount_usd": 50000,
        "max_loan_amount_usd": 250000,
        "deal_purpose_allowed": "WorkingCapital,Equipment",
    }


def make_customer():
    return {
        "entity_type": "LLC",
        "industry": "Restaurants",
        "state": "CA",
        "years_in_business": 3,
        "annual_revenue_usd": 500000,
        "personal_credit_score": 700,
        "business_credit_score": 660,
        "dscr": 1.3,
        "current_ratio": 1.2,
        "debt_to_equity": 2.5,
        "cashflow_positive": True,
        "negative_balance_days_avg": 2,
        "negative_balance_longest_streak": 3,
        "negative_balance_max_overdraft_usd": 3000,
        "requested_amount_usd": 150000,
        "use_of_proceeds": "WorkingCapital",
    }


def test_eligibility_and_underwriting_pass():
    product = make_product()
    customer = make_customer()
    assert passes_eligibility(product, customer)[0]
    assert passes_underwriting(product, customer)[0]


def test_deal_and_score():
    product = make_product()
    customer = make_customer()
    ok, _ = passes_deal(product, customer)
    assert ok
    score = compute_score(product, customer)
    assert score > 0
