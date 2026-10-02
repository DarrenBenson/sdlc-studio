"""BG0891: DORA time to restore pairs a failure with the next success, never an earlier one.

`gh run list` answers newest first, and the pairing walked that order as though it were
chronological, so RPT0014 paired the 16:10 failure with the 12:22 success before it and printed
-4h 20m. The runs are now ordered by when they were created, a failure is paired with the first
success created after it that concluded after it, and a failure with none reads not restored.

Each test freezes the window's CI runs on the run record, in the forge's newest-first order, and
derives the page through `sprint_report.build_report`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import importlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(TESTS))
import test_lean_close as lean  # noqa: E402 - the lean run fixture, shared

RETRO = "RETRO0001"


def _live(name: str):
    return sys.modules.get(name) or importlib.import_module(name)


def _run(rid: int, at: str, conclusion: str, event: str = "push",
         created: str | None = None) -> dict:
    """One `gh run list --json` row on main, concluded at `at` and created at `created` (or
    `at`), both HH:MM on the run's first day."""
    return {"databaseId": rid, "event": event, "conclusion": conclusion, "headBranch": "main",
            "headSha": f"{rid:07d}", "workflowName": "Lint",
            "createdAt": f"2026-09-23T{created or at}:00Z", "updatedAt": f"2026-09-23T{at}:00Z"}


class TimeToRestoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _restore(self, runs: list[dict], **build) -> dict:
        """The Time to restore row of a page over `runs`, given in the forge's own order."""
        lean._fixture(self.root, ended_at="2026-09-24T00:00:00Z",
                      ci_runs={"source": "gh run list", "runs": runs})
        page = _live("sprint_report").build_report(self.root, RETRO, **build)
        rows = next(s for s in page["sections"] if s["key"] == "dora")["rows"]
        return next(r for r in rows if r["dora_key"]["value"] == "Time to restore")

    def test_restore_pairs_a_failure_with_the_next_success(self) -> None:
        """AC1. MUTANTS: HEAD, which walks the forge's newest-first list as chronological and
        reads -4h 20m against the 12:22 success; pairing with the first success in list order
        whatever its time; measuring from the failure's creation rather than its conclusion."""
        row = self._restore([_run(3, "17:19", "success"),
                             _run(2, "16:10", "failure", created="16:02"),
                             _run(1, "12:22", "success")])
        self.assertEqual("1h 9m", row["dora_value"]["value"])
        self.assertIn("forge runs 2/3", row["dora_source"]["value"])
        self.assertFalse(str(row["dora_value"]["value"]).startswith("-"))

    def test_a_red_streak_restores_from_its_first_failure(self) -> None:
        """MUTANT: take the forge's list order as time, so the newest failure (16:40) is the
        one paired and two reds in a row read 39m instead of the 1h 9m main stayed red."""
        row = self._restore([_run(3, "17:19", "success"), _run(5, "16:40", "failure"),
                             _run(2, "16:10", "failure"), _run(1, "12:22", "success")])
        self.assertEqual("1h 9m", row["dora_value"]["value"])

    def test_a_failure_with_no_later_success_reads_not_restored(self) -> None:
        """AC2. MUTANTS: HEAD, which pairs the 16:10 failure with the 12:22 success before it;
        reading the unrestored failure as NOT MEASURED - no forge run data, though the forge
        answered. A success that is not push-triggered does not restore main."""
        row = self._restore([_run(4, "18:00", "success", event="workflow_dispatch"),
                             _run(2, "16:10", "failure"), _run(1, "12:22", "success")])
        self.assertEqual("not restored", row["dora_value"]["value"])
        self.assertIn("forge runs 2", row["dora_source"]["value"])
        self.assertIn("no push-triggered run concluded success after", row["dora_source"]["value"])

    def test_a_page_filed_before_the_fix_re_derives_its_restore(self) -> None:
        """RPT0014 was signed reading -4h 20m. MUTANTS: apply the fix when re-deriving a page
        that carries no mark of it, so the signed page reads INVALIDATED; leave the mark off a
        new page, so it re-derives under the old pairing."""
        sr = _live("sprint_report")
        runs = [_run(3, "17:19", "success"), _run(2, "16:10", "failure"),
                _run(1, "12:22", "success")]
        before = self._restore(runs, restore_rule=False)
        self.assertEqual("-4h 12m", before["dora_value"]["value"], "premise: HEAD's pairing")
        page = sr.build_report(self.root, RETRO, restore_rule=False)
        self.assertNotIn(sr.RESTORE_RULE, page)
        check = sr.revalidate(self.root, sr.file_report(self.root, page))
        self.assertTrue(check["valid"], check["changes"])
        page = sr.build_report(self.root, RETRO)
        self.assertEqual(sr.RESTORE_NEXT_SUCCESS, page.get(sr.RESTORE_RULE))
        check = sr.revalidate(self.root, sr.file_report(self.root, page))
        self.assertTrue(check["valid"], check["changes"])


if __name__ == "__main__":
    unittest.main()
