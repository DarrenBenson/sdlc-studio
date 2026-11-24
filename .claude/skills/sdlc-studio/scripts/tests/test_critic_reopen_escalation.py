"""BG1069: the escalation `critic.py record` prints read the unit's whole verdict history, so a
reopened unit's first REJECT in its new delivery was reported as a panel split against the closed
delivery's APPROVE, or as a second REJECT beside the closed delivery's. It now reads the unit's
current delivery alone, as `delivery_rounds` partitions it, for both the REJECT count and the
seats' verdicts; two REJECTs, or a split, inside one delivery still escalate.

Each case records through `critic.py record`'s entry point in a throwaway workspace, an open run
opened through `run_state` where the case needs one.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import critic  # noqa: E402
from lib import run_state  # noqa: E402

UNIT = "US0101"
SEAT_A, SEAT_B = "engineering-seat-a", "qa-seat-b"
ESCALATED = "ESCALATED for the operator"


def _workspace(root: Path) -> None:
    story = root / "sdlc-studio" / "stories" / f"{UNIT}-unit.md"
    story.parent.mkdir(parents=True)
    story.write_text(f"# {UNIT}: unit\n\n> **Status:** Review\n> **Points:** 1\n"
                     f"> **Epic:** EP0001\n> **Affects:** src/unit.py\n\n"
                     "## Acceptance Criteria\n\n### AC1: works\n- **Verify:** shell true\n",
                     encoding="utf-8")


def _record(root: Path, verdict: str, reviewer: str) -> str:
    """Record one verdict through `critic.py record`; everything it printed."""
    issues = "[new] the unit is wrong" if verdict == "reject" else "none"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = critic.main(["record", "--unit", UNIT, "--verdict", verdict, "--reviewer", reviewer,
                          "--author", "builder", "--issues", issues, "--root", str(root)])
    assert rc == 0, buf.getvalue()
    return buf.getvalue()


class ReopenEscalationTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        _workspace(self.root)
        saved = os.environ.get(run_state.TRANSCRIPTS_ENV)
        os.environ[run_state.TRANSCRIPTS_ENV] = "/nonexistent-transcripts-for-tests"
        self.addCleanup(lambda: os.environ.__setitem__(run_state.TRANSCRIPTS_ENV, saved)
                        if saved is not None else os.environ.pop(run_state.TRANSCRIPTS_ENV, None))

    def _round_one(self) -> None:
        self.assertEqual([1], [r["round"] for r in critic.delivery_rounds(self.root, UNIT)],
                         "premise: the REJECT is not round 1 of a new delivery")

    def test_a_reject_after_a_reopen_is_judged_against_the_new_delivery_only(self) -> None:
        """AC1. Mutant: the seats' verdicts read from the whole history, so seat A's APPROVE of
        the closed delivery reads as a split."""
        _record(self.root, "approve", SEAT_A)
        out = _record(self.root, "reject", SEAT_B)
        self._round_one()
        self.assertNotIn(ESCALATED, out)

    def test_a_closed_deliverys_reject_is_not_counted_in_a_new_run(self) -> None:
        """AC2. Mutant: the REJECTs counted over the whole history, so the closed delivery's
        REJECT makes two."""
        _record(self.root, "reject", SEAT_A)
        _record(self.root, "approve", SEAT_A)
        run_state.open_run(self.root, batch=[UNIT], goal="g")
        out = _record(self.root, "reject", SEAT_B)
        self._round_one()
        self.assertNotIn(ESCALATED, out)

    def test_two_rejects_in_one_delivery_still_escalate(self) -> None:
        """AC3, the control: the current delivery's own REJECTs are still counted."""
        self.assertNotIn(ESCALATED, _record(self.root, "reject", SEAT_A))
        out = _record(self.root, "reject", SEAT_A)
        self.assertIn(f"{ESCALATED} - {UNIT}: the panel rejected this unit twice", out)

    def test_a_split_inside_one_delivery_still_escalates(self) -> None:
        """The control for the seats: in an open run, seat A's APPROVE and then seat B's REJECT
        are one delivery, and still a split, though B's REJECT at the cap carried the unit out of
        the batch. Mutants: no seats' verdicts passed to the judge; the delivery read without
        the open run's base once the carry dropped the unit, so only B's REJECT is seen."""
        run_state.open_run(self.root, batch=[UNIT], goal="g")
        _record(self.root, "approve", SEAT_A)
        out = _record(self.root, "reject", SEAT_B)
        self.assertNotIn(UNIT, run_state.read(self.root)["batch"], "premise: no carry")
        self.assertEqual(2, len(critic.delivery_rounds(self.root, UNIT, run_state.read(self.root))),
                         "premise: one delivery in the run")
        self.assertIn(f"{ESCALATED} - {UNIT}: the panel split: {SEAT_B} rejected while {SEAT_A} "
                      f"approved", out)

    def test_a_closed_runs_delivery_is_not_read_after_a_reopen(self) -> None:
        """A run that closed on seat A's APPROVE still holds its base for the unit; seat B's
        REJECT after the close is round 1 of a new delivery. Mutant: the run's base read
        whether or not the run is open, so the closed run's APPROVE reads as a split."""
        run_state.open_run(self.root, batch=[UNIT], goal="g")
        _record(self.root, "approve", SEAT_A)
        state = run_state.read(self.root)
        state["outcome"] = run_state.GOAL_REACHED
        run_state.write(self.root, state)
        self.assertIn(UNIT, run_state.read(self.root)[run_state.REVIEW_BASE], "premise: no base")
        out = _record(self.root, "reject", SEAT_B)
        self._round_one()
        self.assertNotIn(ESCALATED, out)

    def test_the_plan_review_phase_reads_its_own_ledger(self) -> None:
        """The phase no command records: its rounds are its own ledger's, not the delivery's.
        Mutant: every phase read through `delivery_rounds`."""
        for _ in range(2):
            critic.record_verdict(self.root, UNIT, "REJECT", SEAT_A, "builder",
                                  "[new] the plan is wrong", phase="plan-review")
        self.assertEqual([], critic.delivery_rounds(self.root, UNIT), "premise: no delivery row")
        self.assertIn("the panel rejected this unit twice",
                      critic.escalation_notice(self.root, UNIT, "plan-review"))
        self.assertEqual("", critic.escalation_notice(self.root, UNIT))


if __name__ == "__main__":
    unittest.main()
