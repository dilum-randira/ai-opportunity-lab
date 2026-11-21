"""Deterministic downside screen for caller-defined OrderPilot scenarios.

This is a stress-test summary, not a probability model or investment advice.
"""
from decimal import Decimal
from orderpilot.sensitivity import compare_scenarios


def screen_downside(scenarios: list) -> dict:
    """Summarize the count and magnitude of nonpositive modeled scenarios.

    Reuses compare_scenarios for input validation, equal-volume constraints,
    and the existing unit-economics calculations.
    """
    comparison = compare_scenarios(scenarios)
    rows = comparison["scenarios"]
    nets = [(row["name"], Decimal(row["monthly_lkr"]["net_value"]))
            for row in rows]
    nonpositive = [(name, net) for name, net in nets if net <= 0]
    worst = min(net for _, net in nets)
    best = max(net for _, net in nets)
    return {
        "mode": "HYPOTHETICAL_OFFLINE_DOWNSIDE_SCREEN",
        "monthly_orders": comparison["monthly_orders"],
        "scenario_count": len(nets),
        "nonpositive_scenario_count": len(nonpositive),
        "nonpositive_scenario_names": [name for name, _ in nonpositive],
        "worst_displayed_net_lkr": str(worst),
        "best_displayed_net_lkr": str(best),
        "displayed_spread_lkr": str(best - worst),
        "all_scenarios_positive_under_assumptions":
            comparison["all_scenarios_positive_under_assumptions"],
        "warning": (
            "These scenarios are caller-selected, not random samples. Counts "
            "are not probabilities or risk estimates. Displayed values are "
            "rounded; zero or negative values do not prove business failure, "
            "and positive values do not prove realized savings or profitability."
        ),
    }
