"""Compare multiple cost assumptions across order volumes; offline, no API calls."""
from __future__ import annotations

import argparse
import json
from .unit_economics import project


def compare(*, volumes: list[int], seconds_saved: str, hourly_lkr: str,
            subscription_lkr: str, service_messages: str = "2",
            service_rate_lkr: str = "0", free_messages: int = 0,
            utility_messages: str = "1", utility_rate_lkr: str = "0") -> dict:
    """Return two modeled workflows with the same workload and labor assumptions.

    'No paid messaging' is a workflow assumption (manual/free Business app),
    not a claim that an API sends free messages. Rates are user-supplied LKR.
    """
    if not isinstance(volumes, list) or not 1 <= len(volumes) <= 20:
        raise ValueError("provide between one and twenty monthly order volumes")
    if len(set(map(str, volumes))) != len(volumes):
        raise ValueError("monthly order volumes must not repeat")
    scenarios = []
    for volume in volumes:
        base = dict(monthly_orders=volume, seconds_saved_per_order=seconds_saved,
                    hourly_lkr=hourly_lkr, subscription_lkr=subscription_lkr)
        offline = project(**base)
        platform = project(**base, service_messages_per_order=service_messages,
                           service_rate_lkr=service_rate_lkr,
                           free_service_messages=free_messages,
                           utility_messages_per_order=utility_messages,
                           utility_rate_lkr=utility_rate_lkr)
        scenarios.append({"orders": volume,
                          "no_paid_messaging_net_lkr": offline["monthly_lkr"]["net_value"],
                          "paid_platform_net_lkr": platform["monthly_lkr"]["net_value"],
                          "paid_messaging_lkr": platform["monthly_lkr"]["messaging"],
                          "platform_positive_under_assumptions": platform["commercially_positive_under_assumptions"]})
    return {"mode": "HYPOTHETICAL_COMPARISON_NO_CUSTOMER_DATA",
            "scenarios": scenarios,
            "note": "These are assumptions only. No paid messaging does not imply free Platform messaging. Confirm actual country and provider rates."}


def main() -> int:
    p = argparse.ArgumentParser(description="Compare hypothetical manual and paid-messaging merchant ROI")
    p.add_argument("--volumes", required=True, nargs="+", type=int)
    p.add_argument("--seconds-saved", required=True)
    p.add_argument("--hourly-lkr", required=True)
    p.add_argument("--subscription-lkr", required=True)
    p.add_argument("--service-messages", default="2")
    p.add_argument("--service-rate-lkr", default="0")
    p.add_argument("--free-messages", type=int, default=0)
    p.add_argument("--utility-messages", default="1")
    p.add_argument("--utility-rate-lkr", default="0")
    args = p.parse_args()
    try:
        report = compare(volumes=args.volumes, seconds_saved=args.seconds_saved,
                         hourly_lkr=args.hourly_lkr, subscription_lkr=args.subscription_lkr,
                         service_messages=args.service_messages,
                         service_rate_lkr=args.service_rate_lkr,
                         free_messages=args.free_messages,
                         utility_messages=args.utility_messages,
                         utility_rate_lkr=args.utility_rate_lkr)
    except ValueError as exc:
        p.exit(2, f"Invalid comparison: {exc}\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
