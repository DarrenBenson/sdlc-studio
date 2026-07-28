# US0522: A repeatedly violated lesson can propose a change request or bug for the operator to accept or decline

> **Status:** Review
> **Delivers:** CR0464
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py
> **Epic:** EP0179
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** operator who would rather have a guard than a better-worded lesson
**I want** a repeatedly violated lesson able to propose a change request or bug
**So that** the loop ends in work instead of a longer list

## Acceptance Criteria

### AC1: a lesson past the repeat threshold proposes a unit for the operator to accept or decline

- **Given** a carried lesson violated more than the configured number of times
- **When** the close runs
- **Then** it proposes a change request or bug carrying the lesson and its violations as evidence, for the operator to accept or decline
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::ProposalTests::test_a_repeated_lesson_proposes_a_unit
- **Verified:** yes (2026-07-28)

### AC2: nothing is filed without acceptance

- **Given** a proposal
- **When** the operator declines it
- **Then** no artefact is created and the decline is recorded against the lesson, so the proposal cannot recur silently
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::ProposalTests::test_a_declined_proposal_files_nothing_and_is_recorded
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
