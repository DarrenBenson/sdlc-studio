"""US0979: a lane brief and return open and close the unit's span (CR0605).

RPT0014 read 29 of 34 units NOT MEASURED because a unit built through `sprint lane brief` and
`sprint lane return` never passed through In Progress, so nothing opened its span. The brief now
opens the span through the transition's own rule (`run_state.record_unit_actual`) and a passing
return closes it. A brief with no return leaves the span open: the page reads it NOT MEASURED,
and the close does not measure it to the close, because the close is not when the work ended.

Every test drives `sprint.py lane` and `sprint.py close` in-process against a throwaway git
workspace with its own transcript directory, so the meter is one the test wrote and the clock
is one the test set, and derives the page through `sprint_report`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import importlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(TESTS))
import gitutil  # noqa: E402 - confined, hermetic git for fixtures

T0 = datetime(2026, 10, 2, 9, 0, tzinfo=timezone.utc)
RETRO = "RETRO0001"


def _live(name: str):
    """The module the command resolves at call time (see `test_lean_close._live`): a sibling
    suite that loads a script by path replaces the `sys.modules` entry, so a module held from
    import time is where a patch lands unread."""
    return sys.modules.get(name) or importlib.import_module(name)


def _stamp(at: datetime) -> str:
    return at.isoformat().replace("+00:00", "Z")


@contextlib.contextmanager
def _clock(at: datetime):
    """The unit clock set to `at`, on every run-state module object a caller may hold: the one
    `sprint` imported and the one `lib.run_state` names now (patched by name, LC-010)."""
    stamp = _stamp(at)
    with contextlib.ExitStack() as stack:
        stack.enter_context(unittest.mock.patch("lib.run_state._unit_clock", lambda: stamp))
        held = _live("sprint").run_state
        if held is not sys.modules.get("lib.run_state"):
            stack.enter_context(unittest.mock.patch.object(held, "_unit_clock", lambda: stamp))
        yield


class _Workspace:
    """A git workspace with two Ready stories whose criterion is executable: US0101 green
    (`file src/a.py` exists), US0102 red until `src/b.py` is written."""

    def __init__(self, d: str) -> None:
        self.root = Path(d) / "repo"
        self.transcripts = Path(d) / "transcripts"
        self.transcripts.mkdir()
        self.root.mkdir()
        self.env = {**gitutil.git_env(), _live("lib.run_state").TRANSCRIPTS_ENV:
                    str(self.transcripts)}

    def build(self, batch=("US0101", "US0102")) -> None:
        root = self.root
        (root / "src").mkdir()
        (root / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
        stories = root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        for uid, target in (("US0101", "src/a.py"), ("US0102", "src/b.py")):
            (stories / f"{uid}-x.md").write_text(
                f"# {uid}: x\n\n> **Status:** Ready\n> **Epic:** EP0001\n> **Points:** 2\n\n"
                f"## Acceptance Criteria\n\n### AC1: it holds\n\n- **Verify:** file {target}\n",
                encoding="utf-8")
        retros = root / "sdlc-studio" / "retros"
        retros.mkdir(parents=True)
        (retros / f"{RETRO}-lean.md").write_text(
            f"# RETRO-0001: lean\n\n> **Date:** 2026-10-02\n> **Batch:** {', '.join(batch)}\n\n"
            "## Delivered\n\n- US0101 - shipped\n\n## Lessons\n\n- learned a thing\n",
            encoding="utf-8")
        (retros / "_index.md").write_text(
            "# Retro Registry\n\n**Last Updated:** 2026-10-02\n\n| ID | Title | Date |\n"
            "| --- | --- | --- |\n| [RETRO-0001](RETRO0001-lean.md) | lean | 2026-10-02 |\n",
            encoding="utf-8")
        (root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
        self.git("init", "-q")
        self.commit("base")
        self.spend(1000)
        rs = _live("lib.run_state")
        rs.open_run(root, batch=list(batch), goal="g")
        rs.update(root, sprint_goal="each unit is measured over its own span",
                  sprint_goal_verdict={"verdict": "achieved", "note": "it was"},
                  plan_snapshot={"units": {uid: {
                      "planned_points": 2, "forecast_minutes": 20.0,
                      "forecast_tokens": 200_000, "added": False} for uid in batch}})

    def git(self, *argv: str) -> None:
        subprocess.run(["git", "-C", str(self.root), *argv], env=self.env, check=True,
                       capture_output=True)

    def commit(self, message: str) -> None:
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message)

    def spend(self, tokens: int) -> None:
        """One usage record on the session transcript: the meter grows by `tokens`."""
        with (self.transcripts / "session.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"message": {"model": "m", "usage": {
                "input_tokens": tokens, "output_tokens": 0}}}) + "\n")

    def sprint(self, *argv: str, at: datetime) -> tuple[int, str]:
        """`sprint.py <argv>` through its own `main`, at `at` on the unit clock."""
        out = io.StringIO()
        with _clock(at), contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = _live("sprint").main([*argv, "--root", str(self.root)])
        return rc, out.getvalue()

    def transition(self, uid: str, status: str, at: datetime) -> None:
        out = io.StringIO()
        with _clock(at), contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = _live("transition").main(["set", "--id", uid, "--status", status, "--force",
                                           "--root", str(self.root)])
        assert rc == 0, out.getvalue()

    def close(self, at: datetime) -> str:
        """`sprint.py close` with its chain stubbed green (the close fixture's own stub), the
        work committed first so the dirty-tree refusal does not fire. Returns the report id."""
        import test_lean_close as lean  # noqa: PLC0415 - the close fixture, shared
        self.commit("the work")
        with _clock(at):
            rc, out, err = lean._close(self.root)
        assert rc == 0, out + err
        return self.state()["report"]

    def state(self) -> dict:
        return _live("lib.run_state").read(self.root)

    def span(self, uid: str) -> dict:
        return (self.state().get("unit_actuals") or {}).get(uid) or {}

    def rows(self, report: str | None = None) -> dict:
        """The page's per-unit actuals, `{unit: (eu_minutes cell, eu_tokens cell)}`: derived
        from the run now, or read back from a filed `report`."""
        sr = _live("sprint_report")
        page = sr.read_report(self.root, report) if report else sr.build_report(self.root, RETRO)
        sec = next(s for s in page["sections"] if s["key"] == "estimates")
        return {r["unit_id"]["value"]: (r["eu_minutes"], r["eu_tokens"])
                for r in sec.get("unit_rows") or []}


class LaneUnitSpanTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.ws = _Workspace(self._tmp.name)
        env = unittest.mock.patch.dict(os.environ, self.ws.env, clear=True)
        env.start()
        self.addCleanup(env.stop)

    def test_a_lane_brief_and_return_measure_the_unit(self) -> None:
        """AC1. MUTANTS: HEAD, which opens no span at the brief, so US0101 reads NOT MEASURED;
        a brief that opens the span and a return that does not close it (left for the close to
        settle), so the span is still open at the page and reads NOT MEASURED; a return that
        closes the span on a BLOCKED return too, so US0102's failed lane reads 3.0 minutes."""
        ws = self.ws
        ws.build()
        rc, out = ws.sprint("lane", "brief", "--units", "US0101", "US0102", at=T0)
        self.assertEqual(0, rc, out)                      # the shipped argv: no new flag
        self.assertIs(True, ws.span("US0101").get("open"), "the brief opened no span")
        self.assertEqual(_stamp(T0), ws.span("US0101").get("started_at"))
        ws.spend(400)                                     # the lane's work, on the meter
        rc, out = ws.sprint("lane", "return", "--units", "US0101", at=T0 + timedelta(minutes=7))
        self.assertEqual(0, rc, out)
        self.assertIn("US0101: fixed", out)
        # US0102's criterion is red: the return is blocked, no new refusal, and its span stays
        # open - the lane came back without the work, so its time is not yet known.
        rc, out = ws.sprint("lane", "return", "--units", "US0102", at=T0 + timedelta(minutes=3))
        self.assertEqual(1, rc, out)
        self.assertIn("US0102: blocked", out)
        self.assertEqual((False, 7.0, 400),
                         tuple(ws.span("US0101").get(k) for k in ("open", "minutes", "tokens")))
        self.assertIs(True, ws.span("US0102").get("open"), "a blocked return closed the span")
        rows = ws.rows()
        self.assertEqual((7.0, 400), (rows["US0101"][0]["value"], rows["US0101"][1]["value"]))
        self.assertEqual("NOT MEASURED", rows["US0102"][0]["value"])
        # The unit's terminal move after a passing return finds no span open: nothing restarts
        # or doubles the measurement the return recorded.
        ws.transition("US0101", "Done", T0 + timedelta(minutes=30))
        self.assertEqual((False, 7.0, 400),
                         tuple(ws.span("US0101").get(k) for k in ("open", "minutes", "tokens")))

    def test_a_unit_already_in_progress_keeps_its_one_span(self) -> None:
        """MUTANT: a brief that restarts an open span (a second open), so a unit moved to In
        Progress at T0 and briefed at T0+3 reads 7.0 minutes instead of the 10.0 it took."""
        ws = self.ws
        ws.build()
        ws.transition("US0101", "In Progress", T0)
        rc, out = ws.sprint("lane", "brief", "--units", "US0101", at=T0 + timedelta(minutes=3))
        self.assertEqual(0, rc, out)
        self.assertEqual(_stamp(T0), ws.span("US0101").get("started_at"))
        rc, out = ws.sprint("lane", "return", "--units", "US0101",
                            at=T0 + timedelta(minutes=10))
        self.assertEqual(0, rc, out)
        self.assertEqual((False, 10.0), (ws.span("US0101")["open"], ws.span("US0101")["minutes"]))

    def test_a_brief_with_no_return_is_not_measured(self) -> None:
        """AC2. MUTANTS: HEAD, which opens no span at the brief, so there is no open span to
        find; reading an open span's running total as the unit's time (HEAD's report reads
        0.0); a derivation that closes the open span; a close that settles a lane briefed and
        never returned, so the filed page reads 20.0 minutes. Control: US0102, moved to In
        Progress by hand with no lane, is still measured to the close (BG0848)."""
        ws = self.ws
        ws.build()
        rc, out = ws.sprint("lane", "brief", "--units", "US0101", at=T0)
        self.assertEqual(0, rc, out)
        ws.transition("US0102", "In Progress", T0)
        ws.spend(400)
        rows = ws.rows()                                  # derived while the run is open
        self.assertEqual("NOT MEASURED", rows["US0101"][0]["value"])
        self.assertEqual("NOT MEASURED", rows["US0101"][1]["value"])
        self.assertIn("still open", rows["US0101"][0]["reason"])
        self.assertIs(True, ws.span("US0101").get("open"), "the derivation closed the span")
        report = ws.close(T0 + timedelta(minutes=20))
        self.assertIs(True, ws.span("US0101").get("open"), "the close closed the span")
        filed = ws.rows(report)
        self.assertEqual("NOT MEASURED", filed["US0101"][0]["value"])
        self.assertEqual("NOT MEASURED", filed["US0101"][1]["value"])
        self.assertEqual((20.0, 400), (filed["US0102"][0]["value"], filed["US0102"][1]["value"]),
                         "the control: an In Progress span with no lane is measured to the close")

    def test_the_sign_leaves_a_lane_never_returned_unmeasured(self) -> None:
        """BG0848's neighbour. A reviewed unit whose lane never returned (RPT0014's run closed
        with one, BG0839) is moved terminal by `sprint sign` over a span the close left open.
        MUTANT: let a terminal move close a span while the unit's lane is in flight, so the
        sign measures it to the sign and stamps the meter - the sealed page re-derives
        INVALIDATED on eu_minutes, eu_tokens and the run's token total."""
        import test_lean_sign as sign  # noqa: PLC0415 - BG0848's sign fixture, shared
        (Path(self._tmp.name) / "sign").mkdir()
        run = sign._SignMovesRun(str(Path(self._tmp.name) / "sign"))
        with unittest.mock.patch.dict(os.environ, run.env, clear=True):
            run.build()
            run._cli("sprint", "lane", "brief", "--units", "US0101")
            report = run.close()
            self.assertEqual({"US0101": ("NOT MEASURED", "NOT MEASURED"),
                              "BG0101": (10.0, 5000)}, run.unit_rows(report))
            run.sign(report)
            self.assertEqual("Done", run.status("US0101"), "premise: the sign moved it")
            check = run.lean._live("sprint_report").revalidate(run.root, report)
        self.assertTrue(check["valid"], check["changes"])


if __name__ == "__main__":
    unittest.main()
