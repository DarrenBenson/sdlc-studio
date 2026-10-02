"""BG0899: a lane brief leaves the span of a unit already at a terminal status alone.

`sprint lane brief` opens a span for every unit it briefs, and a plain brief with no `--units`
briefs the whole batch, so a unit already Done and measured got a new open span; when that lane
never returned, the close left the span open and the page read NOT MEASURED where it had read
the measured minutes. A brief now opens a span only for a unit not yet at a terminal status.

Driven through `sprint.py lane brief` and the real `sprint.py close` (every chain step stubbed
green, `test_lean_close._close`) under a unit clock the test sets.
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


class LaneRebriefTerminalTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        lean._fixture(self.root, batch=["US0101", "US0102"], plan_snapshot={"units": {
            uid: {"planned_points": 3, "forecast_minutes": 30.0, "added": False}
            for uid in ("US0101", "US0102")}})
        stories = self.root / "sdlc-studio" / "stories"
        self.story = stories / "US0101-widget.md"
        (stories / "US0102-gadget.md").write_text(
            self.story.read_text(encoding="utf-8").replace("US0101: widget", "US0102: gadget")
            .replace("Review", "Ready"), encoding="utf-8")
        self.rs = lean._live("lib.run_state")

    def _status(self, uid: str, status: str) -> None:
        p = next((self.root / "sdlc-studio" / "stories").glob(f"{uid}-*.md"))
        text = p.read_text(encoding="utf-8")
        old = next(ln for ln in text.splitlines() if ln.startswith("> **Status:**"))
        p.write_text(text.replace(old, f"> **Status:** {status}"), encoding="utf-8")

    def _brief_the_batch(self, at: datetime) -> None:
        out = io.StringIO()
        with _clock(at), contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = lean._live("sprint").main(["lane", "brief", "--root", str(self.root)])
        self.assertEqual(0, rc, out.getvalue())

    def _span(self, uid: str) -> dict:
        return (lean._read(self.root).get(self.rs.UNIT_ACTUALS) or {}).get(uid) or {}

    def test_a_brief_leaves_a_terminal_unit_measured(self) -> None:
        """AC1. MUTANT: HEAD, which opens a span for every briefed unit whatever its status, so
        US0101's lane never returns, the close leaves the span open and the page reads NOT
        MEASURED. The control: US0102, not yet started, still has its span opened by the
        brief."""
        self._status("US0101", "In Progress")
        with _clock(T0):
            self.rs.record_unit_actual(self.root, "US0101", "In Progress", False)
        self._status("US0101", "Done")
        with _clock(T0 + timedelta(minutes=10)):
            self.rs.record_unit_actual(self.root, "US0101", "Done", True)
        self.assertEqual((10.0, False), (self._span("US0101")["minutes"],
                                         self._span("US0101")["open"]), "premise")

        self._brief_the_batch(T0 + timedelta(minutes=15))
        self.assertFalse(self._span("US0101")["open"], "the brief reopened a Done unit's span")
        self.assertTrue(self._span("US0102").get("open"), "the brief opened no span for "
                                                         "the unit it starts")

        with _clock(T0 + timedelta(minutes=20)):
            rc, out, err = lean._close(self.root)
        self.assertEqual(0, rc, out + err)
        state = lean._read(self.root)
        page = lean._live("sprint_report").read_report(self.root, state["report"])
        est = next(s for s in page["sections"] if s["key"] == "estimates")
        rows = {r["unit_id"]["value"]: r for r in est.get("unit_rows") or []}
        self.assertEqual(10.0, rows["US0101"]["eu_minutes"]["value"], rows["US0101"])
        self.assertFalse(self._span("US0101")["open"])


if __name__ == "__main__":
    unittest.main()
