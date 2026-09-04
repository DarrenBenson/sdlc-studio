# CR-0563: verify_ac run prints the near-miss hint when a collected file's node is absent, so the RED first run of a mistyped selector names what was meant

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Date:** 2026-09-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0643 lets a not-yet-written test file, and its accepted trade is that a selector with the class AND the method mistyped (WrongClass::`test_methd)` now files and is reported RED on the first run - where the filer used to refuse it with the near miss named. The first run today prints FAIL plus pytest's not-found line and no hint. Found by the product seat in BG0643's delivery review on 2026-09-04.

## Impact

A person who mistyped both halves of a selector is told the test is not found and nothing else, on the one run that could have named what they meant.

## Acceptance Criteria

- [ ] Given a criterion whose pytest selector names a collected file and an absent node, when `verify_ac` run reports it FAIL, then the report line carries `selector_near_miss`'s hint when there is one, beside the not-found text

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-04 | sdlc-studio | Raised |
