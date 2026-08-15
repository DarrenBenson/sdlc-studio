"""BG0529: the CLI lane test US0640 was delivered without, for `plan_review.py`.

Each of US0640, US0642, US0644 and US0645 changes a command, and every criterion any of them
carries is pinned IN-PROCESS only. That is not the same as unverified - both adversarial seats
drove each mechanism through the shipped verb during the review, and the transcripts are in the
run's record - but a hand-run transcript verifies today and pins nothing for tomorrow. It is
exactly the state `critic.py brief --tier` sat in for a whole sprint while
`brief_fingerprint(brief(...))` passed in-process and the shipped verb printed nothing.

So these drive the shipped entry point in a subprocess and assert on exit code and OUTPUT. The
wiring is the part a library test cannot exercise, which is the whole reason `verify_ac
lane-check` names a unit that changes a command and has no lane verifier.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent
REPO = DIR.parent.parent.parent.parent


def _run(script: str, *argv: str, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(DIR / script), *argv],
                          capture_output=True, text=True, cwd=str(cwd or REPO), timeout=180)


class US0640ThePlanGateKnobIsConsultedByTheCommand(unittest.TestCase):
    """US0640. `plan_review.enabled` when stated, the schema version otherwise. In-process that
    is a resolver; the lane question is whether the COMMAND that consults it changes behaviour
    when the knob moves."""

    def _ws(self, body: str) -> Path:
        d = Path(tempfile.mkdtemp(prefix="plangate_"))
        self.addCleanup(__import__("shutil").rmtree, d, ignore_errors=True)
        (d / "sdlc-studio" / "stories").mkdir(parents=True)
        (d / "sdlc-studio" / ".config.yaml").write_text(body, encoding="utf-8")
        (d / "sdlc-studio" / "stories" / "US0090-x.md").write_text(
            "# US0090: a fixture story\n\n> **Status:** Ready\n> **Points:** 3\n"
            "> **Affects:** src/thing.py\n\n## Acceptance Criteria\n\n"
            "### AC1: it works\n\n- **Then** it behaves\n- **Verify:** manual a human checks\n",
            encoding="utf-8")
        return d

    def test_the_stated_knob_beats_the_schema_version(self) -> None:
        """MUTANT: read the schema version first - a project that deliberately set
        `plan_review.enabled: false` is told its gate is on, which is the reason the stated
        value wins in the first place."""
        off = _run("plan_review.py", "check", "--id", "US0090", "--root",
                   str(self._ws("schema: 2\nplan_review:\n  enabled: false\n")))
        on = _run("plan_review.py", "check", "--id", "US0090", "--root",
                  str(self._ws("schema: 2\nplan_review:\n  enabled: true\n")))
        for proc in (off, on):
            self.assertNotIn("Traceback", (proc.stdout or "") + (proc.stderr or ""))
        self.assertNotEqual(
            (off.returncode, off.stdout.strip()), (on.returncode, on.stdout.strip()),
            "the command answers identically with the knob on and off, so it never read it")

if __name__ == "__main__":
    unittest.main()
