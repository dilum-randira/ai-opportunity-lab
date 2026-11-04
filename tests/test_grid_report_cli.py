"""CLI integration checks without network, credentials, or merchant records."""
import json
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from orderpilot.grid_report_cli import main


class GridReportCliTests(unittest.TestCase):
    def test_success_and_redacted_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scenario.json"
            scenario = {
                "workloads": [{"monthly_orders": 100, "service_messages_by_number": [0]}],
                "subscription_prices_lkr": ["0"],
                "seconds_saved_per_order": "60",
                "hourly_lkr": "600",
            }
            path.write_text(json.dumps(scenario), encoding="utf-8")
            stdout, stderr = StringIO(), StringIO()
            with patch("sys.stdout", stdout), patch("sys.stderr", stderr):
                self.assertEqual(main([str(path)]), 0)
            output = json.loads(stdout.getvalue())
            self.assertEqual(output["summary"]["scenario_count"], 1)
            self.assertEqual(stderr.getvalue(), "")

            path.write_text('{"customer_name":"PRIVATE_PERSON"}', encoding="utf-8")
            stdout, stderr = StringIO(), StringIO()
            with patch("sys.stdout", stdout), patch("sys.stderr", stderr):
                self.assertEqual(main([str(path)]), 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertNotIn("PRIVATE_PERSON", stderr.getvalue())
            self.assertNotIn(str(path), stderr.getvalue())

    def test_missing_file_does_not_echo_path(self):
        stdout, stderr = StringIO(), StringIO()
        with patch("sys.stdout", stdout), patch("sys.stderr", stderr):
            self.assertEqual(main(["/private/secret-merchant-file.json"]), 2)
        self.assertNotIn("secret-merchant", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
