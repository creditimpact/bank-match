"""Rule-based credit evaluation engine.

This module implements a minimal rule processor used to evaluate borrower metrics
against lender credit boxes.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List

# Supported comparison operators
OPERATORS: Dict[str, Callable[[float, float], bool]] = {
    ">=" : lambda a, b: a >= b,
    "<=" : lambda a, b: a <= b,
    ">"  : lambda a, b: a > b,
    "<"  : lambda a, b: a < b,
    "==" : lambda a, b: a == b,
}


@dataclass
class Rule:
    """Single evaluation rule.

    Attributes:
        field: Metric name to evaluate.
        op: Comparison operator as string.
        threshold: Numeric threshold to compare against.
        weight: Weight used for soft scoring.
        hard: If True, failure results in immediate decline.
    """

    field: str
    op: str
    threshold: float
    weight: float = 1.0
    hard: bool = True


class RulesEngine:
    """Evaluate metrics using a list of :class:`Rule` objects.

    TODO:
        * Load rules from YAML/JSON configuration files.
        * Support nested AND/OR groups and custom functions.
        * Persist detailed decline reasons for audit purposes.
    """

    def __init__(self, rules: List[Rule]):
        self.rules = rules

    def evaluate(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Return evaluation result with approval flag and score."""
        score = 0.0
        reasons: List[str] = []
        for rule in self.rules:
            func = OPERATORS.get(rule.op)
            if not func:
                reasons.append(f"unknown operator {rule.op}")
                continue
            value = metrics.get(rule.field)
            if value is None or not func(value, rule.threshold):
                reasons.append(
                    f"{rule.field} {rule.op} {rule.threshold} failed (value={value})"
                )
                if rule.hard:
                    return {"approved": False, "score": score, "reasons": reasons}
            else:
                if not rule.hard:
                    score += rule.weight
        max_weight = sum(r.weight for r in self.rules if not r.hard)
        pct = (score / max_weight * 100.0) if max_weight > 0 else 0.0
        return {"approved": True, "score": pct, "reasons": reasons}
