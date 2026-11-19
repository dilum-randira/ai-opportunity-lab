import unittest

from orderpilot.cost_checklist import build_cost_review_checklist


class CostChecklistTests(unittest.TestCase):
    def row(self, name, kind, observed):
        return {
            "name": name,
            "kind": kind,
            "lkr_per_unit": "99.99",
            "observed_on": observed,
            "source_url": "" if kind == "internal_assumption"
                          else "https://example.org/pricing",
        }

    def test_priorities_and_kind_specific_tasks(self):
        report = build_cost_review_checklist([
            self.row("recent", "public_price_list", "2026-11-19"),
            self.row("old", "provider_quote", "2026-09-01"),
            self.row("assumption", "internal_assumption", "2026-11-18"),
        ], as_of="2026-11-20")
        self.assertEqual([i["name"] for i in report["items"]],
                         ["assumption", "old", "recent"])
        self.assertEqual([i["priority"] for i in report["items"]], [1, 2, 3])
        self.assertIn("fresh dated", report["items"][1]["tasks"][0]["description"])
        self.assertIn("negotiated", str(report["items"][1]["tasks"]))
        self.assertIn("region", str(report["items"][2]["tasks"]))

    def test_never_claims_verification(self):
        report = build_cost_review_checklist(
            [self.row("sample", "public_price_list", "2026-11-20")],
            as_of="2026-11-20")
        self.assertEqual(report["verified_provider_prices"], 0)
        self.assertFalse(report["ready_for_commercial_pricing_claims"])
        self.assertEqual(report["items"][0]["verification_status"], "unverified")
        self.assertTrue(all(task["status"] == "pending"
                            for task in report["items"][0]["tasks"]))

    def test_excludes_unverified_amounts_and_urls(self):
        report = build_cost_review_checklist(
            [self.row("sample", "provider_quote", "2026-11-19")],
            as_of="2026-11-20")
        self.assertNotIn("99.99", str(report))
        self.assertNotIn("https://", str(report))
        self.assertNotIn("lkr_per_unit", str(report))

    def test_invalid_rows_and_threshold_rejected(self):
        with self.assertRaises(ValueError):
            build_cost_review_checklist([], as_of="2026-11-20")
        with self.assertRaises(ValueError):
            build_cost_review_checklist(
                [self.row("future", "provider_quote", "2026-11-21")],
                as_of="2026-11-20")
        with self.assertRaises(ValueError):
            build_cost_review_checklist(
                [self.row("sample", "internal_assumption", "2026-11-19")],
                as_of="2026-11-20", max_age_days=True)


if __name__ == "__main__":
    unittest.main()
