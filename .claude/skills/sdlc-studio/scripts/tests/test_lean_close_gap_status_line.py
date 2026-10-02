"""BG0894: the close hands over a failed step's failures, never its status line.

When the retro-extract step's lesson pass reports an error, the step failed with the pass's
summary line (`lessons: N hit(s) from cited REJECTs ...`) in its detail, and the close carried
every detail line as a known issue: RPT0014 listed a close gap reading
`lessons: 0 hit(s) from cited REJECTs` beside the real failure. The summary is still printed;
only the failures are handed over.

Each test runs the real `sprint.py close` with the retro-extract step real and every other
step stubbed green (`test_lean_close._close`), the lesson pass answering with one failure, and
reads the known issues off the page the close filed.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402 - the close fixture, shared

FAILURE = ("LC-005: the graduation CR could not be filed (file_finding refused: the store is "
           "read-only)")


def _pass_result() -> dict:
    """`lessons.close_pass`'s answer for a pass that hit one class and failed to file its CR."""
    return {"hits": 0, "unknown": [], "reactivated": [], "graduating": [], "graduated": [],
            "retired": [], "closed_by": {}, "errors": [FAILURE]}


class CloseGapStatusLineTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        lean._fixture(self.root)

    def _gaps(self) -> tuple[list[str], str]:
        """The retro-extract rows on the filed page, and what the close printed."""
        held = lean._live("sprint").lessons
        with unittest.mock.patch.object(held, "close_pass", lambda *a, **k: _pass_result()):
            rc, out, err = lean._close(self.root, real=("retro-extract",))
        self.assertEqual(0, rc, out + err)
        rows = lean._known_issue_rows(self.root, lean._read(self.root)["report"])
        return ([r["issue_detail"] for r in rows if r["issue_id"] == "retro-extract"],
                out + err)

    def test_only_the_failure_is_a_close_gap(self) -> None:
        """AC1. MUTANT: HEAD, which puts the pass's summary line in the failed step's detail, so
        the page lists `lessons: 0 hit(s) from cited REJECTs` as a second close gap."""
        gaps, printed = self._gaps()
        self.assertEqual([FAILURE], gaps)
        self.assertFalse(any("hit(s) from cited REJECTs" in g for g in gaps), gaps)
        self.assertIn("lessons: 0 hit(s) from cited REJECTs", printed,
                      "the summary is no longer a known issue, but the operator still sees it")

    def test_a_real_step_failure_is_still_a_close_gap(self) -> None:
        """AC2, the control. MUTANT: drop every retro-extract line from the handover (or pass
        the step), so the CR that was never filed reaches no page."""
        gaps, _printed = self._gaps()
        self.assertIn(FAILURE, gaps)


if __name__ == "__main__":
    unittest.main()
