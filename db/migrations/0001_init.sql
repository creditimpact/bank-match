CREATE TABLE IF NOT EXISTS banks (
  id SERIAL PRIMARY KEY,
  fdic_certificate TEXT NOT NULL,
  legal_name TEXT NOT NULL,
  website TEXT,
  lending_footprint TEXT,
  UNIQUE(fdic_certificate)
);

CREATE TABLE IF NOT EXISTS products (
  id SERIAL PRIMARY KEY,
  bank_id INTEGER NOT NULL REFERENCES banks(id) ON DELETE CASCADE,
  product_type TEXT NOT NULL,
  min_loan_amount_usd NUMERIC,
  max_loan_amount_usd NUMERIC,
  rate_structure TEXT,
  min_years_in_business NUMERIC,
  min_annual_revenue_usd NUMERIC,
  min_personal_credit_score NUMERIC,
  min_dscr NUMERIC,
  max_ltv_real_estate NUMERIC,
  max_ltv_equipment NUMERIC,
  max_ltv_receivables NUMERIC,
  max_ltv_inventory NUMERIC,
  personal_guarantee TEXT,
  collateral_required TEXT,
  industry_restrictions TEXT,
  decision_timeline_prequal_days INTEGER,
  decision_timeline_underwriting_days INTEGER,
  last_verified DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
  id SERIAL PRIMARY KEY,
  product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  source_url TEXT NOT NULL,
  evidence_type TEXT,
  title TEXT,
  date_accessed DATE
);

CREATE INDEX IF NOT EXISTS idx_products_bank_type ON products(bank_id, product_type);
