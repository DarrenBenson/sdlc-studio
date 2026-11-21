"""`sprint lane accept` on a carried unit records under the reviewer who rejected it.

A unit rejected at the review cap is carried as a bug and delivered again in a later run, where
it reaches Done only on an APPROVE from the reviewer whose REJECT it carried (`critic`'s
REJECT_EXITS). The later run counts its rounds afresh, so `critic.py record` takes a verdict
from any reviewer there, and an APPROVE recorded under another id was stranded: written, and
the unit refused Done. `lane accept` now defaults `--reviewer` on a carried unit to the id that
rejected it and refuses any other, naming that id, before anything is recorded, and records the
verdict under that id exactly as the REJECT was recorded, bare or with its seat group.

Every case but one drives `sprint.py lane accept` through `sprint.main` against
`test_lane_accept`'s throwaway repository; the carry is made for real, by two REJECTs recorded
at the cap with `critic.py record` in an open run, before a later run opens with the unit in
its batch. The one calls `sprint._lane_carried_reviewer` with the unit's verdict rows stubbed,
for orders of REJECTs by several reviewers that the round rule does not let a ledger reach.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import io
import os
import subprocess
import sys
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lane_accept as base  # noqa: E402

critic, sprint, SCRIPTS = base.critic, base.sprint, base.SCRIPTS
GREEN, BUG, AUTHOR = base.GREEN, base.BUG, base.AUTHOR
run_state = sys.modules["lib.run_state"]
#: the reviewer whose two REJECTs carried GREEN, as `lane accept` records a seat's id
REJECTER = f"qa-seat-{GREEN}-r1 (qa)"
#: the same reviewer as `critic.py record --reviewer` writes it, with no seat group
BARE = f"qa-seat-{GREEN}-r1"


class CarriedReviewerIdTests(unittest.TestCase):

    def setUp(self) -> None:
        base.LaneAcceptTests.setUp(self)  # the repository, its briefs and GREEN's self-check
        self.addCleanup(self._tmp.cleanup)
        env = unittest.mock.patch.dict(os.environ, {
            run_state.TRANSCRIPTS_ENV: str(self.root / "no-transcripts")})
        env.start()
        self.addCleanup(env.stop)
        # the carry is made by each test, under the id it names (`_carry`)

    def _record(self, uid: str, verdict: str, reviewer: str) -> None:
        """`verdict` on `uid` under `reviewer`, through `critic.py record`, moving nothing."""
        self._n = getattr(self, "_n", 0) + 1
        path = base._write(self.root, f"verdicts/{uid}-{self._n}.txt", verdict)
        done = subprocess.run(
            [sys.executable, str(SCRIPTS / "critic.py"), "record", "--unit", uid,
             "--from-verdict", str(path), "--reviewer", reviewer, "--author", AUTHOR,
             "--brief", self.fp[uid], "--tier", "full", "--root", str(self.root)],
            capture_output=True, text=True, timeout=300, check=False)
        self.assertEqual(0, done.returncode, done.stdout + done.stderr)

    def _carry(self, rejecter: str = REJECTER) -> None:
        """GREEN carried at the cap by two REJECTs under `rejecter`, and a later run opened with
        GREEN in its batch, where its rounds count afresh."""
        run_state.open_run(self.root, batch=[GREEN], goal="g")
        for _ in (1, 2):
            self._record(GREEN, base.REJECT, rejecter)
        self.bug = critic.carried_by(self.root, GREEN)
        self.assertIsNotNone(self.bug, "premise: the second REJECT carried the unit")
        run_state.update(self.root, outcome="goal-reached")
        run_state.open_run(self.root, batch=[GREEN], goal="g2")
        self.assertEqual(0, critic.review_rounds(self.root, GREEN),
                         "premise: the later run counts the unit's rounds afresh")

    def _accept(self, uid: str, *reviewer: str, author: str | None = None
                ) -> tuple[int, str, str]:
        path = base._write(self.root, f"verdicts/{uid}-approve.txt", base.APPROVE)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sprint.main(["lane", "accept", "--unit", uid, "--verdict", str(path),
                              *(("--reviewer", reviewer[0]) if reviewer else ()),
                              *(("--author", author) if author else ()),
                              "--root", str(self.root)])
        return rc, out.getvalue(), err.getvalue()

    def _rows(self, uid: str) -> list[list[str]]:
        return base.LaneAcceptTests._rows(self, uid)

    def test_another_reviewer_is_refused_naming_the_one_who_rejected(self) -> None:
        """MUTANT: no check, so the APPROVE is recorded under the fresh id and stranded: the
        unit is refused Done and the carry is not discharged."""
        self._carry()
        before = len(self._rows(GREEN))
        rc, out, err = self._accept(GREEN, f"qa-seat-{GREEN}-r2")
        self.assertEqual(2, rc, out + err)
        self.assertIn(REJECTER, err)
        self.assertIn(self.bug, err)
        self.assertEqual(before, len(self._rows(GREEN)), "a verdict was recorded")
        self.assertEqual("Review", base._status(self.root, GREEN))

    def test_no_reviewer_defaults_to_the_one_who_rejected(self) -> None:
        """MUTANT: no default, so `lane accept` refuses for want of --reviewer."""
        self._carry()
        rc, out, err = self._accept(GREEN)
        self.assertEqual(0, rc, out + err)
        self.assertIn(f"--reviewer defaults to {REJECTER}", out + err)
        row = self._rows(GREEN)[-1]
        self.assertEqual(["APPROVE", REJECTER], [row[1], row[2]])
        self.assertEqual("Done", base._status(self.root, GREEN))

    def test_the_rejecting_id_and_an_uncarried_unit_are_accepted_as_before(self) -> None:
        """The control: the id that rejected, given bare, records under its seat group, and a
        unit never carried takes any reviewer the seat check takes."""
        self._carry()
        rc, out, err = self._accept(GREEN, f"qa-seat-{GREEN}-r1")
        self.assertEqual(0, rc, out + err)
        self.assertEqual(REJECTER, self._rows(GREEN)[-1][2])
        rc, out, err = self._accept(BUG, "qa-seat-anyone", author="bug-builder")
        self.assertEqual(0, rc, out + err)
        self.assertEqual("qa-seat-anyone (qa)", self._rows(BUG)[-1][2])

    def test_a_rejecter_recorded_bare_is_defaulted_to_as_recorded(self) -> None:
        """The carrying REJECTs were recorded under a bare id, the form `critic.py record
        --reviewer` writes: the default records the APPROVE under that id exactly, so it answers
        them and the unit reaches Done. MUTANT: the default given the seat group a --reviewer
        value gets, as it was, so the APPROVE is recorded under `<id> (qa)`, answers neither
        REJECT, and the unit stays at Review."""
        self._carry(BARE)
        rc, out, err = self._accept(GREEN)
        self.assertEqual(0, rc, out + err)
        self.assertIn(f"--reviewer defaults to {BARE}, whose REJECT", out + err)
        self.assertEqual(["APPROVE", BARE], self._rows(GREEN)[-1][1:3])
        self.assertEqual("Done", base._status(self.root, GREEN))
        self.assertEqual([], critic._unanswered_rejects(  # noqa: SLF001
            critic._live_verdict_rows(self.root, GREEN)))  # noqa: SLF001

    def test_a_bare_rejecter_named_as_recorded_is_recorded_as_recorded(self) -> None:
        """The bare id given as --reviewer is recorded as the REJECTs were, not under the seat
        group the cell check gives it. MUTANT: the cell recorded, `<id> (qa)`, as it was."""
        self._carry(BARE)
        rc, out, err = self._accept(GREEN, BARE)
        self.assertEqual(0, rc, out + err)
        self.assertEqual(["APPROVE", BARE], self._rows(GREEN)[-1][1:3])
        self.assertEqual("Done", base._status(self.root, GREEN))

    def test_a_rejecter_whose_id_names_no_seat_is_taken_as_recorded(self) -> None:
        """The carrying REJECTs were recorded under an id that names no seat: that id, given or
        defaulted to, is recorded as it was, though the seat check refuses it for any other
        unit, since no other id can answer the carry. MUTANT: the seat check's refusal kept
        over the carried id, so the only APPROVE that discharges the carry is refused."""
        self._carry("reviewer-x")
        rc, out, err = self._accept(GREEN, "reviewer-x")
        self.assertEqual(0, rc, out + err)
        self.assertEqual(["APPROVE", "reviewer-x"], self._rows(GREEN)[-1][1:3])
        self.assertEqual("Done", base._status(self.root, GREEN))

    def test_the_default_is_the_reviewer_of_the_latest_unanswered_reject(self) -> None:
        """The default is the reviewer of the latest unanswered REJECT, a named one of them is
        taken as recorded, and a refusal names them latest first. A, B, A (the review's own
        case) defaults to A; B, A, C, A defaults to A as well, where each wrong order gives
        another reviewer. MUTANTS: the first-seen order with its last id, as it was (B, then
        C); the first-seen order with its first id (A, then B); the latest-first order with its
        last id (B, then B)."""
        self._carry()
        for order, named, listed in (
                (("a", "b", "a"), "b", "'qa-seat-a' or 'qa-seat-b'"),
                (("b", "a", "c", "a"), "c", "'qa-seat-a' or 'qa-seat-c' or 'qa-seat-b'")):
            rows = [{"unit": GREEN, "verdict": "REJECT", "reviewer": f"qa-seat-{who}"}
                    for who in order]
            with self.subTest(order=order), \
                    unittest.mock.patch.object(critic, "_live_verdict_rows", return_value=rows), \
                    contextlib.redirect_stderr(io.StringIO()) as said:
                self.assertEqual(("qa-seat-a", None),
                                 sprint._lane_carried_reviewer(self.root, GREEN, None, None))
                self.assertIn("defaults to qa-seat-a,", said.getvalue())
                self.assertEqual((f"qa-seat-{named}", None), sprint._lane_carried_reviewer(
                    self.root, GREEN, f"qa-seat-{named}", f"qa-seat-{named} (qa)"))
                got, refusal = sprint._lane_carried_reviewer(self.root, GREEN, "qa-seat-d", None)
                self.assertIsNone(got)
                self.assertIn(f"Name {listed}, or leave --reviewer off to record under "
                              f"'qa-seat-a'", refusal)

    def test_an_uncarried_unit_with_an_unanswered_reject_takes_no_default(self) -> None:
        """A unit never carried, with one unanswered round-1 REJECT, takes no default reviewer:
        with no --reviewer `lane accept` refuses, exit 2, and records nothing. MUTANT: the
        carry gate forced, so every unit is read as carried and the REJECT's reviewer is
        defaulted to, the APPROVE recorded."""
        self._carry()
        self._record(BUG, base.REJECT, f"qa-seat-{BUG}-r1")
        before = len(self._rows(BUG))
        rc, out, err = self._accept(BUG, author="bug-builder")
        self.assertEqual(2, rc, out + err)
        self.assertNotIn("defaults to", out + err)
        self.assertEqual(before, len(self._rows(BUG)), "a verdict was recorded")
        self.assertEqual("In Progress", base._status(self.root, BUG))

    def test_a_discharged_carry_takes_another_reviewer(self) -> None:
        """The rejecting reviewer's APPROVE discharged the carry, so no unanswered REJECT stands
        against the unit: a further verdict under another id is not refused by the carry check.
        MUTANT: every live verdict row read as owed, not only the unanswered REJECTs, so the
        rejecting reviewer is still the only id taken and the second verdict is refused."""
        self._carry()
        self._record(GREEN, base.APPROVE, REJECTER)
        rc, out, err = self._accept(GREEN, f"qa-seat-{GREEN}-r2")
        self.assertEqual(0, rc, out + err)
        self.assertNotIn("carried at the review cap", out + err)
        self.assertEqual(["APPROVE", f"qa-seat-{GREEN}-r2 (qa)"], self._rows(GREEN)[-1][1:3])
        self.assertEqual("Done", base._status(self.root, GREEN))


if __name__ == "__main__":
    unittest.main()
