"""BG0983: review coverage and the per-unit verdict read only the open run's own rounds.

The run fixes each unit's `REVIEW_BASE`, its row count before its first review in the run, and
`critic.delivery_rounds` reads only the rows past it. `sprint.review_coverage` and
`critic.verdict_for` read every row the unit ever had, so a unit re-delivered in a later run
carried its earlier delivery's APPROVE into the new run and the close counted it covered with no
review of the new change. The rows are written by `critic.record_verdict`, the product's writer,
and the closing-review row is read from `sprint_report.checklist`.

The run scopes which APPROVE covers a unit, never which REJECT holds it: a REJECT no later
APPROVE from its own reviewer answered stands from any delivery (`critic.REJECT_EXITS`).

MUTANTS, each of which a test here fails on: (1) the whole ledger is read again inside a run;
(2) a unit the run holds but never reviewed reads the whole ledger; (3) the rows past the base
are dropped too, so an APPROVE recorded in the run covers nothing; (4) the run's scoping is
applied outside a run, so a unit no open run holds reads no verdict; (5) the unanswered REJECTs
are read from the run's rows alone, so another reviewer's APPROVE in a later run discharges a
carried unit's REJECT, and a held unit the run has not reviewed reads no verdict and a frozen
batch review covers it over its REJECT; (6) the base skips only the live rows, not every row it
counted; (7) the base is looked up under the id as typed rather than its normal form; (8) a phase
other than delivery is scoped to the run's delivery base.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import critic  # noqa: E402
import sprint  # noqa: E402
import sprint_report as sr  # noqa: E402
import test_lean_review_cap as cap  # noqa: E402 - the carried-at-the-cap fixture, shared
from lib import run_state, sdlc_md  # noqa: E402

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

    def _batch_review(self) -> None:
        """A frozen batch-ledger APPROVE naming the unit, dated before
        `critic.REPAIR_VERB_RETIRED`, so it still covers a unit with no verdict of its own."""
        path = self.root / "sdlc-studio" / "reviews" / "sprint-review-record.md"
        path.write_text("# Sprint-level Reviews\n\n"
                        "| Base | Reviewer | Author | Verdict | Date | Units | Findings |\n"
                        "| --- | --- | --- | --- | --- | --- | --- |\n"
                        f"| - | Ana Ruiz (qa) | {AUTHOR} | APPROVE | 2026-09-01 | {UNIT} | - |\n",
                        encoding="utf-8")

    @staticmethod
    def _who(row: dict | None) -> tuple:
        return ((row or {}).get("verdict"), (row or {}).get("reviewer"))

    def test_an_earlier_reject_holds_a_held_unit_a_batch_review_names(self) -> None:
        """MUTANT (5): the unanswered REJECTs read from the run's rows alone, so a held unit the
        run has not reviewed reads no verdict and the batch lane covers it over its REJECT."""
        self._batch_review()
        self.assertEqual({"covered": True, "by": "batch review"},
                         sprint.review_coverage(self.root, [UNIT])[UNIT],
                         "premise: the batch row does not cover a unit with no verdict")
        critic.record_verdict(self.root, UNIT, "REJECT", reviewer=REVIEWER, author=AUTHOR,
                              issues="[new] drops a row")
        self._open_run()
        self.assertEqual(("REJECT", REVIEWER), self._who(critic.verdict_for(self.root, UNIT)))
        self.assertFalse(self._covered(), "a batch review covers a unit over its REJECT")
        self.assertEqual(critic.COVERAGE_UNREVIEWED, critic.coverage_state(self.root, UNIT))
        self.assertEqual(sr.NOT_RUN, self._closing()["state"])

    def test_the_base_skips_every_row_it_counted(self) -> None:
        """MUTANT (6): skip only the live rows. The base counts every row the unit had, a
        superseded one too, so a base of 2 over a superseded row and an earlier delivery's
        APPROVE leaves the run's own APPROVE; skipping two LIVE rows skips that APPROVE too."""
        critic.record_verdict(self.root, UNIT, "APPROVE", reviewer="Ana Ruiz (qa)",
                              author=AUTHOR)
        critic.record_supersession(self.root, UNIT, date=critic.read_verdicts(self.root)[0]
                                   ["date"], reason="recorded against the wrong unit",
                                   authorised_by="Olu Ade", boundary="operator session",
                                   reviewer="Ana Ruiz (qa)")
        self._approve()                     # the earlier delivery
        self._open_run()
        critic.record_verdict(self.root, UNIT, "APPROVE", reviewer="Sam Eriksson (qa)",
                              author=AUTHOR)
        self.assertEqual({UNIT: 2}, run_state.read(self.root)[run_state.REVIEW_BASE])
        self.assertTrue(critic.read_verdicts(self.root)[0]["superseded"], "premise")
        self.assertEqual(("APPROVE", "Sam Eriksson (qa)"),
                         self._who(critic.verdict_for(self.root, UNIT)))
        self.assertTrue(self._covered())

    def test_the_base_is_read_under_the_normal_id(self) -> None:
        """MUTANT (7): look the base up under the id as typed, so `critic.py show --unit us0001`
        in a run prints no verdict over the run's own APPROVE."""
        self._open_run()
        self._approve()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = critic.main(["show", "--unit", UNIT.lower(), "--root", str(self.root)])
        self.assertEqual(0, rc)
        self.assertNotIn("no verdict", out.getvalue())
        self.assertIn("'verdict': 'APPROVE'", out.getvalue())

    def test_only_the_delivery_phase_is_scoped_to_the_run(self) -> None:
        """MUTANT (8): scope every phase to the run's delivery base, so a plan-review APPROVE a
        held unit carries reads None at `plan-review`, the phase transition.py reads it at."""
        self._open_run()
        critic.record_verdict(self.root, UNIT, "APPROVE", reviewer=REVIEWER, author=AUTHOR,
                              phase="plan-review")
        self.assertNotIn(UNIT, run_state.read(self.root).get(run_state.REVIEW_BASE) or {},
                         "premise: the run has not reviewed the unit's delivery")
        self.assertEqual("APPROVE", (critic.verdict_for(self.root, UNIT, "plan-review") or {})
                         .get("verdict"))
        self.assertEqual(critic.COVERAGE_APPROVED,
                         critic.coverage_state(self.root, UNIT, "plan-review"))


