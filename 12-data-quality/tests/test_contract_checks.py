import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from contract_checks import Contract, Violation, validate_rows


class ContractCheckTests(unittest.TestCase):
    def test_reports_missing_domain_and_duplicate_keys(self):
        contract = Contract(
            required_fields=("order_id", "status"),
            unique_key="order_id",
            allowed_values={"status": frozenset({"new", "complete"})},
        )
        rows = [
            {"order_id": "o1", "status": "new"},
            {"order_id": "o1", "status": "unknown"},
            {"order_id": "", "status": None},
        ]

        self.assertEqual(
            validate_rows(rows, contract),
            [
                Violation(2, "allowed_values", "status"),
                Violation(2, "unique", "order_id"),
                Violation(3, "required", "order_id"),
                Violation(3, "required", "status"),
            ],
        )

    def test_does_not_include_row_values_in_violations(self):
        violations = validate_rows(
            [{"email": "private@example.invalid"}],
            Contract(required_fields=("order_id",)),
        )

        self.assertEqual(violations, [Violation(1, "required", "order_id")])
        self.assertNotIn("private@example.invalid", repr(violations))

    def test_unexpected_unhashable_domain_value_is_reported(self):
        violations = validate_rows(
            [{"status": ["not", "a", "scalar"]}],
            Contract(
                required_fields=("status",),
                allowed_values={"status": frozenset({"new"})},
            ),
        )

        self.assertEqual(violations, [Violation(1, "allowed_values", "status")])


if __name__ == "__main__":
    unittest.main()
