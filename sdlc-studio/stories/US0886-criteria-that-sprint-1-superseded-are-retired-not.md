# US0886: Criteria that Sprint 1 superseded are retired, not left red

> **Status:** In Progress
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_autosprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_retired.py
> **Epic:** EP0261
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator preparing a release
**I want** the criteria Sprint 1 superseded (D0259) retired along with their stub tests
**So that** the release verify lane is not red on promises we retired on purpose (BG0749)

## Acceptance Criteria

- **AC1:** Given every criterion D0259 lists, when `verify_ac` runs over those units, then none reads FAIL for an all-skipped selection: each is retired with a Verified line naming the unit that superseded it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_retired.py::RetiredCriteriaTests::test_no_d0259_criterion_reads_red
- **AC2:** Given the test suites, then the skipped stub tests those criteria named are deleted
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_retired.py::RetiredCriteriaTests::test_the_stub_tests_are_gone

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Created via `new` (deterministic) |
