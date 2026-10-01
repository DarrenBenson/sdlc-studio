"""BG0833: the engagement floor counts a request's decomposition as its planning pass.

A CR delivered wholly through its `Decomposed-into` children, each planned, was refused as
`unplanned` because the floor read only the CR's own criteria. `refine`'s decomposition IS the
planning pass, so a `Decomposed-into` line naming children satisfies the floor. Each test drives
the shipped `engagement_floor.py check` as a subprocess against a throwaway tree.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent

_STORY = ("# {sid}: a child\n\n> **Status:** Done\n> **Parent:** CR0001\n\n"
          "## Acceptance Criteria\n\n- [x] **AC1** Given a, when b, then c\n"
          "  - **Verify:** shell true\n")
_CR = ("# CR0001: a request\n\n> **Status:** Complete\n> **Affects:** a.py, b.py\n"
       "{decomposed}\n## Summary\n\nDelivered through its children.\n")


class EngagementDecomposedTests(unittest.TestCase):
    def _check(self, decomposed: str) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            stories = root / "sdlc-studio" / "stories"
            stories.mkdir(parents=True)
            for sid in ("US0001", "US0002"):
                (stories / f"{sid}-a-child.md").write_text(_STORY.format(sid=sid),
                                                           encoding="utf-8")
            crs = root / "sdlc-studio" / "change-requests"
            crs.mkdir(parents=True)
            (crs / "CR0001-a-request.md").write_text(_CR.format(decomposed=decomposed),
                                                     encoding="utf-8")
            return subprocess.run(
                [sys.executable, "-B", str(SCRIPTS / "engagement_floor.py"), "--root", str(root),
                 "check"], capture_output=True, text=True, check=False, timeout=120)

    def test_a_decomposed_request_passes_through_its_children(self) -> None:
        """AC1. MUTANT: HEAD, which exits 1 on the decomposed CR. MUTANT: count a
        `Decomposed-into` line whatever it holds - the control below names no child and must
        still be refused, and so must the same CR with the line removed."""
        proc = self._check("> **Decomposed-into:** US0001, US0002\n")
        out = proc.stdout + proc.stderr
        self.assertEqual(0, proc.returncode, out)
        self.assertNotIn("CR0001", out)
        for control in ("", "> **Decomposed-into:** none yet\n"):
            with self.subTest(decomposed=control):
                proc = self._check(control)
                out = proc.stdout + proc.stderr
                self.assertEqual(1, proc.returncode, out)
                self.assertIn("CR0001", out)
                self.assertIn("unplanned", out)


if __name__ == "__main__":
    unittest.main()
