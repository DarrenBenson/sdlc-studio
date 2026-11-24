"""The close checklist's cost row reads the run as the report page does.

A run holding only its legacy `session_token_baseline` needs a closing reading of the same
meter, which the page reads from the live transcript; the row reads it the same way. A total
that re-derived a reading on an earlier counting basis says so in the row's detail.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402 - the live-module loader, shared

SOURCE = "/t/s1.jsonl"


class CloseChecklistCostPathsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "repo"
        self.root.mkdir()
        self.transcripts = Path(self._tmp.name) / "transcripts"
        self.transcripts.mkdir()
        self.rs = lean._live("lib.run_state")
        self.sr = lean._live("sprint_report")
        env = unittest.mock.patch.dict(os.environ,
                                       {self.rs.TRANSCRIPTS_ENV: str(self.transcripts)})
        env.start()
        self.addCleanup(env.stop)

    def spend(self, tokens: int) -> None:
        with (self.transcripts / "session.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"message": {"model": "m", "usage": {
                "input_tokens": tokens, "output_tokens": 0}}}) + "\n")

    def test_a_legacy_baseline_only_run_reads_as_the_page_does(self) -> None:
        """AC1. MUTANT: `_ck_cost` reads `run_token_total(metered)` with no closing reading,
        so a run holding only its legacy baseline reads 'unattributed'."""
        self.spend(1000)
        baseline = self.rs.session_tokens(self.root)
        self.assertEqual(1000, baseline["tokens"], "premise: the opening reading")
        self.spend(4000)
        run = {"run_id": "RUN-X", "session_token_baseline": {
            **baseline, "at": "2026-09-23T00:00:00Z"}}
        status, value, _ = self.sr._ck_cost({"root": self.root, "run": run})
        self.assertEqual(self.sr.ANSWERED, status)
        self.assertEqual("4,000 tokens, measured", value)

    def test_a_run_with_stamps_does_not_read_the_transcript(self) -> None:
        """The control: a run holding stamps is measured from them, whatever the live
        transcript holds, as the page does."""
        run = {"run_id": "RUN-X", "session_token_stamps": [
            {"tokens": 1000, "source": SOURCE, "at": "2026-09-23T00:00:00Z", "kind": "open"},
            {"tokens": 3000, "source": SOURCE, "at": "2026-09-23T01:00:00Z",
             "kind": "report"}]}
        self.spend(99_000)
        _, value, _ = self.sr._ck_cost({"root": self.root, "run": run})
        self.assertEqual("2,000 tokens, measured", value)

    def test_the_cost_detail_names_the_re_derivation(self) -> None:
        """AC2. MUTANT: drop `rebased` from the detail, and no other test notices."""
        basis = self.rs.METER_BASIS
        run = {"run_id": "RUN-X", "session_token_stamps": [
            {"tokens": 500, "source": SOURCE, "at": "2026-09-23T00:00:00Z", "kind": "open"},
            {"tokens": 1000, "source": SOURCE, "at": "2026-09-23T00:00:00Z",
             "kind": self.rs.REDERIVED, self.rs.REDERIVES: "2026-09-23T00:00:00Z",
             self.rs.METER: basis},
            {"tokens": 3000, "source": SOURCE, "at": "2026-09-23T01:00:00Z", "kind": "report",
             self.rs.METER: basis}]}
        total = self.rs.run_token_total(run)
        self.assertEqual(1, total["rebased"], "premise: one reading re-derived")
        _, value, detail = self.sr._ck_cost({"root": self.root, "run": run})
        self.assertEqual("2,000 tokens, measured", value)
        self.assertIn(self.rs.rebased_note(total), detail)

    def test_a_total_that_re_derived_nothing_names_no_note(self) -> None:
        """The control beside it: no re-derivation, no note."""
        run = {"run_id": "RUN-X", "session_token_stamps": [
            {"tokens": 1000, "source": SOURCE, "at": "2026-09-23T00:00:00Z", "kind": "open"},
            {"tokens": 3000, "source": SOURCE, "at": "2026-09-23T01:00:00Z",
             "kind": "report"}]}
        _, _, detail = self.sr._ck_cost({"root": self.root, "run": run})
        self.assertNotIn("earlier counting basis", detail)


if __name__ == "__main__":
    unittest.main()
