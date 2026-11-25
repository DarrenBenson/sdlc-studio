# BG1746: BG1449 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept_reject_stale.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, changelog.d/BG1449.md
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M87B5M - raised during the run, 2026-11-25T03:21:38Z

## Summary

BG1449 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] a REJECT the record refuses is first announced as recorded (lanes.py:1386-1388): on a stale self-check under `block`, the malformed REJECT this repair now passes to the record prints "WARNING US0101: ... is the brief of", a space, a semicolon and "a REJECT moves nothing, so it is recorded (review.author\_self\_check: block refuses an APPROVE)", then "sprint lane accept: `critic.py record` exited 2, so US0101 was not moved: record refused: BLOCKING item ..." (probed on the test's own stale fixture), so the warning states a record that did not happen, and its concatenation prints that stray space before the semicolon, both in this unit's own message text (say the REJECT goes to the record, or warn after the record answers); RULINGS: Round-one finding "a REJECT whose BLOCKING quotes no ISSUES finding is still refused as a stale self-check" CLOSED: the verdict is read with `strict=False`, the probe shows the record's own refusal naming the BLOCKING item to fix, and the strict-parse mutant is killed by the new test. Round-one finding "under `review.author_self_check: report` the stale self-check warning still says" CLOSED: a REJECT now reads "`block` records a REJECT too and refuses an APPROVE", pinned (the old-wording mutant is killed). The changelog's new sentences are TRUE apart from the finding above, and a block with two VERDICT lines is still refused on the stale self-check as one with no readable verdict. AC1's Verify passes.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1449 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1449 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] a REJECT the record refuses is first announced as recorded (lanes.py:1386-1388): on a stale self-check under `block`, the malformed REJECT this repair now passes to the record prints "WARNING US0101: ... is the brief of", a space, a semicolon and "a REJECT moves nothing, so it is recorded (review.author\_self\_check: block refuses an APPROVE)", then "sprint lane accept: `critic.py record` exited 2, so US0101 was not moved: record refused: BLOCKING item ..." (probed on the test's own stale fixture), so the warning states a record that did not happen, and its concatenation prints that stray space before the semicolon, both in this unit's own message text (say the REJECT goes to the record, or warn after the record answers)
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1449 AC1 still passes: Given a unit with a stale self-check, when `lane accept` records a REJECT, then it is recorded and nothing moves; an APPROVE is still refused. Fails on: the REJECT refused.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept_reject_stale.py::LaneAcceptRejectStaleTests
  - **Verified:** yes (2026-11-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
