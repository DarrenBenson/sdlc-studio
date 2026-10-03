"""BG0917: a lane brief leaves the span of a bug already at Fixed alone.

BG0899 stopped a brief reopening the span of a unit at a terminal status, and was pinned by a
story at Done only, so a check against Done alone survived it. A bug's terminal statuses are
Fixed and Verified: a whole-batch brief that reopened a Fixed bug's span left the page reading
NOT MEASURED where its lane had returned 10 minutes.

Driven through `sprint.py lane brief` and `lane return` and the real `sprint.py close` (every
chain step stubbed green, `test_lean_close._close`) under a unit clock the test sets.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
import unittest.mock
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402 - the close fixture, shared

T0 = datetime(2026, 9, 23, 9, 0, tzinfo=timezone.utc)


@contextlib.contextmanager
def _clock(at: datetime):
    """The unit clock set to `at` on every run-state module object a caller may hold."""
    stamp = at.isoformat().replace("+00:00", "Z")
    with contextlib.ExitStack() as stack:
        mods = {id(m): m for m in (lean._live("lib.run_state"), lean._live("sprint").run_state)}
        for m in mods.values():
            stack.enter_context(unittest.mock.patch.object(m, "_unit_clock", lambda: stamp))
        yield


class LaneRebriefTerminalBugTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        lean._fixture(self.root, batch=["BG0101", "US0101"], plan_snapshot={"units": {
            uid: {"planned_points": 1, "forecast_minutes": 30.0, "added": False}
            for uid in ("BG0101", "US0101")}})
        bugs = self.root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True)
        self.bug = bugs / "BG0101-widget-breaks.md"
        self.bug.write_text(
            "# BG0101: widget breaks\n\n> **Status:** In Progress\n> **Severity:** Low\n"
            "> **Points:** 1\n> **Affects:** src/widget.py\n\n## Acceptance Criteria\n\n"
            "- [x] **AC1** it holds\n  - **Verify:** shell true\n", encoding="utf-8")
        self.rs = lean._live("lib.run_state")

    def _lane(self, at: datetime, *argv: str) -> None:
        out = io.StringIO()
        with _clock(at), contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = lean._live("sprint").main(["lane", *argv, "--root", str(self.root)])
        self.assertEqual(0, rc, out.getvalue())

    def _span(self, uid: str) -> dict:
        return (lean._read(self.root).get(self.rs.UNIT_ACTUALS) or {}).get(uid) or {}

    def test_a_fixed_bug_keeps_its_span(self) -> None:
        """AC1. MUTANT: a check against Done alone, which reopens the Fixed bug's span; its lane
        never returns again, the close leaves the span open and the page reads NOT MEASURED. The
        control: US0101, at Review, still has its span opened by the same brief."""
        self._lane(T0, "brief", "--units", "BG0101")
        self._lane(T0 + timedelta(minutes=10), "return", "--units", "BG0101")
        self.bug.write_text(self.bug.read_text(encoding="utf-8").replace(
            "> **Status:** In Progress", "> **Status:** Fixed"), encoding="utf-8")
        self.assertEqual((10.0, False), (self._span("BG0101").get("minutes"),
                                         self._span("BG0101").get("open")), "premise")

        self._lane(T0 + timedelta(minutes=15), "brief")
        self.assertFalse(self._span("BG0101")["open"], "the brief reopened a Fixed bug's span")
        self.assertTrue(self._span("US0101").get("open"), "the brief opened no span for "
                                                         "the unit it starts")

        with _clock(T0 + timedelta(minutes=20)):
            rc, out, err = lean._close(self.root)
        self.assertEqual(0, rc, out + err)
        state = lean._read(self.root)
        page = lean._live("sprint_report").read_report(self.root, state["report"])
        est = next(s for s in page["sections"] if s["key"] == "estimates")
        rows = {r["unit_id"]["value"]: r for r in est.get("unit_rows") or []}
        self.assertEqual(10.0, rows["BG0101"]["eu_minutes"]["value"], rows["BG0101"])


if __name__ == "__main__":
    unittest.main()
