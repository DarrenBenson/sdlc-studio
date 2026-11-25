"""BG1449: `lane accept` records a REJECT when the unit's self-check is stale.

Under `review.author_self_check: block`, `lane accept` refused every verdict on a unit whose
Affects changed after its recorded self-check, a REJECT as well as an APPROVE. A REJECT moves
nothing and is the finding the repair answers, so refusing it lost the review and left the
reviewer's findings nowhere. Now the REJECT is recorded with the stale self-check named, and
nothing moves; an APPROVE, which would move the unit, is still refused.

The cases run on `test_lane_accept`'s throwaway repository: `sprint.py lane land` lands the
round for real, a commit to the unit's Affects on the root with no landing makes its
self-check stale, and `critic.py record` runs through its entry point.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/lanes.py
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_lane_accept as base  # noqa: E402 - the lane accept fixture and its helpers

GREEN, APPROVE, REJECT = base.GREEN, base.APPROVE, base.REJECT
critic = base.critic


class LaneAcceptRejectStaleTests(unittest.TestCase):

    # the fixture and helpers of `test_lane_accept`, without collecting its cases a second time
    setUp = base.LaneAcceptTests.setUp
    tearDown = base.LaneAcceptTests.tearDown
    _accept = base.LaneAcceptTests._accept
    _rows = base.LaneAcceptTests._rows
    _scripts = base.LaneAcceptTests._scripts
    _land_round = base.LaneAcceptTests._land_round
    _landed_fp = base.LaneAcceptTests._landed_fp
    _brief = base.LaneAcceptTests._brief

    def _stale(self, mode: str = "block") -> tuple[str, dict]:
        """Land round one under `mode`, then commit to the unit's Affects with no landing: the
        saved brief's fingerprint and the self-check that no longer covers the diff."""
        config = base._write(self.root, "sdlc-studio/.config.yaml",
                             f"review:\n  author_self_check: {mode}\n")
        gitutil.git(["add", "--", str(config)], self.root)
        gitutil.git(["commit", "-q", "-m", "chore: the self-check gate blocks"], self.root)
        landed = self._land_round("A = 2\n", f"feat({GREEN}): a is two")
        self.assertEqual(landed.returncode, 0, landed.stdout + landed.stderr)
        saved = self._landed_fp(landed)
        base._write(self.root, "src/a.py", "A = 20\n")
        gitutil.git(["commit", "-q", "-m", f"fix({GREEN}): a is twenty", "--", "src/a.py"],
                    self.root)
        stale = critic.read_self_checks(self.root)[-1]
        self.assertTrue(critic.self_check_gap(self.root, GREEN), "premise: the self-check is stale")
        return saved, stale

    def test_a_reject_on_a_stale_self_check_is_recorded_and_moves_nothing(self) -> None:
        """MUTANTS: refuse every verdict under `block` (the defect); record a REJECT without
        naming the stale self-check."""
        saved, stale = self._stale()
        self.calls.clear()
        rc, out, err = self._accept(GREEN, REJECT)
        self.assertEqual(rc, 1, out + err)
        self.assertIn(f"{GREEN}: REJECT recorded, round 1; nothing was moved", out, err)
        self.assertEqual(self._scripts(), ["critic.py record"], "a REJECT ran more than the record")
        self.assertEqual(self._rows(GREEN)[-1][1:6:4], ["REJECT", saved])
        self.assertEqual(base._status(self.root, GREEN), "Review")
        said = " ".join(err.split())
        self.assertIn(f"WARNING {GREEN}: the self-check recorded for {GREEN} on {stale['date']} "
                      f"is stale", said)
        # the warning comes before the record answers, so it says where the REJECT goes, with
        # no space before its semicolon
        self.assertIn(f"is the brief of; a REJECT moves nothing, so it goes to `critic.py "
                      f"record` (review.author_self_check: block refuses an APPROVE)", said)

    def test_an_approve_on_a_stale_self_check_is_still_refused(self) -> None:
        """The control beside the REJECT. MUTANT: skip the refusal for every verdict."""
        _saved, stale = self._stale()
        self.calls.clear()
        rc, out, err = self._accept(GREEN, APPROVE)
        self.assertEqual(rc, 2, out + err)
        self.assertEqual(self.calls, [], "lane accept ran a script on a stale self-check")
        self.assertFalse(critic.verdicts_path(self.root).exists(), "a verdict was recorded")
        self.assertEqual(base._status(self.root, GREEN), "Review")
        self.assertIn(f"the self-check recorded for {GREEN} on {stale['date']} is stale", err)
        self.assertIn("review.author_self_check: block", err)

    def test_a_reject_whose_blocking_quotes_no_finding_reaches_the_records_own_refusal(self):
        """A REJECT whose BLOCKING line quotes no ISSUES finding is still a REJECT: the stale
        self-check does not refuse it, so the record's own format refusal names the one-line
        fix rather than sending the operator to land the unit again. MUTANT: read the verdict
        through the strict parser, whose BLOCKING check raises."""
        self._stale()
        self.calls.clear()
        rc, out, err = self._accept(GREEN, "VERDICT: REJECT\nISSUES: [new] the gate lets a red "
                                           "unit through\nBLOCKING: a finding never raised\n")
        self.assertNotEqual(rc, 0, out + err)
        self.assertEqual(self._scripts(), ["critic.py record"], "the record never judged it")
        self.assertNotIn(f"land {GREEN} again", err)
        self.assertIn("`critic.py record` exited", err)
        self.assertIn("BLOCKING", err)
        self.assertFalse(critic.verdicts_path(self.root).exists(), "a verdict was recorded")
        # the warning printed before the refusal claims no record. MUTANT: say it is recorded
        said = " ".join(err.split())
        self.assertIn("a REJECT moves nothing, so it goes to `critic.py record`", said)
        self.assertNotIn("recorded (review.author_self_check", said)
        self.assertLess(said.index("goes to `critic.py record`"),
                        said.index("`critic.py record` exited"))

    def test_report_mode_does_not_say_block_refuses_a_reject(self) -> None:
        """Under `report` the stale self-check is a warning for every verdict; for a REJECT it
        says `block` records it too, since that is what `block` now does. MUTANT: keep the old
        "`block` refuses the verdict" wording for a REJECT."""
        _saved, stale = self._stale("report")
        rc, out, err = self._accept(GREEN, REJECT)
        self.assertEqual(rc, 1, out + err)
        said = " ".join(err.split())
        self.assertIn(f"WARNING {GREEN}: the self-check recorded for {GREEN} on {stale['date']} "
                      f"is stale", said)
        self.assertNotIn("`block` refuses the verdict", said)
        self.assertIn("`block` records a REJECT too and refuses an APPROVE", said)
        # the report-mode clause keeps its one space after "of", as the block one has none
        self.assertIn("is the brief of (review.author_self_check: report;", said)

    def test_an_unreadable_verdict_on_a_stale_self_check_is_refused(self) -> None:
        """A verdict file whose block names no verdict is read as no REJECT, so the stale
        self-check still refuses it rather than recording an unknown verdict."""
        self._stale()
        self.calls.clear()
        rc, out, err = self._accept(GREEN, "no verdict here\n")
        self.assertEqual(rc, 2, out + err)
        self.assertEqual(self.calls, [], "lane accept ran a script on an unreadable verdict")
        self.assertIn("review.author_self_check: block", err)


if __name__ == "__main__":
    unittest.main()
