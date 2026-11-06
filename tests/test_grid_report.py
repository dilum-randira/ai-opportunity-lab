"""Regression checks for sampled-volume summaries and reproducibility."""
import hashlib
import json
import unittest

from orderpilot.grid_report import canonical_json, report, summarize_grid


def sample():
    return {
        "workloads": [
            {"monthly_orders": 100, "service_messages_by_number": [0]},
            {"monthly_orders": 300, "service_messages_by_number": [0]},
        ],
        "subscription_prices_lkr": ["0", "5000"],
        "seconds_saved_per_order": "60",
        "hourly_lkr": "600",
    }


class GridReportTests(unittest.TestCase):
    def test_summary_uses_exact_flags_not_rounded_net(self):
        data = sample()
        data["workloads"] = [{"monthly_orders": 1, "service_messages_by_number": [0]}]
        data["subscription_prices_lkr"] = ["0"]
        data["seconds_saved_per_order"] = "0.001"
        data["hourly_lkr"] = "1"
        result = report(json.dumps(data).encode())
        cell = result["grid"]["rows"][0]["prices"][0]
        self.assertEqual(cell["net_after_messaging_lkr"], "0.00")
        self.assertTrue(cell["positive_after_messaging_under_assumptions"])
        self.assertEqual(result["summary"]["price_summaries"][0]["lowest_sampled_positive_volume"], 1)

    def test_sampled_not_interpolated(self):
        result = report(json.dumps(sample()).encode())
        summaries = {p["subscription_lkr"]: p for p in result["summary"]["price_summaries"]}
        self.assertEqual(summaries["0.00"]["lowest_sampled_positive_volume"], 100)
        self.assertIsNone(summaries["5000.00"]["lowest_sampled_positive_volume"])
        self.assertEqual(summaries["5000.00"]["highest_sampled_negative_volume"], 300)
        self.assertEqual(result["summary"]["scenario_count"], 4)

    def test_input_digest_and_canonical_json_deterministic(self):
        raw = json.dumps(sample(), separators=(",", ":")).encode()
        a = report(raw)
        b = report(raw)
        self.assertEqual(a["input_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(canonical_json(a), canonical_json(b))
        self.assertTrue(canonical_json(a).endswith("\n"))

    def test_direct_summary_rejects_duplicate_volumes(self):
        grid = {"mode": "OFFLINE_HYPOTHETICAL_GRID_NOT_CUSTOMER_VALIDATION",
                "scenario_count": 2,
                "rows": [
                    {"monthly_orders": 100, "prices": [
                        {"subscription_lkr": "0.00", "positive_after_messaging_under_assumptions": True}]},
                    {"monthly_orders": 100, "prices": [
                        {"subscription_lkr": "0.00", "positive_after_messaging_under_assumptions": False}]},
                ]}
        with self.assertRaisesRegex(ValueError, "duplicate monthly order"):
            summarize_grid(grid)

    def test_direct_summary_rejects_inconsistent_price_sets(self):
        grid = {"mode": "OFFLINE_HYPOTHETICAL_GRID_NOT_CUSTOMER_VALIDATION",
                "scenario_count": 4,
                "rows": [
                    {"monthly_orders": 100, "prices": [
                        {"subscription_lkr": "1.00", "positive_after_messaging_under_assumptions": True},
                        {"subscription_lkr": "2.00", "positive_after_messaging_under_assumptions": False}]},
                    {"monthly_orders": 200, "prices": [
                        {"subscription_lkr": "1.00", "positive_after_messaging_under_assumptions": True},
                        {"subscription_lkr": "3.00", "positive_after_messaging_under_assumptions": False}]},
                ]}
        with self.assertRaisesRegex(ValueError, "inconsistent price grid"):
            summarize_grid(grid)

    def test_direct_summary_rejects_incorrect_scenario_count(self):
        grid = {"mode": "OFFLINE_HYPOTHETICAL_GRID_NOT_CUSTOMER_VALIDATION",
                "scenario_count": 99,
                "rows": [{"monthly_orders": 100, "prices": [
                    {"subscription_lkr": "1.00", "positive_after_messaging_under_assumptions": True}]}]}
        with self.assertRaisesRegex(ValueError, "scenario count"):
            summarize_grid(grid)

    def test_reject_unbounded_direct_grids(self):
        grid = {"mode": "OFFLINE_HYPOTHETICAL_GRID_NOT_CUSTOMER_VALIDATION",
                "scenario_count": 21, "rows": [
                    {"monthly_orders": i + 1, "prices": [
                        {"subscription_lkr": "1.00", "positive_after_messaging_under_assumptions": True}]}
                    for i in range(21)]}
        with self.assertRaisesRegex(ValueError, "1..20"):
            summarize_grid(grid)
        grid["rows"] = grid["rows"][:1]
        grid["rows"][0]["prices"] = [
            {"subscription_lkr": f"{i}.00", "positive_after_messaging_under_assumptions": True}
            for i in range(11)]
        with self.assertRaisesRegex(ValueError, "1..10"):
            summarize_grid(grid)

    def test_reject_noncanonical_and_nonfinite_direct_prices(self):
        for bad in ("NaN", "Infinity", "-1.00", "1e3", "1.0", "0001.00", "100000001.00"):
            with self.subTest(price=bad):
                grid = {"mode": "OFFLINE_HYPOTHETICAL_GRID_NOT_CUSTOMER_VALIDATION",
                        "scenario_count": 1, "rows": [{"monthly_orders": 10, "prices": [
                            {"subscription_lkr": bad,
                             "positive_after_messaging_under_assumptions": True}]}]}
                with self.assertRaises(ValueError):
                    summarize_grid(grid)

    def test_reject_customer_identifiers(self):
        data = sample()
        data["customer_phone"] = "PRIVATE"
        with self.assertRaises(ValueError):
            report(json.dumps(data).encode())

    def test_reject_inconsistent_grid(self):
        grid = {"mode": "OFFLINE_HYPOTHETICAL_GRID_NOT_CUSTOMER_VALIDATION",
                "rows": [
                    {"monthly_orders": 10, "prices": [
                        {"subscription_lkr": "1.00", "positive_after_messaging_under_assumptions": True}]},
                    {"monthly_orders": 20, "prices": [
                        {"subscription_lkr": "2.00", "positive_after_messaging_under_assumptions": False}]},
                ]}
        with self.assertRaises(ValueError):
            summarize_grid(grid)

    def test_reject_wrong_grid_mode_and_boolean_outcome(self):
        with self.assertRaises(ValueError):
            summarize_grid({"mode": "OTHER", "rows": []})
        with self.assertRaises(ValueError):
            summarize_grid({"mode": "OFFLINE_HYPOTHETICAL_GRID_NOT_CUSTOMER_VALIDATION",
                            "rows": [{"monthly_orders": 1, "prices": [
                                {"subscription_lkr": "0.00",
                                 "positive_after_messaging_under_assumptions": 1}]}]})


if __name__ == "__main__":
    unittest.main()
