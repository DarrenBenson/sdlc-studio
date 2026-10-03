"""BG0930: transition.py reports no spent appetite against a run that is already signed.

`_report_appetite` read the appetite of whatever run the state file held, so in a workspace
whose last run was signed with its appetite spent, every later `transition.py set` warned
APPETITE SPENT naming a run that is over. A sealed run has no next unit for the ceiling to
stop, so the appetite is read only for a run that is not sealed; an open run still warns.

Driven through `transition.py set`, the shipped entry point, in a subprocess.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/transition.py
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "transition.py"


class AppetiteSealedRunTests(unittest.TestCase):
    def _ws(self, outcome: str, **extra) -> Path:
        d = Path(tempfile.mkdtemp(prefix="appetite_sealed_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "sdlc-studio" / "bugs").mkdir(parents=True)
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        for uid in ("BG9100", "BG9101"):
            (d / "sdlc-studio" / "bugs" / f"{uid}-x.md").write_text(
                f"# {uid}: a fixture bug\n\n> **Status:** Open\n> **Severity:** Medium\n"
                f"> **Points:** 2\n> **Verification depth:** functional\n> **Affects:** f.py\n\n"
                f"## Acceptance Criteria\n\n"
                f"- [x] **AC1** Given a thing, when it happens, then it works.\n"
                f"  - **Verify:** manual a human checks it\n", encoding="utf-8")
        state = {"schema": 1, "run_id": "RUN-SIGNED", "started_at": "2026-08-14T00:00:00Z",
                 "ended_at": None, "outcome": outcome, "goal": "x",
                 # The run's own unit is not the one moved: a sealed run refuses to move its
                 # batch, and the warning was printed on a unit outside it.
                 "batch": ["BG9100"], "plan": {},
                 "appetite": {"units": 0, "minutes": 1.0, "standing_units": 64,
                              "standing_minutes": 960.0, "over_appetite": False}, **extra}
        (d / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps(state), encoding="utf-8")
        return d

    def _set(self, root: Path, uid: str) -> str:
        proc = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "set", "--root", str(root),
             "--id", uid, "--status", "Fixed"],
            capture_output=True, text=True, timeout=120)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        return (proc.stdout or "") + (proc.stderr or "")

    def test_a_signed_run_spends_no_appetite(self) -> None:
        """AC1. MUTANT: HEAD's `_report_appetite`, which reads the appetite of a run whatever
        its outcome - the signed run, its one-minute appetite long spent, is warned about when
        a unit outside its batch moves. The control the criterion names: the same workspace
        with the run open still warns, so a mutant that never warns fails it."""
        signed = self._ws("goal-reached", ended_at="2026-08-14T02:00:00Z",
                          signature={"principal": "Darren", "report": "RPT0001"})
        said = self._set(signed, "BG9101")
        self.assertNotIn("APPETITE SPENT", said, said)

        running = self._ws("running")
        said = self._set(running, "BG9101")
        self.assertIn("APPETITE SPENT", said, said)
        self.assertIn("RUN-SIGNED", said)


if __name__ == "__main__":
    unittest.main()
