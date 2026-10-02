# BG0894: The close carries a lessons status line as a known issue ('lessons: 0 hit(s) from cited REJECTs')

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_close_gap_status_line.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RPT0014 Known issues handed over, last row
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T07:27:55Z

## Summary

When retro-extract hits an error, the close hands over every line of its result as a known issue, so RPT0014 lists a close gap reading 'lessons: 0 hit(s) from cited REJECTs', a status line with no problem in it, beside the real one (LC-005's CR not filed).

## Steps to Reproduce

1. A close whose retro-extract step fails to file one graduation CR. 2. Read the report's known issues -> a second close-gap row holding the lessons summary line.

## Proposed Fix

Carry only the step's failures as known issues, not its status summary.

## Acceptance Criteria

- [ ] **AC1** Given a close whose retro-extract step fails to file one CR, when the page is derived, then exactly one retro-extract close gap is listed (the failure) and no row holds the 'N hit(s) from cited REJECTs' summary. Fails on: the current code lists both
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close_gap_status_line.py::CloseGapStatusLineTests::test_only_the_failure_is_a_close_gap

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
