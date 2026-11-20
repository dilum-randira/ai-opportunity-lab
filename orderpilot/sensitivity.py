"""Offline sensitivity analysis for explicitly hypothetical merchant economics.

Scenario inputs are supplied by the caller, never fetched or presented as
observed merchant behavior. This tool does not predict demand or profitability.
"""
from decimal import Decimal
from orderpilot.unit_economics import project


def compare_scenarios(scenarios: list) -> dict:
    """Compare 2..12 named, equal-volume hypothetical scenarios.

    All scenarios must supply the complete set of required project() inputs.
    Optional cost inputs use project() defaults. No external data is fetched.
    """
    if not isinstance(scenarios, list) or not 2 <= len(scenarios) <= 12:
        raise ValueError("scenarios must be a list of 2..12 entries")
    names = set()
    results = []
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            raise ValueError("each scenario must be an object")
        name = scenario.get("name")
        if (not isinstance(name, str) or not 1 <= len(name) <= 60
                or name != name.strip() or name in names
                or any(ord(char) < 32 or ord(char) == 127 for char in name)):
            raise ValueError("scenario names must be unique printable strings")
        names.add(name)
        inputs = {key: value for key, value in scenario.items() if key != "name"}
        report = project(**inputs)
        results.append({
            "name": name,
            "monthly_orders": report["monthly_orders"],
            "monthly_lkr": report["monthly_lkr"],
            "commercially_positive_under_assumptions":
                report["commercially_positive_under_assumptions"],
        })
    volumes = {entry["monthly_orders"] for entry in results}
    if len(volumes) != 1:
        raise ValueError("all scenarios must use the same monthly_orders")
    # Rounded display values are only for reporting; do not infer a reliable
    # ranking or break-even from sub-cent differences.
    nets = [Decimal(entry["monthly_lkr"]["net_value"]) for entry in results]
    return {
        "mode": "HYPOTHETICAL_OFFLINE_SENSITIVITY",
        "monthly_orders": results[0]["monthly_orders"],
        "scenarios": results,
        "displayed_net_range_lkr": {
            "minimum": str(min(nets)),
            "maximum": str(max(nets)),
        },
        "all_scenarios_positive_under_assumptions":
            all(item["commercially_positive_under_assumptions"] for item in results),
        "warning": (
            "Caller-supplied assumptions only; displayed net values are rounded "
            "to cents. Not observed savings, verified provider pricing, "
            "customer demand, or a profitability forecast."
        ),
    }
