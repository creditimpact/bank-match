-- 0002_match_schema.sql

-- Eligibility — prefilter ("gate") criteria per product
CREATE TABLE IF NOT EXISTS product_eligibility (
  product_id INTEGER PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
  allowed_entities TEXT,
  allowed_industries TEXT,
  excluded_industries TEXT,
  geographic_footprint TEXT,
  excluded_states TEXT,
  min_years_in_business NUMERIC,
  min_annual_revenue_usd NUMERIC,
  requires_existing_relationship BOOLEAN,
  notes TEXT
);

-- Underwriting — basic credit requirements per product
CREATE TABLE IF NOT EXISTS product_underwriting (
  product_id INTEGER PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
  min_personal_credit_score NUMERIC,
  min_business_credit_score NUMERIC,
  min_dscr NUMERIC,
  min_current_ratio NUMERIC,
  max_debt_to_equity NUMERIC,
  cashflow_positive_required BOOLEAN,
  negative_balance_days_avg NUMERIC,
  negative_balance_longest_streak NUMERIC,
  negative_balance_max_overdraft_usd NUMERIC,
  documents_required TEXT
);

-- Deal & Collateral — structure and collateral expectations
CREATE TABLE IF NOT EXISTS product_collateral (
  product_id INTEGER PRIMARY KEY REFERENCES products(id) ON DELETE CASCADE,
  collateral_required TEXT,
  eligible_collateral_types TEXT,
  max_ltv_real_estate NUMERIC,
  max_ltv_equipment NUMERIC,
  max_ltv_receivables NUMERIC,
  max_ltv_inventory NUMERIC,
  personal_guarantee TEXT,
  guarantee_type TEXT,
  purpose_allowed TEXT,
  decision_timeline_prequal_days INTEGER,
  decision_timeline_underwriting_days INTEGER,
  average_time_to_fund_days INTEGER,
  special_conditions TEXT
);

-- Customer profiles — minimal inputs for quick in-office matching
CREATE TABLE IF NOT EXISTS customer_profiles (
  id SERIAL PRIMARY KEY,
  legal_name TEXT,
  entity_type TEXT,
  industry TEXT,
  state TEXT,
  years_in_business NUMERIC,
  annual_revenue_usd NUMERIC,
  personal_credit_score NUMERIC,
  business_credit_score NUMERIC,
  dscr NUMERIC,
  current_ratio NUMERIC,
  debt_to_equity NUMERIC,
  cashflow_positive BOOLEAN,
  negative_balance_days_avg NUMERIC,
  negative_balance_longest_streak NUMERIC,
  negative_balance_max_overdraft_usd NUMERIC,
  requested_product_type TEXT,
  requested_amount_usd NUMERIC,
  use_of_proceeds TEXT
);
