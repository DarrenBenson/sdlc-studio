"""BG0962: the closing-review row reads a unit's latest verdict across BOTH ledgers.

The row folded each unit's latest verdict from the frozen batch ledger alone, so a unit REJECTed
in a pre-6.x batch review stayed unresolved after any number of per-unit APPROVEs, and a run whose
every unit was independently approved could not close. The fold now merges the per-unit verdict
(`critic.verdict_for`, which keeps US0914's rule for answering a REJECT) with the frozen rows by
date. US0593 still holds: a REJECT later than an APPROVE is terminal, whichever ledger holds it,
and a same-day tie between the ledgers fails closed.

The per-unit rows are written by `critic.record_verdict`, the product's own writer; a test that
needs an earlier date rewrites only the date cell of the row it wrote. The frozen ledger has no
writer any more, so its rows are written in the layout the committed ledger carries.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import critic  # noqa: E402
import sprint  # noqa: E402
import sprint_report as sr  # noqa: E402

_ISO_DAY = re.compile(r"\d{4}-\d{2}-\d{2}")

UNIT = "US0001"
RETRO = f"""# RETRO-9100: a sprint

> **Batch:** {UNIT}

## Delivered
- shipped

## What went well
- good

## What was hard / what stalled
- hard

## Lessons
- a real lesson worth keeping for next time

## Actions raised
| Finding | Disposition |
| --- | --- |
| another | declined: not ours |
"""
#: Inside the frozen ledger's licence: `critic.sprint_reviews` keeps only rows dated before
#: `REPAIR_VERB_RETIRED`, so a fixture row on or after it would count for nothing.
FROZEN_DAY = "2026-09-16"
REVIEWER = "qa-seat-r1"
AUTHOR = "engineering-seat"


class ClosingReviewSpansBothLedgersTests(unittest.TestCase):

    def setUp(self) -> None:
        self.assertLess(FROZEN_DAY, critic.REPAIR_VERB_RETIRED)
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

    def _frozen(self, verdict: str, date: str = FROZEN_DAY) -> None:
        body = ["| Base | Reviewer | Author | Verdict | Date | Units | Findings |",
                "| --- | --- | --- | --- | --- | --- | --- |",
                f"| abc123 | qa-batch | {AUTHOR} | {verdict} | {date} | {UNIT} | none |"]
        critic.sprint_review_path(self.root).write_text(
            "# Sprint-level Reviews\n\n" + "\n".join(body) + "\n", encoding="utf-8")

    def _per_unit(self, verdict: str, date: str | None = None) -> None:
        critic.record_verdict(self.root, UNIT, verdict, reviewer=REVIEWER, author=AUTHOR)
        if date is None:
            return
        path = critic.verdicts_path(self.root)
        lines = path.read_text(encoding="utf-8").splitlines()
        row = max(i for i, ln in enumerate(lines) if f"| {UNIT} |" in ln and verdict in ln)
        cells = lines[row].split(" | ")
        idx = next(i for i, c in enumerate(cells) if _ISO_DAY.fullmatch(c))
        cells[idx] = date
        lines[row] = " | ".join(cells)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _closing(self) -> dict:
        ck = sr.checklist(self.root, "RETRO9100", unit_ids=[UNIT])
        return next(r for r in ck["items"] if r["id"] == "closing-review")

    def test_frozen_reject_then_per_unit_approve_is_resolved(self) -> None:
        """AC1. Mutant: `_verdict_entries` folding `ctx['sprint_reviews']` alone, the BG0962
        defect - the frozen REJECT stays the unit's latest verdict and the row names it
        unresolved although its per-unit round 2 approved it."""
        self._frozen("REJECT")
        self._per_unit("REJECT")
        self._per_unit("APPROVE")
        self.assertEqual("APPROVE", critic.verdict_for(self.root, UNIT)["verdict"].upper())
        row = self._closing()
        self.assertEqual(sr.RAN, row["state"], row)
        self.assertNotIn("unresolved", str(row.get("value")))

    def test_later_per_unit_reject_wins(self) -> None:
        """AC2. Mutant: a per-unit APPROVE taken over any batch verdict whatever the dates, or the
        per-unit rows sorted before the batch rows - either hides a REJECT that came later."""
        with self.subTest(case="frozen APPROVE, then a per-unit REJECT"):
            self._frozen("APPROVE")
            self._per_unit("REJECT")
            row = self._closing()
            self.assertEqual(sr.NOT_RUN, row["state"], row)
            self.assertIn("unresolved", str(row.get("value")))

    def test_an_earlier_per_unit_approve_does_not_clear_a_later_frozen_reject(self) -> None:
        """AC2, US0593 kept. Mutant: the per-unit ledger always wins, so a stale APPROVE under a
        later batch REJECT clears the row over a batch nobody cleared."""
        self._per_unit("APPROVE", date="2026-09-01")
        self._frozen("REJECT")
        row = self._closing()
        self.assertEqual(sr.NOT_RUN, row["state"], row)
        self.assertIn("unresolved", str(row.get("value")))

    def test_a_same_day_tie_between_the_ledgers_fails_closed(self) -> None:
        """Mutant: per-unit rows always sorted after batch rows on the same date, so a per-unit
        APPROVE recorded the day of a batch REJECT clears it although nothing says which came
        second. A tie the record cannot order is resolved towards the REJECT."""
        self._frozen("REJECT")
        self._per_unit("APPROVE", date=FROZEN_DAY)
        row = self._closing()
        self.assertEqual(sr.NOT_RUN, row["state"], row)

    def test_agrees_with_review_coverage(self) -> None:
        """AC3. Mutant: the fold merging the ledgers while the row still decides on a reading of
        its own - closing-review must clear exactly the unit `review_coverage` reports covered,
        and hold exactly the one it does not."""
        self._frozen("REJECT")
        self._per_unit("REJECT")
        self._per_unit("APPROVE")
        covered = sprint.review_coverage(self.root, [UNIT])[UNIT]["covered"]
        self.assertTrue(covered)
        self.assertEqual(sr.RAN, self._closing()["state"])
        # And the converse, on a fresh per-unit ledger (the round cap allows two rounds): a
        # per-unit REJECT later than a batch APPROVE leaves the unit uncovered, a recorded
        # negative being terminal for `review_coverage`, and the row holds it.
        critic.verdicts_path(self.root).unlink()
        self._frozen("APPROVE")
        self._per_unit("REJECT")
        self.assertFalse(sprint.review_coverage(self.root, [UNIT])[UNIT]["covered"])
        self.assertEqual(sr.NOT_RUN, self._closing()["state"])


if __name__ == "__main__":
    unittest.main()
