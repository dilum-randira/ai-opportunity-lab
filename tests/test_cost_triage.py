import unittest

from orderpilot.cost_triage import prioritize_cost_review


class CostTriageTests(unittest.TestCase):
    def row(self, name, kind, observed_on):
        return {
            "name": name, "kind": kind, "lkr_per_unit": "3.50",
            "observed_on": observed_on,
            "source_url": "" if kind == "internal_assumption" else "https://example.com/pricing",
        }

    def test_assumptions_first_then_stale_then_recent(self):
        rows = [
            self.row("Recent", "public_price_list", "2026-11-15"),
            self.row("Old", "provider_quote", "2026-09-01"),
            self.row("Assumption", "internal_assumption", "2026-11-18"),
        ]
        result = prioritize_cost_review(rows, as_of="2026-11-19")
        self.assertEqual([x["name"] for x in result["queue"]],
                         ["Assumption", "Old", "Recent"])
        self.assertEqual([x["priority"] for x in result["queue"]], [1, 2, 3])
        self.assertEqual(result["stale_count"], 1)
        self.assertFalse(result["ready_for_commercial_pricing_claims"])
        self.assertEqual(result["verified_provider_prices"], 0)

    def test_stable_order_within_priority(self):
        rows = [self.row("Z", "public_price_list", "2026-10-01"),
                self.row("A", "provider_quote", "2026-10-01"),
                self.row("Newer", "public_price_list", "2026-10-02")]
        result = prioritize_cost_review(rows, as_of="2026-11-19", max_age_days=30)
        self.assertEqual([x["name"] for x in result["queue"]], ["A", "Z", "Newer"])

    def test_does_not_expose_unverified_price_or_url(self):
        result = prioritize_cost_review(
            [self.row("Sample", "internal_assumption", "2026-11-01")],
            as_of="2026-11-19")
        self.assertTrue(result["missing_external_evidence"])
        self.assertTrue(result["queue"][0]["requires_manual_verification"])
        self.assertNotIn("source_url", str(result))
        self.assertNotIn("lkr_per_unit", str(result))
        self.assertNotIn("3.50", str(result))

    def test_external_sources_still_not_verified(self):
        result = prioritize_cost_review(
            [self.row("External", "public_price_list", "2026-11-18")],
            as_of="2026-11-19")
        self.assertFalse(result["missing_external_evidence"])
        self.assertFalse(result["ready_for_commercial_pricing_claims"])

    def test_rejects_invalid_inputs_using_existing_validator(self):
        with self.assertRaises(ValueError):
            prioritize_cost_review([], as_of="2026-11-19")
        with self.assertRaises(ValueError):
            prioritize_cost_review(
                [self.row("Future", "provider_quote", "2026-11-20")],
                as_of="2026-11-19")
        with self.assertRaises(ValueError):
            prioritize_cost_review(
                [self.row("Sample", "internal_assumption", "2026-11-01")],
                as_of="2026-11-19", max_age_days=True)


if __name__ == "__main__":
    unittest.main()
