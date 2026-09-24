# US0903: A recurring lesson asks for a fix or a retirement, not another check

> **Status:** Draft
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py
> **Epic:** EP0262
> **Points:** 1
> **Persona:** Maya Okafor

## User Story

**As a** team learning from each sprint
**I want** a lesson that keeps recurring to raise a request to fix the failing path first, and to name what any check it proposes retires
**So that** learning stops ratcheting the process: a repeat produces a fix, and a new check arrives only in exchange for an old one

## Acceptance Criteria

- **AC1:** Given a class hit twice after it was recorded, when `sprint close` runs, then the CR it files is titled `Prevent or retire lesson <id> (<class>)`, not `Turn lesson <id> ... into a check`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py::RetiringGraduationTests::test_the_graduation_cr_asks_to_prevent_or_retire
- **AC2:** Given that CR, then its first criterion requires fixing the code path its recorded hits name, and any criterion that proposes a check requires it to name the lane, refusal, baseline or pin it retires; no criterion asks for a new check on its own
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lessons.py::RetiringGraduationTests::test_the_cr_puts_the_fix_first_and_names_what_a_check_retires

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `batch` (deterministic); body trimmed to the lean story shape |
