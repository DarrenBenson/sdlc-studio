"""`sprint_report.py build --run RUN-x` renders RUN-x's page (BG1010).

`cmd_build` resolved the named run only to decide whether `--write` is refused, then built the
page with no `run_id`, so `build_report` read the live run instead. With another run live, the
preview showed that run's figures under the named run's retro; in a clean clone, which holds no
live record, it refused with "no run record names a run". The named run's record is the one
the close and `sprint sign` file under `sdlc-studio/reports/runs/`, which a clone holds once it
is committed.
"""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import sprint_report as sr  # noqa: E402
from lib import run_state  # noqa: E402
import test_sprint_report as tsr  # noqa: E402 - the fixture run lives beside it

OLDER_RUN = "RUN-01M0OLDR"
OLDER_GOAL = "The older run's own goal: its page reads its record, never the live run's."


def _goal(report: dict) -> dict:
    return {s["key"]: s for s in report["sections"]}["goal"]["figures"]


class BuildNamedRunTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        # The live run is the fixture's; the older run's tracked record differs from it in
        # its id, its goal and its window (2.0h against the live run's 8.0h).
        tsr.fixture_run(self.root)
        live = json.loads(run_state.path(self.root).read_text(encoding="utf-8"))
        older = dict(live, run_id=OLDER_RUN, goal=OLDER_GOAL, sprint_goal=OLDER_GOAL,
                     started_at="2026-09-01T05:00:00Z", ended_at="2026-09-01T07:00:00Z")
        self.tracked = run_state.tracked_path(self.root, OLDER_RUN)
        self.tracked.parent.mkdir(parents=True, exist_ok=True)
        self.tracked.write_text(json.dumps(older, indent=2), encoding="utf-8")

    def _build(self, *extra: str) -> dict:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sr.main(["--root", str(self.root), "build", *extra, "--format", "json"])
        self.assertEqual(rc, 0, err.getvalue())
        return json.loads(out.getvalue())

    def _assert_older(self, report: dict) -> None:
        goal = _goal(report)
        self.assertEqual(report["run_id"], OLDER_RUN)
        self.assertEqual(goal["run_id"]["value"], OLDER_RUN)
        self.assertEqual(goal["sprint_goal"]["value"], OLDER_GOAL)
        self.assertEqual(goal["duration_hours"]["value"], "2.0h")
        self.assertEqual(goal["run_id"]["source"],
                         self.tracked.relative_to(self.root).as_posix(),
                         "the named run's figures are not sourced to its committed record")

    def test_build_renders_the_named_run(self) -> None:
        """AC1. MUTANT: drop `run_id=` from `cmd_build`'s `build_report` call; the page is then
        the live run's with another run live, and refused in a clean clone."""
        # Another run is live: the named run's page, not the live one's.
        self._assert_older(self._build("--run", OLDER_RUN, "--id", tsr.FIX_RETRO))
        # Positive control: unnamed, and named as the live run, the live record is still the
        # one reported, as `_run_state_for` resolves it, over a stale tracked copy of that run.
        stale = json.loads(run_state.path(self.root).read_text(encoding="utf-8"))
        run_state.tracked_path(self.root, tsr.FIX_RUN).write_text(
            json.dumps(dict(stale, goal="stale", sprint_goal="stale")), encoding="utf-8")
        for args in ((), ("--run", tsr.FIX_RUN)):
            with self.subTest(args=args):
                rep = self._build(*args, "--id", tsr.FIX_RETRO)
                self.assertEqual(_goal(rep)["run_id"]["value"], tsr.FIX_RUN)
                self.assertEqual(_goal(rep)["sprint_goal"]["value"], tsr.FIX_GOAL)
                self.assertEqual(_goal(rep)["run_id"]["source"],
                                 run_state.path(self.root).relative_to(self.root).as_posix(),
                                 "the live run's page is not sourced to the live record")
        # A clean clone: no `.local`, so no live record; only the tracked one.
        shutil.rmtree(self.root / "sdlc-studio" / ".local")
        self._assert_older(self._build("--run", OLDER_RUN, "--id", tsr.FIX_RETRO))


if __name__ == "__main__":
    unittest.main()
