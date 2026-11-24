# BG1449: lane accept refuses to record a REJECT when the unit's self-check is stale, though a REJECT moves nothing

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept_reject_stale.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, changelog.d/BG1449.md
> **Evidence:** Run twelve (RUN-01M7E52T) orchestrator friction log
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T05:37:55Z

## Summary

After US1155's Affects were widened post-land, `sprint lane accept --verdict <REJECT>` refused: 'the self-check recorded ... is stale'. A REJECT transitions nothing, so the staleness should block only an APPROVE; the orchestrator fell back to `critic.py record` with a hand-supplied --author.

## Steps to Reproduce

Land a unit, widen its Affects, then run `lane accept` with a REJECT verdict: refused on a stale self-check.

## Proposed Fix

Check the self-check's digest only on an APPROVE path; record a REJECT regardless.

## Acceptance Criteria

- [ ] **AC1** Given a unit with a stale self-check, when `lane accept` records a REJECT, then it is recorded and nothing moves; an APPROVE is still refused. Fails on: the REJECT refused.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept_reject_stale.py::LaneAcceptRejectStaleTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
| 2026-11-24 | orchestrator (delegate under D0545) | Affects widened for run twenty-six's SPB lane: the stale-self-check refusal lives in lib/lanes.py `_brief_of` |
