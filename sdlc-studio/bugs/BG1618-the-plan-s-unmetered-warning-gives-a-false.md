# BG1618: The plan's unmetered warning gives a false reason on a re-plan, one of its test assertions cannot fail, and a fallback sentence is reached by no test

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, changelog.d/BG1618.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** run eighteen, 2026-11-19: sdlc-studio/reviews/verdicts/BG1605/6b1af452cfb0-6934249c.txt and sdlc-studio/reviews/verdicts/BG1605/90ab5c4b4795-ffc45d3f.txt
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T14:54:55Z

## Summary

Non-blocking findings from both seats' reviews of the plan's unmetered warning (run eighteen): on a re-plan the warning states a reason that is not the cause; one assertion in its test holds whatever the code does; and no test reaches the warning's fallback sentence.

## Steps to Reproduce

Plan a run with no transcript store, then plan again: the warning's reason no longer matches why no stamp was taken.

## Proposed Fix

Derive the reason on each plan, replace the vacuous assertion with one that fails on a wrong reason, and add a case for the fallback.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Non-blocking findings from both seats' reviews of the plan's unmetered warning (run eighteen): on a re-plan the warning states a reason that is not the cause...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Plan a run with no transcript store, then plan again: the warning's reason no longer matches why no stamp was taken.
- [ ] **AC3** The proposed fix lands, pinned by a test: Derive the reason on each plan, replace the vacuous assertion with one that fails on a wrong reason, and add a case for the fallback.

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because the change it asks for is a wording preference, not a defect a user meets. A false reason on a re-plan warning.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
