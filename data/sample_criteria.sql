-- Sample product criteria for matching demo
-- Assumes products with IDs 1 and 2 already exist (e.g., from ingested sample batch)

INSERT INTO product_eligibility (
  product_id, allowed_entities, allowed_industries, excluded_industries,
  geographic_footprint, excluded_states, min_years_in_business,
  min_annual_revenue_usd, requires_existing_relationship, notes
) VALUES
(1, 'LLC,S-Corp', 'Restaurants,Manufacturing', 'Cannabis', NULL, 'NV', 2, 100000, false, NULL),
(2, 'LLC,S-Corp', NULL, NULL, NULL, NULL, 1, 50000, false, NULL);

INSERT INTO product_underwriting (
  product_id, min_personal_credit_score, min_business_credit_score, min_dscr,
  min_current_ratio, max_debt_to_equity, cashflow_positive_required,
  negative_balance_days_avg, negative_balance_longest_streak,
  negative_balance_max_overdraft_usd, documents_required
) VALUES
(1, 680, 650, 1.2, 1.1, 3.0, true, 3, 5, 5000, NULL),
(2, 700, 670, 1.3, 1.1, 2.5, true, 2, 4, 3000, NULL);

INSERT INTO product_collateral (
  product_id, collateral_required, eligible_collateral_types,
  max_ltv_real_estate, max_ltv_equipment, max_ltv_receivables, max_ltv_inventory,
  personal_guarantee, guarantee_type, purpose_allowed,
  decision_timeline_prequal_days, decision_timeline_underwriting_days,
  average_time_to_fund_days, special_conditions
) VALUES
(1, 'Case-by-case', 'RealEstate,Equipment', 80, 70, NULL, NULL, 'Required', 'Personal', 'WorkingCapital,Equipment', 5, 10, 15, NULL),
(2, 'Yes', 'Equipment', 70, 80, NULL, NULL, 'Required', 'Personal', 'Equipment', 7, 14, 30, NULL);
