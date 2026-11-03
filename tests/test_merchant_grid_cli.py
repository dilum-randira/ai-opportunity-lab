"""Safety and behavior checks for the offline JSON scenario CLI."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from io import StringIO

from orderpilot.merchant_grid_cli import MAX_INPUT_BYTES, main, parse_scenario, run


def scenario():
    return {
        "workloads": [
            {"monthly_orders": 100, "service_messages_by_number": [1500, 500],
             "utility_messages": 100}
        ],
        "subscription_prices_lkr": ["0", "1000"],
        "seconds_saved_per_order": "60",
        "hourly_lkr": "600",
        "service_rate_lkr": "2",
        "utility_rate_lkr": "1",
    }


class MerchantGridCliTests(unittest.TestCase):
    def test_valid_scenario_reuses_grid_without_pooling_allowance(self):
        report = run(json.dumps(scenario()).encode())
        self.assertEqual(report["scenario_count"], 2)
        self.assertEqual(report["rows"][0]["message_counts"]["service_billable"], 500)
        self.assertEqual(report["rows"][0]["platform_messaging_cost_lkr"], "1100.00")

    def test_reject_unknown_customer_identifiers_at_root_and_workload(self):
        for key in ("customer_name", "phone_number", "customer_id", "raw_message"):
            with self.subTest(key=key):
                item = scenario()
                item[key] = "sensitive"
                with self.assertRaises(ValueError):
                    run(json.dumps(item).encode())
                item = scenario()
                item["workloads"][0][key] = "sensitive"
                with self.assertRaises(ValueError):
                    run(json.dumps(item).encode())

    def test_reject_duplicate_json_keys_even_when_nested(self):
        for raw in (
            b'{"workloads": [], "workloads": []}',
            b'{"workloads": [{"monthly_orders": 1, "monthly_orders": 2}]}',
        ):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_scenario(raw)

    def test_reject_nonfinite_numbers_and_nonjson(self):
        for raw in (b'{"x": NaN}', b'{"x": Infinity}', b'{"x": -Infinity}',
                    b'[]', b'null', b'\xff', b'{}', b''):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_scenario(raw)

    def test_reject_oversized_payload(self):
        with self.assertRaises(ValueError):
            parse_scenario(b' ' * (MAX_INPUT_BYTES + 1))

    def test_decimal_fraction_retained_without_float_conversion(self):
        item = scenario()
        item["subscription_prices_lkr"] = [0.001]
        parsed = parse_scenario(json.dumps(item).encode())
        self.assertEqual(str(parsed["subscription_prices_lkr"][0]), "0.001")

    def test_cli_success_and_invalid_file_do_not_leak_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scenario.json"
            path.write_text(json.dumps(scenario()), encoding="utf-8")
            stdout, stderr = StringIO(), StringIO()
            with patch("sys.stdout", stdout), patch("sys.stderr", stderr):
                self.assertEqual(main([str(path)]), 0)
            self.assertEqual(json.loads(stdout.getvalue())["scenario_count"], 2)
            self.assertEqual(stderr.getvalue(), "")
            path.write_text('{"customer_name":"PRIVATE_PERSON"}', encoding="utf-8")
            stdout, stderr = StringIO(), StringIO()
            with patch("sys.stdout", stdout), patch("sys.stderr", stderr):
                self.assertEqual(main([str(path)]), 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertNotIn("PRIVATE_PERSON", stderr.getvalue())
            self.assertNotIn(str(path), stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
