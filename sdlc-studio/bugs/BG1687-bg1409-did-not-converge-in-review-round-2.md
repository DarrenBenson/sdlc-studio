# BG1687: BG1409 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/scripts/tests/test_land_empty_replay.py, changelog.d/BG1409.md
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T17:59:18Z

## Summary

BG1409 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The branch where the replay's rebase drops the scratch commit (main already holds the staged change) but ends on a builder commit main does not hold is pinned by no test, though the comment and the changelog say the scratch is "taken back out only when it is the commit the rebase ended on" (lanes.py:367-370, changelog.d/BG1409.md:10-11): the mutant `if HEAD != target: reset --soft HEAD~1` in place of the author check at lanes.py:369 SURVIVED `test_land_empty_replay.py` and `test_lane_land.py` (30 passed). Through `sprint.py lane land` with a builder commit "fix: b is three, in the lane" and main holding the lane's staged `A = 2`, HEAD lands the builder's commit as its own (main reads "fix: b is three, in the lane" over "chore: main moves src/a.py"), while under the mutant that commit is taken back out and its change lands as "feat(US0101): a is two", the builder's commit gone; RULINGS: Round 1, "The replay now takes its scratch commit back out only when the message HEAD ends on equals the mark": CLOSED. The reviewer's scenario re-run through `sprint.py lane land` (a `prepare-commit-msg` hook appending a trailer, main moved, no builder commit) exits 0 at HEAD, the pre-commit hook ran once and main's head is "feat(US0101): a is two" over main's commit with no replay commit on main, while the round-1 commit 09cf0766 still lands "lane land: the staged change, replayed (...)" with no hook run. It also holds with GIT\_AUTHOR\_NAME and GIT\_AUTHOR\_EMAIL exported to the land, since the rebase keeps the scratch's author. "The half of the fix that drops a builder commit whose change main holds in a different commit": CLOSED, `test_a_builder_commit_main_holds_in_a_different_commit_is_dropped`, the author's `--empty=keep` mutant replayed killed. My mutants KILLED: the scratch told by its committer email, and the mark given as the author name while the email is compared. AC1 is green through `verify_ac.py run --id BG1409 --dry-run` (pass=1). Claims TRUE by execution: the replay rebases as the later rebase does, a builder commit main holds is dropped by either route, and with such a hook the lane's own commit lands through the hooks. Probes were re-run on ed47dfd4, which landed after this brief, with the same results\\\; line numbers are ed47dfd4's. Unit diff judged: `_carry`, `test_land_empty_replay.py` and changelog.d/BG1409.md\\\; `test_lane_land.py` is declared but its changed hunk is BG1399's.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1409 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1409 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The branch where the replay's rebase drops the scratch commit (main already holds the staged change) but ends on a builder commit main does not hold is pinned by no test, though the comment and the changelog say the scratch is "taken back out only when it is the commit the rebase ended on" (lanes.py:367-370, changelog.d/BG1409.md:10-11): the mutant `if HEAD != target: reset --soft HEAD~1` in place of the author check at lanes.py:369 SURVIVED `test_land_empty_replay.py` and `test_lane_land.py` (30 passed). Through `sprint.py lane land` with a builder commit "fix: b is three, in the lane" and main holding the lane's staged `A = 2`, HEAD lands the builder's commit as its own (main reads "fix: b is three, in the lane" over "chore: main moves src/a.py"), while under the mutant that commit is taken back out and its change lands as "feat(US0101): a is two", the builder's commit gone
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1409 AC1 still passes: Given a builder commit that main already holds, when the lane lands, then no empty commit results. Fails on: an empty commit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_land_empty_replay.py::LandEmptyReplayTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (run twenty-one orchestrator) | Fixed: BG1409 was reviewed again in round three under D0572 and its qa seat (Sam Eriksson) approved, closing the round-two findings this bug carried; BG1409 is Fixed |
