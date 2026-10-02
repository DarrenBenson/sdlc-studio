"""BG0910: a re-close's dry run asks the gate now, never the previous attempt's freeze.

BG0895 has the close pre-flight's checklist read pass `live_gate=True`
(`sprint._checklist_blockers`), so a re-close's `sprint close --dry-run` names the same unruled
findings the page will list. Dropping it survived every test, and a red-then-green re-close's
dry run then printed a stale `2 unruled`, reading BG0101 as undelivered from the gate the first
attempt froze.

Runs the real `sprint close` twice on BG0895's re-close fixture
(`test_lean_seal_finding_in_batch`), then the real `sprint close --dry-run`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402 - the close fixture, shared
import test_lean_seal_finding_in_batch as seal  # noqa: E402 - BG0895's re-close fixture


class PreflightLiveGateTests(unittest.TestCase):
    _close_with_checklist = seal.SealFindingInBatchTests._close_with_checklist
    _finding_rows = staticmethod(seal.SealFindingInBatchTests._finding_rows)

    def test_a_re_close_dry_run_names_only_the_page_s_findings(self) -> None:
        """AC1. MUTANT: drop `live_gate=True` from the pre-flight's checklist read, so the dry
        run reads the first attempt's frozen gate - BG0101 carried - and prints `2 unruled`
        naming BG0101 beside BG0102. The control: the close itself, run after the dry run,
        files a page listing BG0102 alone."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        run = seal._FindingRun(tmp.name, outside=True)
        env = unittest.mock.patch.dict(os.environ, run.env, clear=True)
        env.start()
        self.addCleanup(env.stop)
        run.build()
        seal._rule(run.root)                               # neither finding ruled
        seal._criterion(run, green=False)                  # attempt 1: BG0101 carried
        self._close_with_checklist(run)
        seal._criterion(run, green=True)                   # then verified and approved
        _rc, out, err = lean._close(run.root, "--dry-run", real=("checklist",))
        printed = out + err
        lines = [ln for ln in printed.splitlines() if "known-issues:" in ln]
        self.assertTrue(lines, printed)
        self.assertTrue(all("1 unruled" in ln for ln in lines), lines)
        self.assertIn("UNRULED BG0102", printed)
        self.assertNotIn("UNRULED BG0101", printed)
        page, _gaps = self._close_with_checklist(run)
        self.assertEqual(["BG0102"], list(self._finding_rows(page)))


if __name__ == "__main__":
    unittest.main()
