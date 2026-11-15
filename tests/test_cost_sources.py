import unittest
from orderpilot.cost_sources import validate_cost_sources


class CostSourceTests(unittest.TestCase):
    def setUp(self):
        self.row = dict(name="Synthetic outbound message", kind="internal_assumption",
                        lkr_per_unit="3.50", observed_on="2026-11-16", source_url="")

    def test_assumption_never_claims_verified_price(self):
        result = validate_cost_sources([self.row], as_of="2026-11-16")
        self.assertEqual(result["verified_provider_prices"], 0)
        self.assertTrue(result["entries"][0]["requires_manual_verification"])
        self.assertEqual(result["entries"][0]["lkr_per_unit"], "3.50")

    def test_public_source_requires_https(self):
        for url in ("", "http://example.com/rates", "https://user:pass@example.com",
                    "https://example.com/has space"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_cost_sources([{**self.row, "kind": "public_price_list",
                                        "source_url": url}], as_of="2026-11-16")

    def test_future_observation_rejected(self):
        with self.assertRaises(ValueError):
            validate_cost_sources([{**self.row, "observed_on": "2026-11-17"}],
                                  as_of="2026-11-16")

    def test_duplicate_name_rejected(self):
        with self.assertRaises(ValueError):
            validate_cost_sources([self.row, self.row], as_of="2026-11-16")

    def test_invalid_prices_rejected(self):
        for price in ("-1", "NaN", "Infinity", "1e3", "1000000001", "2.2.2", 2):
            with self.subTest(price=price), self.assertRaises(ValueError):
                validate_cost_sources([{**self.row, "lkr_per_unit": price}],
                                      as_of="2026-11-16")

    def test_public_source_still_requires_verification(self):
        result = validate_cost_sources([{**self.row, "kind": "public_price_list",
            "source_url": "https://example.com/pricing", "observed_on": "2026-11-01"}],
            as_of="2026-11-16")
        self.assertEqual(result["entries"][0]["age_days"], 15)
        self.assertEqual(result["verified_provider_prices"], 0)

    def test_unknown_fields_rejected(self):
        with self.assertRaises(ValueError):
            validate_cost_sources([{**self.row, "phone": "private"}],
                                  as_of="2026-11-16")
