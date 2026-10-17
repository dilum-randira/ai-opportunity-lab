"""Regression tests for the offline unit-economics engine."""
import unittest
from orderpilot.unit_economics import project

BASE = dict(monthly_orders=60, seconds_saved_per_order=60, hourly_lkr="600",
            subscription_lkr="500")


class UnitEconomicsTests(unittest.TestCase):
    def test_known_positive_scenario(self):
        result = project(**BASE)
        self.assertEqual(result["monthly_lkr"]["gross_labor_value"], "600.00")
        self.assertEqual(result["monthly_lkr"]["net_value"], "100.00")
        self.assertEqual(result["monthly_lkr"]["net_roi_percent"], "20.00")
        self.assertEqual(result["conservative_break_even_orders_excluding_allowance"], 50)

    def test_service_allowance_applied_to_service_only(self):
        result = project(**BASE, service_messages_per_order="2", service_rate_lkr="3",
                         utility_messages_per_order="1", utility_rate_lkr="4",
                         free_service_messages=100)
        self.assertEqual(result["messages"]["service_total"], 120)
        self.assertEqual(result["messages"]["service_billable"], 20)
        self.assertEqual(result["messages"]["utility_total"], 60)
        self.assertEqual(result["monthly_lkr"]["messaging"], "300.00")

    def test_no_allowance_by_default(self):
        result = project(**BASE, service_messages_per_order="1", service_rate_lkr="3")
        self.assertEqual(result["messages"]["service_billable"], 60)
        self.assertEqual(result["monthly_lkr"]["messaging"], "180.00")

    def test_setup_is_amortized_not_fully_repeated(self):
        result = project(**BASE, setup_lkr="1200", setup_amortization_months=12, hosting_support_lkr="50")
        self.assertEqual(result["monthly_lkr"]["amortized_setup"], "100.00")
        self.assertEqual(result["monthly_lkr"]["total_cost"], "650.00")

    def test_fractional_messages_rounded_up_on_month(self):
        result = project(**(BASE | {"monthly_orders": 3}), service_messages_per_order="0.5",
                         service_rate_lkr="10")
        self.assertEqual(result["messages"]["service_total"], 2)

    def test_break_even_conservative_when_free_allowance(self):
        result = project(**BASE, service_messages_per_order="2", service_rate_lkr="3",
                         free_service_messages=1000)
        self.assertEqual(result["monthly_lkr"]["messaging"], "0.00")
        self.assertEqual(result["conservative_break_even_orders_excluding_allowance"], 125)

    def test_negative_contribution_no_break_even(self):
        result = project(**BASE, service_messages_per_order="1", service_rate_lkr="1000")
        self.assertIsNone(result["conservative_break_even_orders_excluding_allowance"])

    def test_zero_cost_roi_percentage_not_defined(self):
        result = project(**(BASE | {"subscription_lkr": "0"}))
        self.assertIsNone(result["monthly_lkr"]["net_roi_percent"])

    def test_errors_on_non_finite_or_negative_prices(self):
        for value in ("NaN", "Infinity", "-1", True, "oops"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                project(**(BASE | {"hourly_lkr": value}))

    def test_invalid_counts(self):
        for orders in (True, 0, -1, 1000001, "60"):
            with self.subTest(orders=orders), self.assertRaises(ValueError):
                project(**(BASE | {"monthly_orders": orders}))
        for allowance in (True, -1, 10000001):
            with self.subTest(allowance=allowance), self.assertRaises(ValueError):
                project(**BASE, free_service_messages=allowance)

    def test_unrealistic_time_rejected(self):
        with self.assertRaises(ValueError):
            project(**(BASE | {"seconds_saved_per_order": 36001}))

    def test_large_yet_valid_order_volume(self):
        result = project(**(BASE | {"monthly_orders": 1000000}))
        self.assertEqual(result["monthly_orders"], 1000000)


if __name__ == '__main__':
    unittest.main()
