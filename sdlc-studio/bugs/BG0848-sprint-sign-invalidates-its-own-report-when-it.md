# BG0848: sprint sign invalidates its own report when it moves an approved unit to Done

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-09-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-29T08:37:31Z

## Summary

An approved story left at Review at close is moved to Done by `sprint sign` (as 6.0.0 intends: it awaits only the signature). The move gives that unit an elapsed time, and the report's `eu_minutes` row re-derives from it, so the report `sign` has just sealed no longer re-derives to its fingerprint: `sprint_report.py check` prints INVALIDATED straight after a clean seal. Found by a seal rehearsal on the sdlc-studio.com web run (RUN-01M3HRHY): four approved units at Review, `eu_minutes` signed 0.0 and now 2024.2 to 2107.6.

## Steps to Reproduce

In a project whose run has an APPROVE verdict on a story still at Review, run `sprint.py close`, then `sprint.py sign --report RPTxxxx --principal op`, then `sprint_report.py check --report RPTxxxx`: it prints INVALIDATED naming `eu_minutes` for each unit the sign moved. Moving those units to Done before the close gives VALID.

## Proposed Fix

Exclude from the fingerprint what the signature itself moves (the unit's status-derived elapsed time), or have the close move each approved unit to its terminal status before it derives the report, so the sign moves nothing the report digests.

## Acceptance Criteria

- [ ] **AC1** Given a run whose approved story sits at Review at close, when the run is closed and signed, then `sprint_report.py check` on the sealed report prints VALID.

## Impact

Any run that relies on the sign to finish an approved unit ends with a signed report that fails its own check in every clone, which reads as tampering. Workaround: transition approved units to Done before `sprint close`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-29 | sdlc-studio | Filed |
