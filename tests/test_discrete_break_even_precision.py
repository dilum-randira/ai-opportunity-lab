"""Regression for exact sub-cent first-positive order thresholds."""
import unittest

from orderpilot.discrete_break_even import first_profitable_volume
from orderpilot.unit_economics import project


class DiscreteBreakEvenPrecisionTests(unittest.TestCase):
    def test_subcent_profit_counts_even_if_display_is_zero(self):
        params = dict(seconds_saved_per_order="1", hourly_lkr="1",
                      subscription_lkr="0.0001")
        self.assertEqual(project(monthly_orders=1, **params)["monthly_lkr"]["net_value"], "0.00")
        self.assertTrue(project(monthly_orders=1, **params)["commercially_positive_under_assumptions"])
        self.assertEqual(first_profitable_volume(max_orders=2, **params)["first_positive_monthly_orders"], 1)

    def test_negative_then_subcent_positive_returns_second_order(self):
        params = dict(seconds_saved_per_order="1", hourly_lkr="1",
                      subscription_lkr="0.0003")
        self.assertFalse(project(monthly_orders=1, **params)["commercially_positive_under_assumptions"])
        self.assertEqual(project(monthly_orders=2, **params)["monthly_lkr"]["net_value"], "0.00")
        self.assertEqual(first_profitable_volume(max_orders=2, **params)["first_positive_monthly_orders"], 2)

    def test_zero_margin_not_profitable(self):
        params = dict(seconds_saved_per_order="0", hourly_lkr="100",
                      subscription_lkr="0")
        self.assertIsNone(first_profitable_volume(max_orders=3, **params)["first_positive_monthly_orders"])

    def test_message_rounding_can_delay_positive_volume(self):
        params = dict(seconds_saved_per_order="1", hourly_lkr="1",
                      subscription_lkr="0", utility_messages_per_order="0.5",
                      utility_rate_lkr="0.0003")
        # One order: 0.000277... labor - one 0.0003 message < 0.
        # Two orders: 0.000555... labor - one 0.0003 message > 0.
        self.assertEqual(first_profitable_volume(max_orders=2, **params)["first_positive_monthly_orders"], 2)


if __name__ == "__main__":
    unittest.main()
