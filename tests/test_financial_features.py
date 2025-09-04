from src.features.financial_features import avg_daily_balance, dscr, month_over_month_growth

def test_avg_daily_balance():
    assert avg_daily_balance([100.0, 200.0, 300.0]) == 200.0
    assert avg_daily_balance([]) is None


def test_dscr():
    assert dscr(120.0, 100.0) == 1.2
    assert dscr(100.0, 0.0) is None


def test_month_over_month_growth():
    assert month_over_month_growth([100.0, 110.0, 121.0]) == [0.1, 0.1]
    assert month_over_month_growth([0.0, 50.0]) == [None]
