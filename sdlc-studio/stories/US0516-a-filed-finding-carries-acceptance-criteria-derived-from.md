# US0516: A filed finding carries acceptance criteria derived from its own evidence, so a lane has a contract to deliver against

> **Status:** Review
> **Delivers:** CR0458
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Epic:** EP0178
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** lane picking up a finding somebody else filed
**I want** the finding to carry acceptance criteria derived from its own evidence
**So that** the lane has a contract to deliver against instead of inferring one from a summary

## Acceptance Criteria

### AC1: a filed finding carries at least one acceptance criterion

- **Given** a finding filed with steps and a proposed fix
- **When** it is written
- **Then** the artefact carries a criterion derived from its evidence, so the engagement floor and the delivery lane both have something to read
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::FiledCriteriaTests::test_a_filed_finding_carries_a_criterion
- **Verified:** yes (2026-07-28)

### AC2: a finding whose evidence cannot support a criterion says so rather than emitting a placeholder

- **Given** a finding whose evidence is too thin to derive a criterion from
- **When** it is filed
- **Then** the artefact records that explicitly instead of carrying a scaffold that reads like content
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::FiledCriteriaTests::test_thin_evidence_is_stated_not_scaffolded
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
