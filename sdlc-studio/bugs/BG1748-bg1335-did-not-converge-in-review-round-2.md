# BG1748: BG1335 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_decision.py, changelog.d/BG1335.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M87B5M - raised during the run, 2026-11-25T04:04:27Z

## Summary

BG1335 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] a unit with two blocking decisions loses its block when the first is answered, so `decision list` and status disagree about it (sprint.py:14664-14666). The resolve drops the unit from `blocked_units` by `norm_id` whenever any one of its decisions is answered, and since the round-two store now holds each unit only once, nothing is left to carry the second question's block. Probed through `sprint.main` and `status.main`: `defer --block` twice on BG0001, then `decision resolve --index 1`, leaves `blocked_units` as [] and `status pillars` with no Blocked line. Yet `decision list` still prints "[1] BG0001 (Open, BLOCKED on the run state)" for the unanswered question, because `_decision_rows` also reads the decision's own `blocked` flag. The code's own comment says the block "goes with its answered question" (sprint.py:14664), and the round-two changelog says resolving "clears that unit's block alone". So the bug reads as an ordinary open unit on the run state and the dashboard while one of its blocking questions is still open, which is the failure AC1 exists to prevent, and no test holds two blocking decisions on one unit; [pre-existing] `deferred_units` is cleared the same way, on the first of a unit's decisions to be answered (`still_deferred`, present at the base 74903e754 sprint.py:14319). No open bug covers it; RULINGS: CLOSED "the new status line and the defer message print a held unit through `sdlc_md.norm_id`": both now print through `display_id`. The new test shows `BG-01ABCDEH` and never `BG01ABCDEH`, and my mutants restoring the key in the status line and in the defer message were killed. CLOSED "the close's showing of a held unit is unpinned": test\_the\_close\_shows\_a\_held\_unit\_with\_its\_status\_as\_blocked kills my no-root mutant. CLOSED "the resolve filter that keeps other units' blocks is unpinned": test\_resolving\_one\_decision\_keeps\_every\_other\_units\_block kills my clear-every-block mutant. CLOSED "`blocked_units` stores the id as typed and de-duplicates it by raw text": the store now de-duplicates by `norm_id` in the file's spelling, and status de-duplicates an older run state. My mutants for raw-text dedupe, storing as typed, and no status dedupe were each killed. The new finding is not a round-one finding moved. It was in the round-one diff too, and I missed it then. The round-two dedupe now covers spellings as well, which does not change it. verify\_ac --dry-run gives 1 of 1 passing. The tree was clean after my pass.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1335 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1335 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] a unit with two blocking decisions loses its block when the first is answered, so `decision list` and status disagree about it (sprint.py:14664-14666). The resolve drops the unit from `blocked_units` by `norm_id` whenever any one of its decisions is answered, and since the round-two store now holds each unit only once, nothing is left to carry the second question's block. Probed through `sprint.main` and `status.main`: `defer --block` twice on BG0001, then `decision resolve --index 1`, leaves `blocked_units` as [] and `status pillars` with no Blocked line. Yet `decision list` still prints "[1] BG0001 (Open, BLOCKED on the run state)" for the unanswered question, because `_decision_rows` also reads the decision's own `blocked` flag. The code's own comment says the block "goes with its answered question" (sprint.py:14664), and the round-two changelog says resolving "clears that unit's block alone". So the bug reads as an ordinary open unit on the run state and the dashboard while one of its blocking questions is still open, which is the failure AC1 exists to prevent, and no test holds two blocking decisions on one unit
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [pre-existing] `deferred_units` is cleared the same way, on the first of a unit's decisions to be answered (`still_deferred`, present at the base 74903e754 sprint.py:14319). No open bug covers it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** BG1335 AC1 still passes: Given an open run with a bug in its batch, when `sprint.py decision defer --unit <bug> --block` runs, then the bug is shown as blocked on the run state, in `sprint.py decision list` and in status, by a field a bug may carry. Fails on: the defer printing that it could not block and leaving the bug indistinguishable from an open unit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_decision.py::DeferBlockTests::test_a_deferred_bug_is_shown_blocked

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
