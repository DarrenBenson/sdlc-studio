"""BG0983: review coverage and the per-unit verdict read only the open run's own rounds.

The run fixes each unit's `REVIEW_BASE`, its row count before its first review in the run, and
`critic.delivery_rounds` reads only the rows past it. `sprint.review_coverage` and
`critic.verdict_for` read every row the unit ever had, so a unit re-delivered in a later run
carried its earlier delivery's APPROVE into the new run and the close counted it covered with no
review of the new change. The rows are written by `critic.record_verdict`, the product's writer,
and the closing-review row is read from `sprint_report.checklist`.

MUTANTS, each of which a test here fails on: (1) the whole ledger is read again inside a run;
(2) a unit the run holds but never reviewed reads the whole ledger; (3) the rows past the base
are dropped too, so an APPROVE recorded in the run covers nothing; (4) the run's scoping is
applied outside a run, so a unit no open run holds reads no verdict.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import critic  # noqa: E402
import sprint  # noqa: E402
import sprint_report as sr  # noqa: E402
from lib import run_state  # noqa: E402

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
REVIEWER = "Rowan Hart (qa)"
AUTHOR = "Dani Okafor (engineering)"


class CoverageScopedToTheRunTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        sd = self.root / "sdlc-studio"
        for sub in ("retros", ".local", "stories", "reviews"):
            (sd / sub).mkdir(parents=True)
        (sd / "retros" / "RETRO9100-t.md").write_text(RETRO, encoding="utf-8")
        (sd / "stories" / f"{UNIT}-s.md").write_text(
            f"# {UNIT}: s\n\n> **Status:** Review\n> **Points:** 3\n", encoding="utf-8")

    def _open_run(self, **extra) -> None:
        state = {"schema": 1, "run_id": "RUN-TEST01", "started_at": "2026-10-01T00:00:00Z",
                 "outcome": "running", "batch": [UNIT], "batch_changes": [], **extra}
        (self.root / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps(state), encoding="utf-8")

    def _approve(self) -> None:
        critic.record_verdict(self.root, UNIT, "APPROVE", reviewer=REVIEWER, author=AUTHOR)

    def _covered(self) -> bool:
        return sprint.review_coverage(self.root, [UNIT])[UNIT]["covered"]

    def _closing(self) -> dict:
        ck = sr.checklist(self.root, "RETRO9100", unit_ids=[UNIT])
        return next(r for r in ck["items"] if r["id"] == "closing-review")

    def test_an_earlier_delivery_approve_does_not_cover(self) -> None:
        self._approve()                     # the earlier delivery, recorded outside any run
        self.assertTrue(self._covered(), "the earlier APPROVE must cover outside a run")
        for label, extra in (("base fixed past the APPROVE", {run_state.REVIEW_BASE: {UNIT: 1}}),
                             ("held, never reviewed in the run", {})):
            with self.subTest(label):
                self._open_run(**extra)
                self.assertIsNone(critic.verdict_for(self.root, UNIT),
                                  "the per-unit verdict reads an earlier delivery's APPROVE")
                self.assertFalse(self._covered(),
                                 "an earlier delivery's APPROVE covers the re-delivered unit")
                row = self._closing()
                self.assertEqual(sr.NOT_RUN, row["state"],
                                 f"closing-review reads the batch reviewed: {row}")

    def test_an_approve_in_the_run_covers(self) -> None:
        self._approve()                     # the earlier delivery
        self._open_run()
        self._approve()                     # this run's review: the writer fixes the base first
        self.assertEqual({UNIT: 1}, run_state.read(self.root)[run_state.REVIEW_BASE])
        row = critic.verdict_for(self.root, UNIT)
        self.assertEqual("APPROVE", row["verdict"])
        self.assertTrue(self._covered(), "the run's own APPROVE does not cover the unit")
        self.assertEqual(sr.RAN, self._closing()["state"])

    def test_outside_a_run_the_whole_ledger_counts(self) -> None:
        self._approve()
        for label, extra in (("no run state", None),
                             ("a run that does not hold the unit", {"batch": ["US0002"]}),
                             ("a run that has ended", {"outcome": "goal-reached"})):
            with self.subTest(label):
                path = self.root / "sdlc-studio" / ".local" / "run-state.json"
                path.unlink(missing_ok=True)
                if extra is not None:
                    self._open_run(**extra)
                self.assertEqual("APPROVE", (critic.verdict_for(self.root, UNIT) or {})
                                 .get("verdict"), "outside a run the whole ledger counts")
                self.assertTrue(self._covered())
        # A run state that cannot be read, its bytes not JSON or not UTF-8, names no run to
        # scope to, so the per-unit verdict reads the whole ledger rather than raising.
        for label, body in (("not JSON", b"{not json"), ("not UTF-8", b"\xff\xfe{}")):
            with self.subTest(label):
                (self.root / "sdlc-studio" / ".local" / "run-state.json").write_bytes(body)
                self.assertEqual("APPROVE", (critic.verdict_for(self.root, UNIT) or {})
                                 .get("verdict"), "an unreadable run state raised or hid it")


if __name__ == "__main__":
    unittest.main()
