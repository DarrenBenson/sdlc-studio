# BG1500: help/retro.md says an escaped defect is charged to the seat whose latest verdict approved, in any run, leaving out the code's limit to verdicts on or before the bug's Created day

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/help/retro.md, .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_evidence.py, changelog.d/BG1500.md
> **Evidence:** Run fifteen (RUN-01M7HA6R) US1171 QA verdict 204ec71c3de6-bdf90726, 2026-11-16.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T06:11:51Z

## Summary

Run fifteen's US1171 QA seat found that help/retro.md (near line 68) says an escaped defect's charge goes to every seat whose latest verdict on the unit approved, in any run, while the code counts only verdicts recorded on or before the bug's Created day. A reader would expect a later approval to be charged with an earlier escape, which the code never does.

## Steps to Reproduce

Read help/retro.md near line 68 against the seat-evidence charge in retro.py.

## Proposed Fix

Add the on-or-before-Created limit to the help sentence, matching reference-retro.md's seat-evidence section and the code.

## Acceptance Criteria

- [ ] **AC1** Given the shipped help/retro.md, when its sentence on charging an escaped defect is read, then it says the charge goes to each seat whose latest verdict on the unit recorded on or before the bug's `Created` day approved, as reference-retro.md's seat-evidence section and `retro.py` do, and it no longer says 'in any run' without that limit. Fails on: help text that lets a reader expect a later approval to be charged with an earlier escape.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro_seat_evidence.py::HelpStatesTheChargeLimitTests::test_the_help_limits_the_charge_to_verdicts_on_or_before_the_created_day

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because the change it asks for is a wording preference, not a defect a user meets. Retro help omits a date limit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
