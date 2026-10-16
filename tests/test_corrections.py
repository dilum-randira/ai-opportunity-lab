"""Offline audited corrections: approvals remain human-only, versions are durable."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from orderpilot.corrections import history, replace_items
from orderpilot.queue import OrderQueue

CATALOG = {"NUT250": "1250.00", "NUT500": "2400.00"}


class CorrectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "orders.sqlite3"
        self.queue = OrderQueue(self.db)
        self.addCleanup(lambda: self.queue.close())
        self.queue.ingest([{"id": "m1", "text": "NUT250 x 2; unknown stuff"}], CATALOG)

    def correct(self, items=None, **kwargs):
        return replace_items(self.queue, "m1", items if items is not None else [{"sku": "NUT500", "quantity": 1}],
                             CATALOG, expected_version=kwargs.get("version", 0),
                             note=kwargs.get("note", "checked SKU with merchant"))

    def test_correction_requires_separate_approval(self):
        self.assertEqual(self.queue.list_orders()[0]["parse_status"], "needs_review")
        result = self.correct()
        self.assertEqual(result["version"], 1)
        self.assertEqual(result["action"], "corrected_not_approved")
        stored = self.queue.list_orders()[0]
        self.assertEqual(stored["review_state"], "pending")
        self.assertEqual(stored["parse_status"], "ready_for_review")
        self.assertEqual(stored["draft"]["total"], "2400.00")
        self.queue.review("m1", "approve")
        self.assertEqual(self.queue.list_orders("approved")[0]["review_state"], "approved")

    def test_original_and_corrected_versions_are_preserved(self):
        self.correct()
        records = history(self.queue, "m1")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["before"]["status"], "needs_review")
        self.assertEqual(records[0]["after"]["total"], "2400.00")
        self.assertEqual(records[0]["version"], 1)

    def test_versions_survive_restart(self):
        self.correct()
        self.queue.close()
        self.queue = OrderQueue(self.db)
        self.correct([{"sku": "NUT250", "quantity": 3}], version=1)
        self.assertEqual([e["version"] for e in history(self.queue, "m1")], [1, 2])
        self.assertEqual(self.queue.list_orders()[0]["draft"]["total"], "3750.00")

    def test_stale_version_rolls_back(self):
        self.correct()
        with self.assertRaisesRegex(ValueError, "stale version"):
            self.correct(version=0)
        self.assertEqual(len(history(self.queue, "m1")), 1)

    def test_cannot_correct_approved_or_rejected(self):
        self.correct()
        self.queue.review("m1", "approve")
        with self.assertRaisesRegex(ValueError, "only pending"):
            self.correct(version=1)
        self.assertEqual(len(history(self.queue, "m1")), 1)

    def test_unknown_sku_is_rejected_atomically(self):
        with self.assertRaisesRegex(ValueError, "replacement failed"):
            self.correct([{"sku": "MISSING", "quantity": 1}])
        self.assertEqual(self.queue.list_orders()[0]["parse_status"], "needs_review")
        self.assertEqual(history(self.queue, "m1"), [])

    def test_quantity_and_shape_validation(self):
        for items in ([{"sku": "NUT250", "quantity": True}],
                      [{"sku": "NUT250", "quantity": -1}],
                      [{"sku": "NUT250", "quantity": 1.5}],
                      [{"sku": "NUT250", "quantity": 1, "price": "0"}],
                      [{"sku": "DROP TABLE", "quantity": 1}], [],
                      [{"sku": "NUT250", "quantity": 1001}]):
            with self.subTest(items=items), self.assertRaises(ValueError):
                self.correct(items)
        self.assertEqual(history(self.queue, "m1"), [])

    def test_version_and_note_validation(self):
        for version in (-1, True, "0"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                self.correct(version=version)
        for note in ("", "   ", "x" * 241):
            with self.subTest(note=note), self.assertRaises(ValueError):
                self.correct(note=note)

    def test_message_fingerprint_unchanged(self):
        digest = self.queue.connection.execute("SELECT message_digest FROM order_drafts WHERE source_id='m1'").fetchone()[0]
        self.correct()
        self.assertEqual(digest, self.queue.connection.execute(
            "SELECT message_digest FROM order_drafts WHERE source_id='m1'").fetchone()[0])
        self.assertEqual(self.queue.ingest([{"id": "m1", "text": "NUT250 x 2; unknown stuff"}], CATALOG)[0]["result"], "duplicate")

    def test_noop_correction_rejected(self):
        self.correct()
        with self.assertRaisesRegex(ValueError, "no actual"):
            self.correct(version=1)
        self.assertEqual(len(history(self.queue, "m1")), 1)

    def test_cli_correction_and_history(self):
        catalog = Path(self.tmp.name) / "catalog.json"
        items = Path(self.tmp.name) / "items.json"
        catalog.write_text(json.dumps(CATALOG))
        items.write_text(json.dumps([{"sku": "NUT250", "quantity": 4}]))
        root = Path(__file__).resolve().parents[1]
        cmd = [sys.executable, "-m", "orderpilot.correction_cli", "--db", str(self.db)]
        corrected = subprocess.run(cmd + ["correct", "--id", "m1", "--items", str(items),
                                     "--catalog", str(catalog), "--expected-version", "0",
                                     "--note", "corrected line items"], cwd=root, capture_output=True, text=True)
        self.assertEqual(corrected.returncode, 0, corrected.stderr)
        self.assertEqual(json.loads(corrected.stdout)["result"]["draft"]["total"], "5000.00")
        audited = subprocess.run(cmd + ["history", "--id", "m1"], cwd=root, capture_output=True, text=True)
        self.assertEqual(audited.returncode, 0, audited.stderr)
        self.assertEqual(len(json.loads(audited.stdout)["result"]), 1)


if __name__ == "__main__":
    unittest.main()
