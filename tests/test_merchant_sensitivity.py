"""Synthetic, privacy-safe tests of merchant-level leave-one-out sensitivity."""
import unittest
from decimal import Decimal

from orderpilot.merchant_sensitivity import leave_one_merchant_out
from orderpilot.merchant_aggregation import aggregate_merchants


class MerchantSensitivityTests(unittest.TestCase):
    def test_exact_unequal_merchant_savings(self):
        result = leave_one_merchant_out([
            ("10", "5", 0, 0), ("20", "10", 1, 0), ("8", "9", 0, 1)
        ])
        self.assertEqual(result["merchant_count"], 3)
        self.assertEqual(Decimal(result["overall_mean_saving_seconds"]), Decimal("14") / 3)
        self.assertEqual(Decimal(result["leave_one_out_min_mean_saving_seconds"]), Decimal("2"))
        self.assertEqual(Decimal(result["leave_one_out_max_mean_saving_seconds"]), Decimal("7.5"))
        self.assertTrue(result["all_leave_one_out_means_positive"])

    def test_single_positive_merchant_is_not_robust(self):
        result = leave_one_merchant_out([(20, 10, 0, 0), (10, 10, 0, 0)])
        self.assertEqual(result["leave_one_out_min_mean_saving_seconds"], "0")
        self.assertFalse(result["all_leave_one_out_means_positive"])

    def test_two_merchants_with_losses(self):
        result = leave_one_merchant_out([(2, 4, 0, 1), (10, 9, 1, 0)])
        self.assertEqual(result["leave_one_out_min_mean_saving_seconds"], "-2")
        self.assertEqual(result["leave_one_out_max_mean_saving_seconds"], "1")
        self.assertFalse(result["all_leave_one_out_means_positive"])

    def test_aggregation_integrates_without_order_level_inflation(self):
        pairs = aggregate_merchants([
            [(20, 10, 0, 0), (30, 20, 0, 0)],
            [(10, 8, 0, 0)],
        ])
        result = leave_one_merchant_out(pairs)
        self.assertEqual(result["merchant_count"], 2)
        self.assertEqual(result["overall_mean_saving_seconds"], "6")
        self.assertEqual(result["leave_one_out_min_mean_saving_seconds"], "2")

    def test_reject_malformed_inputs(self):
        bad = [None, {}, [], [[(1, 2, 0, 0)]], [(1, 2, 0, 0)],
               [(1, 2, 0, 0)] * 1001,
               [(1, 2, 0)] * 2, [(1, 2, 0, 0, 5)] * 2,
               [("NaN", 2, 0, 0)] * 2,
               [(True, 2, 0, 0)] * 2,
               [(-1, 2, 0, 0)] * 2,
               [(36001, 2, 0, 0)] * 2,
               [(1, 2, True, 0)] * 2,
               [(1, 2, 0, 2)] * 2,
               [("customer@example.com", 2, 0, 0)] * 2]
        for item in bad:
            with self.subTest(value=str(item)[:60]), self.assertRaises(ValueError):
                leave_one_merchant_out(item)


if __name__ == "__main__":
    unittest.main()
