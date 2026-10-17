"""Subprocess checks prove the public CLI can run without network or credentials."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CMD = [sys.executable, "-m", "orderpilot.economics_cli", "--orders", "520",
       "--seconds-saved", "62", "--hourly-lkr", "400", "--subscription-lkr", "3500"]


class EconomicsCLITests(unittest.TestCase):
    def test_reproduce_costly_messaging_scenario(self):
        cmd = CMD + ["--service-messages-per-order", "2", "--service-rate-lkr", "3",
                     "--free-service-messages", "1000", "--utility-messages-per-order", "1",
                     "--utility-rate-lkr", "4"]
        response = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(response.returncode, 0, response.stderr)
        result = json.loads(response.stdout)
        self.assertEqual(result["messages"]["service_billable"], 40)
        self.assertEqual(result["monthly_lkr"]["messaging"], "2200.00")
        self.assertEqual(result["monthly_lkr"]["net_value"], "-2117.78")

    def test_no_paid_messaging_scenario(self):
        response = subprocess.run(CMD, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(response.returncode, 0, response.stderr)
        self.assertEqual(json.loads(response.stdout)["monthly_lkr"]["net_value"], "82.22")

    def test_bad_rate_exits_without_traceback(self):
        response = subprocess.run(CMD + ["--service-rate-lkr", "NaN"],
                                  cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(response.returncode, 2)
        self.assertIn("Invalid hypothetical scenario", response.stderr)
        self.assertNotIn("Traceback", response.stderr)


if __name__ == "__main__":
    unittest.main()
