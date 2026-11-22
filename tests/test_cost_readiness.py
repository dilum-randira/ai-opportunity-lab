import unittest

from orderpilot.cost_readiness import assess_cost_research_readiness


class CostReadinessTests(unittest.TestCase):
    def row(self, name, kind, observed_on):
        return {
            "name": name, "kind": kind, "lkr_per_unit": "2.50",
            "observed_on": observed_on,
            "source_url": "" if kind == "internal_assumption" else "https://example.com/pricing",
        }

    def test_assumptions_require_external_evidence(self):
        report = assess_cost_research_readiness(
            [self.row("assumed", "internal_assumption", "2026-11-01")],
            as_of="2026-11-23")
        self.assertEqual(report["external_reference_count"], 0)
        self.assertFalse(report["has_minimum_reference_mix"])
        self.assertTrue(report["research_gaps"])

    def test_mixed_fresh_references_do_not_verify_prices(self):
        rows = [self.row("quote", "provider_quote", "2026-11-20"),
                self.row("list", "public_price_list", "2026-11-21")]
        report = assess_cost_research_readiness(rows, as_of="2026-11-23")
        self.assertTrue(report["has_minimum_reference_mix"])
        self.assertEqual(report["fresh_external_reference_count"], 2)
        self.assertEqual(report["verified_provider_prices"], 0)
        self.assertFalse(report["ready_for_commercial_pricing_claims"])
        self.assertNotIn("lkr_per_unit", str(report))
        self.assertNotIn("source_url", str(report))

    def test_stale_references_are_flagged(self):
        rows = [self.row("quote", "provider_quote", "2026-10-01"),
                self.row("list", "public_price_list", "2026-10-01")]
        report = assess_cost_research_readiness(rows, as_of="2026-11-23")
        self.assertEqual(report["fresh_external_reference_count"], 0)
        self.assertIn("refresh external pricing references older than the review threshold",
                      report["research_gaps"])

    def test_invalid_input_uses_strict_validator(self):
        with self.assertRaises(ValueError):
            assess_cost_research_readiness(
                [self.row("future", "provider_quote", "2026-11-24")],
                as_of="2026-11-23")

    def test_freshness_boundary(self):
        report = assess_cost_research_readiness(
            [self.row("quote", "provider_quote", "2026-10-24")],
            as_of="2026-11-23")
        self.assertEqual(report["fresh_external_reference_count"], 1)


if __name__ == "__main__":
    unittest.main()
