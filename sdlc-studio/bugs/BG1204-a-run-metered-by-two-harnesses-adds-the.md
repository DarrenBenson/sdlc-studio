# BG1204: A run metered by two harnesses adds the supplied delegated totals in full, even over a reading that already holds delegated spend

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, changelog.d/BG1204.md
> **Evidence:** US0991 round-1 verdict, scratchpad run5/US0991-verdict-r1.txt.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T12:39:24Z

## Summary

2026-11-04, US0991's review (pre-existing, re-probed at b8b7f417). With a Claude main-thread session and an opencode session stamped subagents True, `run_token_total` gives `includes_subagents` False (`run_state.py`:1526, an all() over the meters), so supplied delegated totals are added on top of the opencode reading and may count that spend twice, while the basis calls the total a lower bound. Delegated records name no session, so they cannot yet be split by harness.

## Steps to Reproduce

1. A run with one Claude session (main thread only) and one opencode session stamped subagents True, plus a supplied delegated total.
2. `run_token_total` adds the whole delegated total.

## Proposed Fix

Tag each delegated record with the session or harness it was spent under, and add it only to a reading that cannot see it.

## Acceptance Criteria

- [ ] **AC1** A delegated total is not added over a session whose reading holds delegated spend, in a run metered by two harnesses.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py

## Impact

A mixed-harness run can overstate its tokens.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
