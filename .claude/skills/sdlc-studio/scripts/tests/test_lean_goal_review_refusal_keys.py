"""BG0921: the goal-review fields-file refusal names the keys the help names.

BG0914 made the `--fields-file` help key each seat "seat", "achievable", "done_means" and
"one_increment", but the refusal for an incomplete seat still said a verdict needs `role`, the
flag form's word, which is the key confusion the help fix removed. The refusal now names the
keys the code reads, taken here from the help's own list.

Driven through `sprint.py goal-review`, the shipped entry point.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_lean_goal_review_fields_keys import _fields_file_help, _sprint  # noqa: E402

GOAL = "the close finishes in one pass"


def _required_keys() -> list[str]:
    """The required seat keys, read from the help's `keyed ..., with ... optional` list."""
    rc, text = _sprint("goal-review", "--help")
    assert rc == 0, text
    m = re.search(r"keyed (.*?), with ", _fields_file_help(text))
    assert m, text
    return re.findall(r'"(\w+)"', m.group(1))


class GoalReviewRefusalKeysTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "sdlc-studio" / ".local").mkdir(parents=True)
        self.keys = _required_keys()
        self.assertEqual("seat", self.keys[0], f"premise: the help keys the seat 'seat': {self.keys}")
        self.full = {"seat": "qa", "achievable": "yes", "done_means": "one page is signed",
                     "one_increment": "yes"}
        self.assertEqual(sorted(self.keys), sorted(self.full), "premise: the help's list")

    def _record(self, seat: dict) -> tuple[int, str]:
        doc = self.root / "fields.json"
        doc.write_text(json.dumps({"goal": GOAL, "seats": [seat]}), encoding="utf-8")
        return _sprint("goal-review", "record", "--fields-file", str(doc),
                       "--root", str(self.root))

    def test_the_refusal_names_the_seat_key(self) -> None:
        """AC1. MUTANT: HEAD's two messages - "a verdict needs role, achievable, ..." for a
        missing answer and "has no 'seat' role" for a missing name - each names `role`. The
        missing `achievable` case names that key and every key the help lists; the control is a
        complete seat, which still records."""
        for missing in ("seat", "achievable"):
            with self.subTest(missing=missing):
                seat = {k: v for k, v in self.full.items() if k != missing}
                rc, said = self._record(seat)
                self.assertEqual(2, rc, said)
                self.assertIn("refused", said)
                self.assertRegex(said, rf"'{missing}'", said)
                self.assertNotRegex(said, r"\brole\b", said)
        rc, said = self._record({k: v for k, v in self.full.items() if k != "achievable"})
        for key in self.keys:
            with self.subTest(named=key):
                # Quoted, as the refusal writes a key, so the prose word "seat" is not it.
                self.assertIn(f"'{key}'", said)

        rc, said = self._record(self.full)
        self.assertEqual(0, rc, said)
        rc, shown = _sprint("goal-review", "show", "--root", str(self.root))
        self.assertEqual(0, rc, shown)
        self.assertIn("one page is signed", shown)


if __name__ == "__main__":
    unittest.main()
