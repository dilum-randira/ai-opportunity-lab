"""Integration regression tests for per-number messaging and merchant ROI."""
import unittest

from orderpilot.merchant_roi import evaluate
from orderpilot.unit_economics import project


class MerchantROITests(unittest.TestCase):
    def test_zero_messages_agrees_with_existing_roi(self):
        kwargs = dict(monthly_orders=520, seconds_saved_per_order="60",
                      hourly_lkr="400", subscription_lkr="2500")
        combined = evaluate(**kwargs, service_messages_by_number=[0])
        base = project(**kwargs)
        self.assertEqual(combined["net_before_platform_messaging_lkr"],
                         base["monthly_lkr"]["net_value"])
        self.assertEqual(combined["net_after_platform_messaging_lkr"],
                         base["monthly_lkr"]["net_value"])
        self.assertEqual(combined["platform_messaging_cost_lkr"], "0.00")

    def test_october_fee_scenario_reverses_merchant_net(self):
        result = evaluate(monthly_orders=520, seconds_saved_per_order="60",
                          hourly_lkr="400", subscription_lkr="2500",
                          service_messages_by_number=[1040], utility_messages=520,
                          service_rate_lkr="3", utility_rate_lkr="3")
        self.assertEqual(result["net_before_platform_messaging_lkr"], "966.67")
        self.assertEqual(result["platform_messaging_cost_lkr"], "1680.00")
        self.assertEqual(result["net_after_platform_messaging_lkr"], "-713.33")
        self.assertFalse(result["positive_after_messaging_under_assumptions"])

    def test_service_allowance_not_pooled(self):
        result = evaluate(monthly_orders=100, seconds_saved_per_order="60",
                          hourly_lkr="600", subscription_lkr="0",
                          service_messages_by_number=[1500, 500], service_rate_lkr="2")
        self.assertEqual(result["message_scenario"]["counts"]["service_billable"], 500)
        self.assertEqual(result["platform_messaging_cost_lkr"], "1000.00")

    def test_all_categories_and_fixed_setup(self):
        result = evaluate(monthly_orders=1, seconds_saved_per_order="0",
                          hourly_lkr="0", subscription_lkr="10", setup_lkr="120",
                          setup_amortization_months=12, hosting_support_lkr="5",
                          service_messages_by_number=[1001], utility_messages=1,
                          marketing_messages=1, authentication_messages=1,
                          service_rate_lkr="2", utility_rate_lkr="3",
                          marketing_rate_lkr="4", authentication_rate_lkr="5")
        self.assertEqual(result["fixed_monthly_cost_lkr"], "25.00")
        self.assertEqual(result["platform_messaging_cost_lkr"], "14.00")
        self.assertEqual(result["net_after_platform_messaging_lkr"], "-39.00")

    def test_precision_uses_unrounded_costs_for_positive_flag(self):
        result = evaluate(monthly_orders=1, seconds_saved_per_order="1",
                          hourly_lkr="1", subscription_lkr="0",
                          service_messages_by_number=[1],
                          free_service_messages_per_number=0,
                          service_rate_lkr="0.004")
        self.assertFalse(result["positive_after_messaging_under_assumptions"])
        self.assertEqual(result["net_after_platform_messaging_lkr"], "0.00")

    def test_invalid_inputs_fail_closed(self):
        kwargs = dict(monthly_orders=1, seconds_saved_per_order="1",
                      hourly_lkr="1", subscription_lkr="0",
                      service_messages_by_number=[0])
        for override in ({"monthly_orders": True},
                         {"seconds_saved_per_order": "NaN"},
                         {"hourly_lkr": "-1"},
                         {"setup_amortization_months": 0},
                         {"service_messages_by_number": [True]},
                         {"utility_messages": -1},
                         {"service_rate_lkr": "Infinity"}):
            with self.subTest(override=override), self.assertRaises(ValueError):
                evaluate(**{**kwargs, **override})

    def test_aggregate_output_excludes_identifiers(self):
        result = evaluate(monthly_orders=1, seconds_saved_per_order="1",
                          hourly_lkr="1", subscription_lkr="0",
                          service_messages_by_number=[0])
        self.assertNotIn("phone_number", result)
        self.assertNotIn("customer", result)
        self.assertEqual(result["message_scenario"]["business_phone_number_count"], 1)


if __name__ == "__main__":
    unittest.main()
