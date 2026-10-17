"""Integration tests for multi-volume unit-economics comparisons."""
import json
import subprocess
import sys
import unittest
from pathlib import Path
from orderpilot.scenario_compare import compare


class ScenarioComparisonTests(unittest.TestCase):
    def test_paid_messaging_worse_under_positive_unit_rates(self):
        output = compare(volumes=[200, 520, 1000], seconds_saved="62", hourly_lkr="400",
                         subscription_lkr="3500", service_rate_lkr="3", free_messages=1000,
                         utility_rate_lkr="4")
        self.assertEqual([x["orders"] for x in output["scenarios"]], [200, 520, 1000])
        row = output["scenarios"][1]
        self.assertEqual(row["paid_platform_net_lkr"], "-2117.78")
        self.assertEqual(row["no_paid_messaging_net_lkr"], "82.22")

    def test_zero_rates_mean_same_result(self):
        row = compare(volumes=[120], seconds_saved="45", hourly_lkr="600",
                      subscription_lkr="1500")["scenarios"][0]
        self.assertEqual(row["paid_platform_net_lkr"], row["no_paid_messaging_net_lkr"])

    def test_invalid_volumes_do_not_create_report(self):
        args = dict(seconds_saved="10", hourly_lkr="200", subscription_lkr="100")
        for volumes in ([], [0], [10, 10], [True], list(range(1, 22))):
            with self.subTest(volumes=volumes), self.assertRaises(ValueError):
                compare(volumes=volumes, **args)

    def test_cli_works_with_multiple_volumes(self):
        root = Path(__file__).resolve().parents[1]
        run = subprocess.run([sys.executable, "-m", "orderpilot.scenario_compare",
                              "--volumes", "100", "520", "1000", "--seconds-saved", "62",
                              "--hourly-lkr", "400", "--subscription-lkr", "3500"],
                             cwd=root, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(len(json.loads(run.stdout)["scenarios"]), 3)


if __name__ == "__main__":
    unittest.main()
