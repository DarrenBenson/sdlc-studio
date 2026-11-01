"""BG1137: of two batch rows for one unit on one date, the closing-review fold reads the later.

`sprint_report._verdict_entries` keys each frozen batch row on `(date, 0, append index)`, and
`_ck_closing_review` takes the last entry per unit as that unit's verdict. The committed ledger's
Date cells carry a day and no time, so on a date tie only the order the rows were appended in
says which came second. These tests write two rows for one unit on one day, in both orders, and read the
closing-review row from `sprint_report.checklist`, the function the `checklist` command prints.

Mutant both tests must fail on: the batch-row tiebreak reversed, `(date, 0, -i)` for
`(date, 0, i)`, so the earlier-appended row decides.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling helpers (loader)

import loader  # noqa: E402 - the canonical way to import a script under test

sr = loader.load_script("sprint_report")

UNIT = "US0001"
RETRO = f"""# RETRO-9100: a sprint

> **Batch:** {UNIT}

## Delivered
- shipped
"""
#: Inside the frozen ledger's licence (`critic.REPAIR_VERB_RETIRED` is 2026-09-26): a row dated
#: on or after it counts for nothing, and the approved case below would then read `none
#: recorded`, so that case is the control that the rows were read at all.
DAY = "2026-09-16"


class SameDayBatchRowsTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        sd = self.root / "sdlc-studio"
        for sub in ("retros", ".local", "stories", "reviews"):
            (sd / sub).mkdir(parents=True)
        (sd / "retros" / "RETRO9100-t.md").write_text(RETRO, encoding="utf-8")
        (sd / "stories" / f"{UNIT}-s.md").write_text(
            f"# {UNIT}: s\n\n> **Status:** Done\n> **Points:** 3\n", encoding="utf-8")
        state = {"schema": 1, "run_id": "RUN-TEST01", "started_at": "2026-01-01T00:00:00Z",
                 "outcome": "running", "batch": [UNIT], "batch_changes": []}
        (sd / ".local" / "run-state.json").write_text(json.dumps(state), encoding="utf-8")

    def _closing(self, first: str, second: str) -> tuple:
        """Append `first` then `second` against UNIT, both dated DAY, and return the
        closing-review row's state and value."""
        body = ["| Base | Reviewer | Author | Verdict | Date | Units | Findings |",
                "| --- | --- | --- | --- | --- | --- | --- |",
                f"| abc123 | qa-batch | engineering-seat | {first} | {DAY} | {UNIT} | none |",
                f"| def456 | qa-batch | engineering-seat | {second} | {DAY} | {UNIT} | none |"]
        (self.root / "sdlc-studio" / "reviews" / "sprint-review-record.md").write_text(
            "# Sprint-level Reviews\n\n" + "\n".join(body) + "\n", encoding="utf-8")
        ck = sr.checklist(self.root, "RETRO9100", unit_ids=[UNIT])
        row = next(r for r in ck["items"] if r["id"] == "closing-review")
        return row["state"], row["value"]

    def test_a_later_approve_clears_an_earlier_same_day_reject(self) -> None:
        """Under the mutant the REJECT decides and the row holds the unit as unresolved."""
        self.assertEqual((sr.RAN, "1 unit(s) approved"), self._closing("REJECT", "APPROVE"))

    def test_a_later_reject_holds_an_earlier_same_day_approve(self) -> None:
        """Under the mutant the APPROVE decides. The coverage reading calls the unit uncovered
        in either case, so the row is held under both, and the mutant is caught by its value:
        it reads `unreviewed` where the unit was reviewed and rejected."""
        self.assertEqual((sr.NOT_RUN, "1 unresolved of 1 unit(s)"),
                         self._closing("APPROVE", "REJECT"))


if __name__ == "__main__":
    unittest.main()
