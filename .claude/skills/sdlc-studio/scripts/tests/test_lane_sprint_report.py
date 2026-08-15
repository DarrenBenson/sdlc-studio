"""BG0529: the CLI lane test US0645 was delivered without, for `sprint_report.py`.

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


class US0645EveryFigureIsReadBackFromARecord(unittest.TestCase):
    """US0645. The operator summary must render from records rather than from figures computed
    in the same breath, and an absent record must SAY it is absent rather than print a zero."""

    def test_an_absent_record_is_NAMED_absent_rather_than_rendered_as_a_figure(self) -> None:
        """MUTANT: default a missing record to 0 or "" - the page renders a confident zero, and
        a dict-level test that never asks what was PRINTED stays green.

        The first cut of this asserted only that something printed and no traceback appeared,
        which no plausible change could have failed. The claim is about the WORDS."""
        d = Path(tempfile.mkdtemp(prefix="opsummary_"))
        self.addCleanup(__import__("shutil").rmtree, d, ignore_errors=True)
        (d / "sdlc-studio" / "retros").mkdir(parents=True)
        (d / "sdlc-studio" / "retros" / "RETRO0001-x.md").write_text(
            "# RETRO0001: a fixture retro\n\n> **Date:** 2026-02-01\n> **Run:** RUN-A\n"
            "> **Batch:** BG0001\n\n## What happened\n\nA fixture.\n", encoding="utf-8")
        proc = _run("sprint_report.py", "--root", str(d),
                    "operator-summary", "--id", "RETRO0001")
        self.assertEqual(0, proc.returncode, proc.stderr[-300:])
        out = proc.stdout
        self.assertNotIn("Traceback", out + proc.stderr)
        # Each of these is a figure the summary could have invented. It says so instead.
        for phrase in ("none recorded", "unjudged", "UNMEASURED"):
            self.assertIn(phrase, out,
                          f"an absent record rendered without saying so - expected {phrase!r} "
                          f"in:\n{out[:400]}")
        # ...and a zero is never printed for a cost nobody measured.
        self.assertNotIn("Cost: 0", out, "an unmeasured cost was rendered as a zero")

if __name__ == "__main__":
    unittest.main()
