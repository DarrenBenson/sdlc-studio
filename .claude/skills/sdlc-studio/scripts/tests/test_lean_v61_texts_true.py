"""BG0933: texts the v6.1 reviews found saying what the code does not.

A goal-review fields file whose `seats` list is empty was refused naming only the `--seat`
flag, so the user of the file was pointed at a flag they had not used; and help/gate.md said a
release runs "the full suite plus the three lanes below" over a paragraph describing two.

The refusal is driven through `sprint.py goal-review record`, the shipped entry point; the lane
count is read off help/gate.md and checked against the release lanes `gate.py` registers.
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
from test_lean_goal_review_fields_keys import _sprint  # noqa: E402

SKILL = Path(__file__).resolve().parents[2]
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


class V61TextsTrueTests(unittest.TestCase):
    def test_each_text_says_what_the_code_does(self) -> None:
        """AC1. MUTANTS: HEAD's refusal "at least one --seat verdict is required", which never
        names the file's 'seats' key; and the 'three lanes' sentence. The controls: the
        same refusal with no file still names --seat, a fields file with one seat records,
        and the count is checked against the lanes gate.py registers at a release."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            doc = root / "fields.json"
            doc.write_text(json.dumps({"goal": "one page is signed", "seats": []}),
                           encoding="utf-8")
            rc, said = _sprint("goal-review", "record", "--fields-file", str(doc),
                               "--root", str(root))
            self.assertEqual(2, rc, said)
            self.assertIn("refused", said)
            self.assertIn("'seats'", said)

            rc, said = _sprint("goal-review", "record", "--goal", "one page is signed",
                               "--root", str(root))
            self.assertEqual(2, rc, said)
            self.assertIn("--seat", said)

            doc.write_text(json.dumps({"goal": "one page is signed", "seats": [
                {"seat": "qa", "achievable": "yes", "done_means": "the page is signed",
                 "one_increment": "yes"}]}), encoding="utf-8")
            rc, said = _sprint("goal-review", "record", "--fields-file", str(doc),
                               "--root", str(root))
            self.assertEqual(0, rc, said)

        gate_src = (SKILL / "scripts" / "gate.py").read_text(encoding="utf-8")
        block = re.search(r'if boundary == "release":\n((?:\s+registry\[.*\n)+)', gate_src)
        self.assertIsNotNone(block, "premise: gate.py registers its release-only lanes")
        release_lanes = set(re.findall(r'registry\["([\w-]+)"\]', block.group(1)))
        self.assertTrue(release_lanes, "premise: at least one release-only lane")

        help_text = (SKILL / "help" / "gate.md").read_text(encoding="utf-8")
        row = re.search(r"\| A \*\*release\*\* \| the full suite plus the (\w+) lanes? below",
                        help_text)
        self.assertIsNotNone(row, "the release row of the boundary table moved")
        para = next(p for p in help_text.split("\n\n") if "bind at the release boundary" in p)
        described = set(re.findall(r"`([\w-]+)`", para)) & release_lanes
        self.assertEqual(release_lanes, described,
                         "the release paragraph does not describe every release lane")
        self.assertEqual(len(described), WORDS.get(row.group(1).lower()), row.group(0))


if __name__ == "__main__":
    unittest.main()
