"""Pilot screening gate: synthetic examples never count as verified evidence."""
import unittest
from decimal import Decimal
from orderpilot.pilot_gate import screen


class PilotGateTests(unittest.TestCase):
    def setUp(self):
        self.pairs = [(Decimal("120"), Decimal("60"), 1, 0)] * 24
        self.kwargs = dict(study_kind="consented_aggregate", pairs=self.pairs,
                           consenting_merchants=5, merchants_reporting_repeated_pain=3,
                           merchants_discussing_price=2, modeled_net_lkr="1200")

    def test_positive_screen_requires_all_checks(self):
        result = screen(**self.kwargs)
        self.assertEqual(result["status"], "REVIEW_CANDIDATE_NOT_PILOT_APPROVAL")
        self.assertTrue(all(result["checks"].values()))

    def test_synthetic_never_passes(self):
        result = screen(**{**self.kwargs, "study_kind": "synthetic"})
        self.assertEqual(result["status"], "EVIDENCE_INSUFFICIENT")
        self.assertFalse(result["checks"]["consented_observations"])

    def test_negative_or_zero_mean_fails(self):
        pairs = [(Decimal(30), Decimal(60), 0, 0)] * 24
        result = screen(**{**self.kwargs, "pairs": pairs})
        self.assertFalse(result["checks"]["positive_unrounded_mean_time_saving"])

    def test_more_errors_fails(self):
        pairs = [(Decimal(120), Decimal(60), 0, 1)] * 24
        result = screen(**{**self.kwargs, "pairs": pairs})
        self.assertFalse(result["checks"]["no_increase_in_errors"])

    def test_nonpositive_profit_fails(self):
        result = screen(**{**self.kwargs, "modeled_net_lkr": "0"})
        self.assertFalse(result["checks"]["positive_modeled_net_value"])

    def test_undersized_study_fails(self):
        result = screen(**{**self.kwargs, "pairs": self.pairs[:2], "consenting_merchants": 2,
                           "merchants_reporting_repeated_pain": 1, "merchants_discussing_price": 1})
        self.assertFalse(result["checks"]["screening_sample_target"])

    def test_invalid_study_kind_and_merchant_counts(self):
        for change in (
            {"study_kind": "real"},
            {"consenting_merchants": True},
            {"merchants_reporting_repeated_pain": 6},
            {"merchants_discussing_price": 6},
            {"consenting_merchants": -1},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                screen(**{**self.kwargs, **change})

    def test_invalid_pair_rows_and_numeric_values(self):
        for bad in (
            [(1, 2, 0)],
            [(1, 2, 0, 0, 0)],
            [(Decimal("NaN"), 1, 0, 0)],
            [(Decimal("Infinity"), 1, 0, 0)],
            [(-1, 1, 0, 0)],
            [(1, 1, 0.5, 0)],
            [(1, 1, True, 0)],
            [(1, 1, 0, 101)],
            [("customer@example.com", 1, 0, 0)],
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                screen(**{**self.kwargs, "pairs": bad})

    def test_invalid_modeled_profit(self):
        for bad in ("NaN", "Infinity", "-1", True, "invalid"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                screen(**{**self.kwargs, "modeled_net_lkr": bad})


if __name__ == "__main__":
    unittest.main()
