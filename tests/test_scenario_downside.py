"""Regression tests for non-probabilistic scenario downside screening."""
import unittest
from orderpilot.scenario_downside import screen_downside


def case(name, seconds, orders=100):
    return {
        "name": name,
        "monthly_orders": orders,
        "seconds_saved_per_order": seconds,
        "hourly_lkr": "600",
        "subscription_lkr": "100",
    }


class ScenarioDownsideTests(unittest.TestCase):
    def test_downside_count_and_spread(self):
        report = screen_downside([
            case("negative", 0), case("zero", 6), case("positive", 60)
        ])
        self.assertEqual(report["nonpositive_scenario_count"], 2)
        self.assertEqual(report["nonpositive_scenario_names"], ["negative", "zero"])
        self.assertEqual(report["worst_displayed_net_lkr"], "-100.00")
        self.assertEqual(report["best_displayed_net_lkr"], "900.00")
        self.assertEqual(report["displayed_spread_lkr"], "1000.00")
        self.assertFalse(report["all_scenarios_positive_under_assumptions"])

    def test_all_positive_and_order_preserved(self):
        report = screen_downside([case("b", 60), case("a", 120)])
        self.assertEqual(report["nonpositive_scenario_names"], [])
        self.assertTrue(report["all_scenarios_positive_under_assumptions"])
        self.assertEqual(report["scenario_count"], 2)

    def test_rejects_mismatched_volumes(self):
        with self.assertRaises(ValueError):
            screen_downside([case("a", 60), case("b", 60, orders=101)])

    def test_rejects_duplicate_names(self):
        with self.assertRaises(ValueError):
            screen_downside([case("a", 60), case("a", 30)])

    def test_rejects_single_scenario(self):
        with self.assertRaises(ValueError):
            screen_downside([case("a", 60)])

    def test_no_probability_claim(self):
        report = screen_downside([case("a", 0), case("b", 60)])
        self.assertIn("not probabilities", report["warning"])
        self.assertEqual(report["mode"], "HYPOTHETICAL_OFFLINE_DOWNSIDE_SCREEN")


if __name__ == "__main__":
    unittest.main()
