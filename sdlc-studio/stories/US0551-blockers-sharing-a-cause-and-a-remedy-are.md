# US0551: Blockers sharing a cause and a remedy are filed as one artefact listing the units it covers

> **Status:** Draft
> **Delivers:** CR0495
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0188
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: blockers sharing a cause are filed as one artefact

- **Given** a batch whose units are all blocked by one missing approval
- **When** the bounded exit files them
- **Then** one artefact is filed naming the cause and listing every unit it covers, rather than one per unit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::FileAndCloseGroupingTests::test_one_cause_files_one_artefact_listing_its_units

### AC2: genuinely different remedies stay separate

- **Given** a batch holding two blockers with different causes and remedies
- **When** the bounded exit files them
- **Then** two artefacts are filed, so grouping does not merge unrelated blockers
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::FileAndCloseGroupingTests::test_distinct_causes_are_filed_separately

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
