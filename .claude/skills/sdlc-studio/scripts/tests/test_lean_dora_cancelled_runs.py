"""BG0904: DORA does not count a cancelled or skipped CI run on main as a failed deployment.

`sprint_report._dora_rows` counted every push-triggered run whose conclusion was not success as
a failure, so a cancelled run raised the change failure rate and opened a time-to-restore
incident. Only a run that concluded failure or timed out is a failed deployment now; a
cancelled or skipped run neither fails nor restores. A page filed before the rule carries no
mark and re-derives as it was signed.

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


class DoraCancelledRunsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _dora(self, runs: list[dict], **build) -> dict:
        """The DORA rows of a page over `runs`, by key."""
        dora.lean._fixture(self.root, ended_at="2026-09-24T00:00:00Z",
                           ci_runs={"source": "gh run list", "runs": runs})
        page = dora._live("sprint_report").build_report(self.root, dora.RETRO, **build)
        rows = next(s for s in page["sections"] if s["key"] == "dora")["rows"]
        return {r["dora_key"]["value"]: r for r in rows}

    def test_a_cancelled_run_is_not_a_failed_deployment(self) -> None:
        """AC1. MUTANT: HEAD, which counts every conclusion but success as a failure, so the
        cancelled run reads a 33% change failure rate and a restore incident. The controls: a
        run that concluded failure in the same place still counts, and a page filed before the
        rule re-derives the 33% it was signed with."""
        runs = [_run(3, "14:00", "success"), _run(2, "13:00", "cancelled"),
                _run(1, "12:00", "success")]
        rows = self._dora(runs)
        self.assertEqual("0%", rows["Change failure rate"]["dora_value"]["value"])
        self.assertIn("0 failed", rows["Change failure rate"]["dora_source"]["value"])
        self.assertEqual("no restore needed", rows["Time to restore"]["dora_value"]["value"])
        self.assertIn("no push-triggered run on main concluded failure",
                      rows["Time to restore"]["dora_source"]["value"])
        failed = self._dora([runs[0], _run(2, "13:00", "failure"), runs[2]])
        self.assertEqual("33%", failed["Change failure rate"]["dora_value"]["value"])
        self.assertEqual("1h 0m", failed["Time to restore"]["dora_value"]["value"])
        before = self._dora(runs, cancelled_rule=False)
        self.assertEqual("33%", before["Change failure rate"]["dora_value"]["value"])


if __name__ == "__main__":
    unittest.main()
