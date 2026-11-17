import unittest

from orderpilot.cost_review import review_cost_evidence


class CostReviewTests(unittest.TestCase):
    def setUp(self):
        self.base = {"name": "Illustrative message", "kind": "internal_assumption",
                     "lkr_per_unit": "3.50", "observed_on": "2026-11-01", "source_url": ""}

    def test_boundary_and_staleness(self):
        report = review_cost_evidence([self.base], as_of="2026-12-01", max_age_days=30)
        self.assertEqual(report["stale_count"], 0)
        self.assertEqual(report["items"][0]["age_days"], 30)
        later = review_cost_evidence([self.base], as_of="2026-12-02", max_age_days=30)
        self.assertEqual(later["stale_count"], 1)

    def test_external_evidence_not_equated_with_verification(self):
        external = {**self.base, "name": "Illustrative external reference",
                    "kind": "public_price_list", "source_url": "https://example.com/pricing"}
        report = review_cost_evidence([self.base, external], as_of="2026-11-18")
        self.assertFalse(report["missing_external_evidence"])
        self.assertEqual(report["verified_provider_prices"], 0)
        self.assertEqual(report["counts_by_kind"]["public_price_list"], 1)
        self.assertTrue(all(item["requires_manual_verification"] for item in report["items"]))
        self.assertNotIn("source_url", report["items"][0])
        self.assertNotIn("lkr_per_unit", report["items"][0])

    def test_assumptions_only_are_flagged(self):
        report = review_cost_evidence([self.base], as_of="2026-11-18")
        self.assertTrue(report["missing_external_evidence"])

    def test_threshold_rejects_bool_float_and_out_of_range(self):
        for value in (True, 0, 366, 2.5, "30", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                review_cost_evidence([self.base], as_of="2026-11-18", max_age_days=value)

    def test_original_validator_rejects_future_dates_and_unknown_fields(self):
        for row in ({**self.base, "observed_on": "2026-11-19"},
                    {**self.base, "customer_phone": "not allowed"}):
            with self.assertRaises(ValueError):
                review_cost_evidence([row], as_of="2026-11-18")


if __name__ == "__main__":
    unittest.main()
