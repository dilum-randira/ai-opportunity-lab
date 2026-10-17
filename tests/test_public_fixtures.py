"""Checks that committed public sample data follows strict example-only schemas.

Not a general secret scanner; maintainers must separately review every addition.
"""
import csv
import json
import unittest
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("baseline_seconds", "assisted_seconds", "baseline_errors", "assisted_errors")
FORBIDDEN_KEYS = {"customer_name", "customer_email", "phone_number", "email", "address",
                  "api_key", "password", "access_token", "whatsapp_number"}


def nested_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key.lower()
            yield from nested_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from nested_keys(item)


class PublicFixtureTests(unittest.TestCase):
    def test_committed_timing_examples_are_numeric_only(self):
        samples = list((ROOT / "examples").glob("*.csv"))
        self.assertTrue(samples, "An anonymized synthetic timing sample must be present")
        for path in samples:
            with self.subTest(path=path.name), path.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream, restkey="_extra")
                self.assertEqual(tuple(reader.fieldnames or ()), FIELDS)
                for row in reader:
                    self.assertNotIn("_extra", row)
                    for field in FIELDS:
                        try:
                            value = Decimal(row[field])
                        except (InvalidOperation, TypeError, ValueError) as exc:
                            self.fail(f"{path.name} has nonnumeric content: {exc}")
                        self.assertTrue(value.is_finite() and value >= 0)

    def test_public_json_examples_omit_customer_or_secret_fields(self):
        samples = list((ROOT / "examples").glob("*.json"))
        self.assertTrue(samples)
        for path in samples:
            with self.subTest(path=path.name):
                parsed = json.loads(path.read_text(encoding="utf-8"))
                self.assertFalse(set(nested_keys(parsed)) & FORBIDDEN_KEYS)


if __name__ == "__main__":
    unittest.main()
