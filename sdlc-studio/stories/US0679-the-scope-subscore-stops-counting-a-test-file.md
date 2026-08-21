# US0679: The scope subscore stops counting a test file present only because the Affects convention requires it

> **Status:** Draft
> **Delivers:** CR0549
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/scripts/tests/test_route.py
> **Epic:** EP0217
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The scope subscore stops counting a test file present only because the Affects convention requires it
**So that** CR0549 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a unit whose `Affects` names a production file and the test file the repository's own convention requires beside it, when `scope` is computed, then the conventional test file does not inflate the subscore - either excluded, or weighted separately and named as such
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::ScopeSubscoreTests::test_a_conventional_test_file_does_not_inflate_scope
- [ ] **AC2** Given a unit whose subject IS a test file - a story about test scaffolding - when `scope` is computed, then that file DOES count, because there the test file is the work rather than the convention. The paired control that stops the fix becoming a blanket exclusion
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::ScopeSubscoreTests::test_a_test_file_that_is_the_subject_still_counts

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
