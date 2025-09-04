"""Financial feature calculations used by the underwriting engine."""
from __future__ import annotations

from typing import List, Optional


def avg_daily_balance(balances: List[float]) -> Optional[float]:
    """Return the arithmetic mean of daily balances.

    Returns ``None`` when *balances* is empty.
    """
    if not balances:
        return None
    return sum(balances) / len(balances)


def dscr(ebitda: float, annual_debt_service: float) -> Optional[float]:
    """Debt Service Coverage Ratio = EBITDA / Annual Debt Service."""
    if annual_debt_service == 0:
        return None
    return ebitda / annual_debt_service


def month_over_month_growth(values: List[float]) -> List[Optional[float]]:
    """Return percentage growth for each month compared to previous month."""
    growth: List[Optional[float]] = []
    for prev, curr in zip(values, values[1:]):
        if prev == 0:
            growth.append(None)
        else:
            growth.append((curr - prev) / prev)
    return growth
