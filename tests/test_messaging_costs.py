"""Regression tests for the per-number, privacy-minimal message cost model."""
import unittest
from decimal import Decimal
from orderpilot.messaging_costs import estimate


class MessagingCostTests(unittest.TestCase):
    def test_exactly_one_thousand_service_messages_are_free(self):
        result = estimate(service_messages_by_number=[1000], service_rate_lkr="4")
        self.assertEqual(result["counts"]["service_free"], 1000)
        self.assertEqual(result["counts"]["service_billable"], 0)
        self.assertEqual(result["cost_lkr"]["total"], "0.00")

    def test_one_thousand_and_one_charges_one(self):
        result = estimate(service_messages_by_number=[1001], service_rate_lkr="4.25")
        self.assertEqual(result["counts"]["service_billable"], 1)
        self.assertEqual(result["cost_lkr"]["service"], "4.25")

    def test_allowance_is_per_number_not_pooled(self):
        result = estimate(service_messages_by_number=[1500, 500], service_rate_lkr="2")
        self.assertEqual(result["counts"]["service_free"], 1500)
        self.assertEqual(result["counts"]["service_billable"], 500)
        self.assertEqual(result["cost_lkr"]["service"], "1000.00")

    def test_unused_allowance_does_not_transfer(self):
        result = estimate(service_messages_by_number=[2000, 0], service_rate_lkr="3")
        self.assertEqual(result["counts"]["service_billable"], 1000)
        self.assertEqual(result["cost_lkr"]["total"], "3000.00")

    def test_utility_templates_do_not_use_service_allowance(self):
        result = estimate(service_messages_by_number=[0], utility_messages=1,
                          utility_rate_lkr="7")
        self.assertEqual(result["counts"]["utility_billable"], 1)
        self.assertEqual(result["cost_lkr"]["total"], "7.00")

    def test_all_categories_are_added(self):
        result = estimate(service_messages_by_number=[1002], utility_messages=3,
                          marketing_messages=2, authentication_messages=1,
                          service_rate_lkr="2", utility_rate_lkr="3",
                          marketing_rate_lkr="4", authentication_rate_lkr="5")
        self.assertEqual(result["cost_lkr"], {
            "service": "4.00", "utility": "9.00", "marketing": "8.00",
            "authentication": "5.00", "total": "26.00"})

    def test_fractional_rates_round_money_only_at_output(self):
        result = estimate(service_messages_by_number=[1003], service_rate_lkr="0.005")
        self.assertEqual(result["cost_lkr"]["service"], "0.02")
        self.assertEqual(result["cost_lkr"]["total"], "0.02")

    def test_hypothetical_lkr_scenario(self):
        result = estimate(service_messages_by_number=[1040], utility_messages=520,
                          service_rate_lkr="3", utility_rate_lkr="3")
        self.assertEqual(result["cost_lkr"]["total"], "1680.00")

    def test_custom_allowance_explicitly_supported(self):
        result = estimate(service_messages_by_number=[5],
                          free_service_messages_per_number=3,
                          service_rate_lkr="2")
        self.assertEqual(result["counts"]["service_billable"], 2)

    def test_zero_deliveries(self):
        result = estimate(service_messages_by_number=[0])
        self.assertEqual(result["cost_lkr"]["total"], "0.00")

    def test_invalid_service_lists(self):
        for value in ([], [0] * 21, "100", (100,), None, [True], [-1], [1.5], [1000001]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                estimate(service_messages_by_number=value)

    def test_invalid_other_counts(self):
        for value in (-1, True, 1.1, "2", 1000001):
            with self.subTest(value=value), self.assertRaises(ValueError):
                estimate(service_messages_by_number=[0], marketing_messages=value)

    def test_invalid_allowances(self):
        for value in (-1, True, "1000", 1000001):
            with self.subTest(value=value), self.assertRaises(ValueError):
                estimate(service_messages_by_number=[0], free_service_messages_per_number=value)

    def test_invalid_rates(self):
        for value in ("NaN", "Infinity", "-1", True, "abc", "1000000.01", float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                estimate(service_messages_by_number=[0], service_rate_lkr=value)

    def test_decimal_rate(self):
        result = estimate(service_messages_by_number=[1001], service_rate_lkr=Decimal("1.75"))
        self.assertEqual(result["cost_lkr"]["total"], "1.75")

    def test_no_personal_data_in_result(self):
        result = estimate(service_messages_by_number=[20])
        self.assertNotIn("phone_number", result)
        self.assertNotIn("customer", result)
        self.assertEqual(result["business_phone_number_count"], 1)


if __name__ == "__main__":
    unittest.main()
