import unittest
from datetime import datetime, timezone
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
from scd_type2 import Change, Version, apply_changes


def at(day):
    return datetime(2026, 1, day, tzinfo=timezone.utc)


def version(business_key, region, plan, valid_from, valid_to, is_current, source_sequence):
    return Version(
        business_key,
        region,
        plan,
        valid_from,
        valid_to,
        is_current,
        source_sequence,
        valid_from,
    )


class ScdType2Tests(unittest.TestCase):
    def test_inserts_new_key_and_closes_prior_version(self):
        initial = version("c1", "west", "basic", at(1), None, True, 1)
        change = Change("c1", at(10), 2, "east", "basic")
        result = apply_changes([initial], [change])

        self.assertEqual(len(result), 2)
        self.assertEqual((result[0].valid_to, result[0].is_current), (at(10), False))
        self.assertEqual((result[1].valid_from, result[1].is_current), (at(10), True))
        self.assertEqual(apply_changes(result, [change]), result)

    def test_replay_is_idempotent_and_unchanged_attributes_add_no_version(self):
        initial = version("c1", "west", "basic", at(1), None, True, 1)
        change = Change("c1", at(2), 2, "west", "basic")
        after_first = apply_changes([initial], [change])
        after_replay = apply_changes(after_first, [change])

        self.assertEqual(len(after_replay), 1)
        self.assertEqual(after_replay[0].source_sequence, 2)
        self.assertEqual(after_replay[0].valid_from, at(1))

    def test_rejects_conflicting_duplicate_events(self):
        changes = [
            Change("c1", at(2), 2, "east", "basic"),
            Change("c1", at(2), 2, "west", "premium"),
        ]
        with self.assertRaisesRegex(ValueError, "conflicting duplicate"):
            apply_changes([], changes)

    def test_rejects_out_of_order_change(self):
        initial = version("c1", "west", "basic", at(5), None, True, 5)
        change = Change("c1", at(4), 4, "east", "basic")
        with self.assertRaisesRegex(ValueError, "out-of-order"):
            apply_changes([initial], [change])

    def test_rejects_duplicate_current_versions(self):
        initial = version("c1", "west", "basic", at(1), None, True, 1)
        with self.assertRaisesRegex(ValueError, "multiple current"):
            apply_changes([initial, initial], [])

    def test_rejects_overlapping_existing_intervals(self):
        older = version("c1", "west", "basic", at(1), at(5), False, 1)
        newer = version("c1", "east", "basic", at(4), None, True, 2)
        with self.assertRaisesRegex(ValueError, "overlapping"):
            apply_changes([older, newer], [])

    def test_rejects_timezone_naive_changes(self):
        change = Change("c1", datetime(2026, 1, 1), 1, "west", "basic")
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            apply_changes([], [change])


if __name__ == "__main__":
    unittest.main()
