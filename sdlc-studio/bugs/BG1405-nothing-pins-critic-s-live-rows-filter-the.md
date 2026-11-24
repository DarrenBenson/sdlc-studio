# BG1405: Nothing pins critic's 'live rows' filter, the carried-refusal wording or the stacked-criterion naming, and the BG1339 rejoinder path guards are untested

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_rejoinder_from_ledger.py, .claude/skills/sdlc-studio/scripts/tests/test_rejoinder_and_live_rows_pin.py, changelog.d/BG1405.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: review integrity and accept
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:12:19Z

## Summary

BG1340's live-rows filter and carried-refusal text, BG1343's 'naming each stacked criterion' (no test stacks more than one), and BG1339's rejoinder pick by verdict-file path are unpinned. A plain QA brief re-run after a rejoinder is wrongly refused and one guard is untested.

## Steps to Reproduce

Brief QA again after a rejoinder.

## Proposed Fix

Add the tests and fix the refusal.

## Acceptance Criteria

- [ ] **AC1** Given a carried unit, a stacked-criterion unit and a rejoinder, when briefed, then each behaviour is pinned and a plain QA re-run is accepted. Fails on: the re-run refused.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rejoinder_and_live_rows_pin.py::RejoinderAndLiveRowsPinTests

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. Unpinned filters and guards.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
