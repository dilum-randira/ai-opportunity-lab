"""Regression coverage for explicitly hypothetical scenario comparisons."""
import unittest

from orderpilot.sensitivity import compare_scenarios


def scenario(name, *, orders=100, seconds=60, subscription="100"):
    return {
        "name": name,
        "monthly_orders": orders,
        "seconds_saved_per_order": seconds,
        "hourly_lkr": "600",
        "subscription_lkr": subscription,
    }


class SensitivityTests(unittest.TestCase):
    def test_range_and_positive_flags(self):
        report = compare_scenarios([
            scenario("low", seconds=0),
            scenario("high", seconds=60),
        ])
        self.assertEqual(report["monthly_orders"], 100)
        self.assertEqual(report["displayed_net_range_lkr"],
                         {"minimum": "-100.00", "maximum": "900.00"})
        self.assertFalse(report["all_scenarios_positive_under_assumptions"])
        self.assertEqual([s["name"] for s in report["scenarios"]],
                         ["low", "high"])
        self.assertIn("Not observed savings", report["warning"])

    def test_all_positive(self):
        report = compare_scenarios([
            scenario("one", subscription="1"),
            scenario("two", subscription="2"),
        ])
        self.assertTrue(report["all_scenarios_positive_under_assumptions"])

    def test_reject_mismatched_volumes(self):
        with self.assertRaises(ValueError):
            compare_scenarios([scenario("one"), scenario("two", orders=101)])

    def test_reject_duplicate_and_invalid_names(self):
        for name in ["one", " one", "bad\nname", ""]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                compare_scenarios([scenario("one"), scenario(name)])

    def test_reject_invalid_size_and_cost(self):
        for rows in [[], [scenario("one")], [scenario(str(i)) for i in range(13)]]:
            with self.assertRaises(ValueError):
                compare_scenarios(rows)
        with self.assertRaises(ValueError):
            compare_scenarios([scenario("one"), scenario("two", subscription="-1")])

    def test_preserves_project_message_billing(self):
        a = scenario("no messages")
        b = scenario("billed messages")
        b["utility_messages_per_order"] = "1"
        b["utility_rate_lkr"] = "2"
        report = compare_scenarios([a, b])
        self.assertEqual(report["displayed_net_range_lkr"],
                         {"minimum": "700.00", "maximum": "900.00"})


if __name__ == "__main__":
    unittest.main()
