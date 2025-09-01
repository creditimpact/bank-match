-- Sample customer profiles for matching demo
INSERT INTO customer_profiles (
  legal_name, entity_type, industry, state, years_in_business,
  annual_revenue_usd, personal_credit_score, business_credit_score,
  dscr, current_ratio, debt_to_equity, cashflow_positive,
  negative_balance_days_avg, negative_balance_longest_streak,
  negative_balance_max_overdraft_usd, requested_product_type,
  requested_amount_usd, use_of_proceeds
) VALUES
('Acme Restaurants', 'LLC', 'Restaurants', 'CA', 3, 500000, 700, 660,
 1.3, 1.2, 2.5, true, 2, 3, 3000, 'Line_of_Credit', 150000, 'WorkingCapital'),
('Widget Manufacturing', 'S-Corp', 'Manufacturing', 'NY', 5, 2000000, 720, 680,
 1.5, 1.3, 1.8, true, 1, 2, 2000, 'Term_Loan', 500000, 'Equipment');