class AnEarlierRejectStandsTests(unittest.TestCase):
    """A carried unit reaches Done only on an APPROVE from the reviewer whose REJECT carried it
    (`critic.REJECT_EXITS`), so another reviewer's REJECT and APPROVE in a later run leave it
    rejected, open or ended. The fixture is `test_lean_review_cap`'s, driven through
    `critic.py record` and `transition.py set`."""

    def setUp(self) -> None:
        patch = mock.patch.dict(os.environ, {
            run_state.TRANSCRIPTS_ENV: "/nonexistent-transcripts-for-tests"})
        patch.start()
        self.addCleanup(patch.stop)

    def _carried_then_reviewed_by_another(self, root: Path) -> None:
        run_state.open_run(root, batch=[cap.BUG, "US0002"], goal="g")
        for issues in ("[new] drops a row", "[new] still drops it"):
            rc, out = cap._bug_record(root, "REJECT", "rev-a", issues)
            self.assertEqual(0, rc, out)
        self.assertTrue(run_state.read(root)["batch_changes"][-1]["reason"]
                        .startswith(critic.CARRIED_REASON), "premise: the unit was not carried")
        run_state.update(root, outcome="goal-reached")
        run_state.open_run(root, batch=[cap.BUG], goal="g2")
        self.assertEqual(0, cap._bug_record(root, "REJECT", "rev-b", "[new] another")[0])
        self.assertEqual(0, cap._bug_record(root, "APPROVE", "rev-b")[0])

    @staticmethod
    def _status(root: Path) -> str:
        return sdlc_md.extract_field(cap._bug_text(root), "Status")

    def test_another_reviewers_approve_does_not_discharge_a_carried_reject(self) -> None:
        """MUTANT (5): the unanswered REJECTs read from the run's rows alone. rev-b's APPROVE
        answers rev-b's REJECT and the bug reaches Fixed while the later run is open, and the
        same ledger reads rejected again once the run ends."""
        for shape in ("the later run open", "the later run ended"):
            with self.subTest(shape), tempfile.TemporaryDirectory() as d:
                root = cap._bug_workspace(d)
                self._carried_then_reviewed_by_another(root)
                if shape.endswith("ended"):
                    run_state.update(root, outcome="goal-reached")
                row = critic.verdict_for(root, cap.BUG) or {}
                self.assertEqual(("REJECT", "rev-a"), (row.get("verdict"), row.get("reviewer")))
                self.assertEqual(critic.COVERAGE_UNREVIEWED, critic.coverage_state(root, cap.BUG))
                self.assertFalse(sprint.review_coverage(root, [cap.BUG])[cap.BUG]["covered"])
                rc, out = cap._fixed(root)
                self.assertNotEqual(0, rc, out)
                self.assertIn("rev-a", out)
                self.assertEqual("In Progress", self._status(root))
        # THE CONTROL: the rejecting reviewer's own APPROVE in the later run discharges it.
        with tempfile.TemporaryDirectory() as d:
            root = cap._bug_workspace(d)
            self._carried_then_reviewed_by_another(root)
            rc, out = cap._bug_record(root, "APPROVE", "rev-a")
            self.assertEqual(0, rc, out)
            row = critic.verdict_for(root, cap.BUG) or {}
            self.assertEqual(("APPROVE", "rev-a"), (row.get("verdict"), row.get("reviewer")))
            rc, out = cap._fixed(root)
            self.assertEqual(0, rc, out)
            self.assertEqual("Fixed", self._status(root))


if __name__ == "__main__":
    unittest.main()
