import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))
from pipeline import parse_order, read_orders, run  # noqa: E402


class PipelineTests(unittest.TestCase):
    def test_parse_order_accepts_decimal_and_iso_date(self):
        order, error = parse_order({"order_id": "x", "order_date": "2026-01-02", "amount": "1.20"}, 2)
        self.assertIsNone(error)
        assert order is not None
        self.assertEqual(str(order.amount), "1.20")

    def test_parse_order_rejects_invalid_values(self):
        order, error = parse_order({"order_id": "x", "order_date": "bad", "amount": "1"}, 9)
        self.assertIsNone(order)
        assert error is not None
        self.assertEqual(error.line_number, 9)

    def test_sample_has_expected_accepted_and_rejected_counts(self):
        accepted, rejected = read_orders(PROJECT / "sample_data" / "orders.csv")
        self.assertEqual((len(accepted), len(rejected)), (3, 2))

    def test_aggregate_and_publish(self):
        with tempfile.TemporaryDirectory() as temp:
            accepted, rejected = run(PROJECT / "sample_data" / "orders.csv", Path(temp))
            self.assertEqual((accepted, rejected), (3, 2))
            output = (Path(temp) / "daily_summary.csv").read_text(encoding="utf-8")
            self.assertIn("2026-09-01,2,40.00", output)


if __name__ == "__main__":
    unittest.main()
