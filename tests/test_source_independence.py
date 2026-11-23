import unittest
from orderpilot.source_independence import assess_source_concentration


class SourceIndependenceTests(unittest.TestCase):
    def row(self, name, kind, host="", day="2026-11-20"):
        return {"name": name, "kind": kind, "lkr_per_unit": "2.50",
                "observed_on": day,
                "source_url": f"https://{host}/pricing" if host else ""}

    def test_same_hostname_across_kinds_requires_review(self):
        result = assess_source_concentration([
            self.row("quote", "provider_quote", "vendor.example"),
            self.row("list", "public_price_list", "vendor.example")], as_of="2026-11-24")
        self.assertEqual(result["hostnames_shared_across_quote_and_price_list"], 1)
        self.assertTrue(result["requires_independence_review"])
        self.assertEqual(result["distinct_hostname_count"], 1)

    def test_distinct_hosts_do_not_claim_verified_independence(self):
        result = assess_source_concentration([
            self.row("quote", "provider_quote", "one.example"),
            self.row("list", "public_price_list", "two.example")], as_of="2026-11-24")
        self.assertFalse(result["requires_independence_review"])
        self.assertEqual(result["verified_independent_providers"], 0)

    def test_internal_assumptions_excluded(self):
        result = assess_source_concentration([
            self.row("assumption", "internal_assumption")], as_of="2026-11-24")
        self.assertEqual(result["external_reference_count"], 0)
        self.assertEqual(result["largest_hostname_reference_count"], 0)

    def test_no_sensitive_prices_or_urls_in_output(self):
        result = assess_source_concentration([
            self.row("quote", "provider_quote", "vendor.example")], as_of="2026-11-24")
        self.assertNotIn("vendor.example", str(result))
        self.assertNotIn("2.50", str(result))

    def test_rejects_invalid_source_metadata(self):
        with self.assertRaises(ValueError):
            assess_source_concentration([
                self.row("future", "provider_quote", "vendor.example", "2026-11-25")],
                as_of="2026-11-24")


if __name__ == "__main__":
    unittest.main()
