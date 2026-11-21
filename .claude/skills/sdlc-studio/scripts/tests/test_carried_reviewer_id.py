"""`sprint lane accept` on a carried unit records under the reviewer who rejected it.

A unit rejected at the review cap is carried as a bug and delivered again in a later run, where
it reaches Done only on an APPROVE from the reviewer whose REJECT it carried (`critic`'s
REJECT_EXITS). The later run counts its rounds afresh, so `critic.py record` takes a verdict
from any reviewer there, and an APPROVE recorded under another id was stranded: written, and
the unit refused Done. `lane accept` now defaults `--reviewer` on a carried unit to the id that
rejected it and refuses any other, naming that id, before anything is recorded.

Every case drives `sprint.py lane accept` through `sprint.main` against `test_lane_accept`'s
throwaway repository; the carry is made for real, by two REJECTs recorded at the cap with
`critic.py record` in an open run, before a later run opens with the unit in its batch.
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


class CarriedReviewerIdTests(unittest.TestCase):

    def setUp(self) -> None:
        base.LaneAcceptTests.setUp(self)  # the repository, its briefs and GREEN's self-check
        self.addCleanup(self._tmp.cleanup)
        env = unittest.mock.patch.dict(os.environ, {
            run_state.TRANSCRIPTS_ENV: str(self.root / "no-transcripts")})
        env.start()
        self.addCleanup(env.stop)
        run_state.open_run(self.root, batch=[GREEN], goal="g")
        for n in (1, 2):
            path = base._write(self.root, f"verdicts/reject-{n}.txt", base.REJECT)
            done = subprocess.run(
                [sys.executable, str(SCRIPTS / "critic.py"), "record", "--unit", GREEN,
                 "--from-verdict", str(path), "--reviewer", REJECTER, "--author", AUTHOR,
                 "--brief", self.fp[GREEN], "--tier", "full", "--root", str(self.root)],
                capture_output=True, text=True, timeout=300, check=False)
            self.assertEqual(0, done.returncode, done.stdout + done.stderr)
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
        before = len(self._rows(GREEN))
        rc, out, err = self._accept(GREEN, f"qa-seat-{GREEN}-r2")
        self.assertEqual(2, rc, out + err)
        self.assertIn(REJECTER, err)
        self.assertIn(self.bug, err)
        self.assertEqual(before, len(self._rows(GREEN)), "a verdict was recorded")
        self.assertEqual("Review", base._status(self.root, GREEN))

    def test_no_reviewer_defaults_to_the_one_who_rejected(self) -> None:
        """MUTANT: no default, so `lane accept` refuses for want of --reviewer."""
        rc, out, err = self._accept(GREEN)
        self.assertEqual(0, rc, out + err)
        self.assertIn(f"--reviewer defaults to {REJECTER}", out + err)
        row = self._rows(GREEN)[-1]
        self.assertEqual(["APPROVE", REJECTER], [row[1], row[2]])
        self.assertEqual("Done", base._status(self.root, GREEN))

    def test_the_rejecting_id_and_an_uncarried_unit_are_accepted_as_before(self) -> None:
        """The control: the id that rejected, given bare, records under its seat group, and a
        unit never carried takes any reviewer the seat check takes."""
        rc, out, err = self._accept(GREEN, f"qa-seat-{GREEN}-r1")
        self.assertEqual(0, rc, out + err)
        self.assertEqual(REJECTER, self._rows(GREEN)[-1][2])
        rc, out, err = self._accept(BUG, "qa-seat-anyone", author="bug-builder")
        self.assertEqual(0, rc, out + err)
        self.assertEqual("qa-seat-anyone (qa)", self._rows(BUG)[-1][2])


if __name__ == "__main__":
    unittest.main()
