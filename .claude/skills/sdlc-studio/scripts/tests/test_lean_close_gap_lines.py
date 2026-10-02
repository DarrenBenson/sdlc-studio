"""BG0908: the review-coverage step hands over its gap, never its status line or its prose.

`close_known_issues_from` turns every detail line of a failed close step into a known issue, so
a close whose only gap was one unreviewed unit listed three: the `1/2 unit(s) covered` status
line, the gap naming the unit, and the step's `The close certifies ...` prose. The step now keeps
its status line and prose out of the detail it hands over and prints them for the operator, as
the retro-extract step already does.

Each test runs the real `sprint.py close` with the review-coverage step real and every other
step stubbed green (`test_lean_close._close`), and reads the known issues off the filed page.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402 - the close fixture, shared


class CloseGapLinesTests(unittest.TestCase):
    def test_review_coverage_hands_over_only_its_gap(self) -> None:
        """AC1. MUTANT: HEAD, whose failed step carries its `covered` status line and its
        certification prose in the detail, so the page lists three review-coverage rows for
        one gap. The control: the gap itself is still handed over, naming the unit, and the
        status and prose are still printed for the operator."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            lean._fixture(root)                    # US0101 carries no independent review
            rc, out, err = lean._close(root, real=("review-coverage",))
            self.assertEqual(0, rc, out + err)
            rows = lean._known_issue_rows(root, lean._read(root)["report"])
            gaps = [r["issue_detail"] for r in rows if r["issue_id"] == "review-coverage"]
            self.assertEqual(1, len(gaps), gaps)
            self.assertIn("US0101", gaps[0])
            self.assertIn("covered by NO independent review", gaps[0])
            self.assertNotIn("unit(s) covered by an independent pass", gaps[0])
            self.assertNotIn("The close certifies", gaps[0])
            printed = out + err
            self.assertIn("0/1 unit(s) covered by an independent pass", printed)
            self.assertIn("The close certifies that a review happened", printed)


if __name__ == "__main__":
    unittest.main()
