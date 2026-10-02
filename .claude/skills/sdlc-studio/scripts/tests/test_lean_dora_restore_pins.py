"""BG0906: two of D0304's time-to-restore rules, pinned.

BG0891 ships D0304, but two of its rules were unpinned: the FIRST success created after a
failure restores the streak (a later success does not move it), and a run still in progress
neither ends a streak nor restores one. A mutant letting a later success overwrite the restore,
and one restoring on any run after a failure, both survived the suite.

Each test freezes the window's CI runs on the run record, in the forge's newest-first order, and
derives the page through `sprint_report.build_report`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_dora_time_to_restore as dora  # noqa: E402 - the DORA fixture, shared

_run = dora._run


class DoraRestorePinsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    _restore = dora.TimeToRestoreTests._restore

    def test_the_first_success_restores_and_a_running_run_ends_nothing(self) -> None:
        """AC1. MUTANTS: in `_restore_incidents`, let a later success overwrite the restoring one
        (end on any success while an incident exists, not only an open one), so the first
        window reads 1h 50m; restore on any run after a failure (drop the `success` check), so
        the in-progress run ends the second window's streak and it reads a duration."""
        first = self._restore([_run(4, "18:00", "success"), _run(3, "17:19", "success"),
                               _run(2, "16:10", "failure"), _run(1, "12:22", "success")])
        self.assertEqual("1h 9m", first["dora_value"]["value"])
        self.assertIn("forge runs 2/3", first["dora_source"]["value"])
        self._tmp.cleanup()
        self.root.mkdir(parents=True, exist_ok=True)
        second = self._restore([_run(3, "17:00", ""), _run(2, "16:10", "failure"),
                                _run(1, "12:22", "success")])
        self.assertEqual("not restored", second["dora_value"]["value"])
        self.assertIn("main went red at run 2", second["dora_source"]["value"])


if __name__ == "__main__":
    unittest.main()
