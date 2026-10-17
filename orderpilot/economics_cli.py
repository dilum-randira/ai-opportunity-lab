"""CLI for local economic scenarios; no file uploads or external API calls."""
from __future__ import annotations
import argparse
import json
from .unit_economics import project


def main() -> int:
    parser = argparse.ArgumentParser(description="Model hypothetical merchant ROI in LKR")
    parser.add_argument("--orders", type=int, required=True)
    parser.add_argument("--seconds-saved", required=True)
    parser.add_argument("--hourly-lkr", required=True)
    parser.add_argument("--subscription-lkr", required=True)
    parser.add_argument("--setup-lkr", default="0")
    parser.add_argument("--setup-months", type=int, default=12)
    parser.add_argument("--hosting-support-lkr", default="0")
    parser.add_argument("--service-messages-per-order", default="0")
    parser.add_argument("--service-rate-lkr", default="0")
    parser.add_argument("--free-service-messages", type=int, default=0)
    parser.add_argument("--utility-messages-per-order", default="0")
    parser.add_argument("--utility-rate-lkr", default="0")
    args = parser.parse_args()
    try:
        result = project(
            monthly_orders=args.orders,
            seconds_saved_per_order=args.seconds_saved,
            hourly_lkr=args.hourly_lkr,
            subscription_lkr=args.subscription_lkr,
            setup_lkr=args.setup_lkr,
            setup_amortization_months=args.setup_months,
            hosting_support_lkr=args.hosting_support_lkr,
            service_messages_per_order=args.service_messages_per_order,
            service_rate_lkr=args.service_rate_lkr,
            free_service_messages=args.free_service_messages,
            utility_messages_per_order=args.utility_messages_per_order,
            utility_rate_lkr=args.utility_rate_lkr,
        )
    except ValueError as exc:
        parser.exit(2, f"Invalid hypothetical scenario: {exc}\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
