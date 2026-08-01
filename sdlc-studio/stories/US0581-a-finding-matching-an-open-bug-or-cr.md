# US0581: A finding matching an open Bug or CR is annotated with that id automatically and never blocks

> **Status:** Draft
> **Delivers:** CR0512
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0194
> **Points:** 3

## User Story

**As a** reviewer
**I want** a finding an open artefact already records annotated with its id
**So that** re-finding known debt is not reported as a review result

## Acceptance Criteria

### AC1: a finding an open artefact already records is annotated with its id

- **Given** an open Bug whose summary describes the same defect a finding reports
- **When** the finding is recorded
- **Then** it carries that Bug's id and is classified PRE-EXISTING without the reviewer being asked
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::KnownFindingTests::test_a_covered_finding_is_annotated_with_its_id

### AC2: an annotated finding never blocks

- **Given** a finding annotated with an open artefact id
- **When** the coverage gate reads the verdict
- **Then** the unit is covered, because re-finding known debt is not a review result
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::KnownFindingTests::test_an_annotated_finding_does_not_block

### AC3: a finding no artefact covers is left alone

- **Given** a finding matching nothing in the open backlog
- **When** it is recorded
- **Then** it carries no id and keeps the classification the reviewer gave it, so the matcher cannot quietly absolve a genuinely new defect
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::KnownFindingTests::test_an_uncovered_finding_is_untouched

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
