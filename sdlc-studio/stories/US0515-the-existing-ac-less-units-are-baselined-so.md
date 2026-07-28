# US0515: The existing AC-less units are baselined so the new rule blocks a new one without blocking on the backlog it reveals

> **Status:** Review
> **Delivers:** CR0459
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Epic:** EP0178
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** maintainer introducing a rule over a corpus that already breaks it
**I want** the existing criteria-less units baselined
**So that** a new rule blocks a new instance without blocking on the backlog it reveals

## Acceptance Criteria

### AC1: a pre-existing criteria-less unit is recorded and does not block

- **Given** units already terminal with no criteria when the rule is introduced
- **When** the check runs
- **Then** each recorded instance reports as known debt rather than failing, and the record is captured from the checker's own output rather than hand-written
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::BugCriteriaTests::test_a_baselined_unit_reports_as_debt
- **Verified:** yes (2026-07-28)

### AC2: a new instance still fails, and removal from the baseline is one-way

- **Given** a unit not in the baseline reaching a terminal status with no criteria
- **When** the check runs
- **Then** it fails; and an id removed from the baseline errors from then on, so the count can only fall
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::BugCriteriaTests::test_a_new_instance_still_fails
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
