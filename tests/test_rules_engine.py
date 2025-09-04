from src.scoring.rules_engine import Rule, RulesEngine


def test_rules_engine_approves_and_scores():
    rules = [
        Rule("fico", ">=", 660, hard=True),
        Rule("dscr", ">=", 1.2, weight=50, hard=False),
        Rule("years", ">=", 2, weight=50, hard=False),
    ]
    engine = RulesEngine(rules)
    metrics = {"fico": 700, "dscr": 1.3, "years": 5}
    result = engine.evaluate(metrics)
    assert result["approved"] is True
    assert result["score"] == 100.0


def test_rules_engine_declines_on_hard_rule():
    rules = [Rule("fico", ">=", 700, hard=True)]
    engine = RulesEngine(rules)
    metrics = {"fico": 650}
    result = engine.evaluate(metrics)
    assert result["approved"] is False
