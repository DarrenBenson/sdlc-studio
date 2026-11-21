# BG1674: No test pins card-not-utf8's severity split (a warning for persona cards, an error for seat cards) or the exit code validate.py seats gives for it

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T16:56:02Z

## Summary

US1057's round-three engineering review (RUN-01M7VNR0) found that the severity split the repair commit claims for card-not-utf8 is unpinned: a mutant reading seat cards at warning (validate.py around 1764) survives CardNotUtf8Tests, `test_persona_review_owed.py`, `test_goal_review_persona_block.py`, `test_persona_standard_mode.py` and the rest of `test_validate.py`, so the exit code of validate.py seats on such a card can change unnoticed.

## Steps to Reproduce

Change the seat-card card-not-utf8 severity in validate.py from error to warning and run the persona and validate test modules: all pass.

## Proposed Fix

Pin both severities and validate.py seats' exit code on a seat card holding a 0xff byte, beside a persona card that only warns.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US1057's round-three engineering review (RUN-01M7VNR0) found that the severity split the repair commit claims for card-not-utf8 is unpinned: a mutant reading...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Change the seat-card card-not-utf8 severity in validate.py from error to warning and run the persona and validate test modules: all pass.
- [ ] **AC3** The proposed fix lands, pinned by a test: Pin both severities and validate.py seats' exit code on a seat card holding a 0xff byte, beside a persona card that only warns.

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. The card-not-utf8 severity split works; only a test pinning it is missing. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
