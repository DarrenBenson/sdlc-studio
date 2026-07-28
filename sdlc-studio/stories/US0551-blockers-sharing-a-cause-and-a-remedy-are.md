# US0551: Blockers sharing a cause and a remedy are filed as one artefact listing the units it covers

> **Status:** Done
> **Delivers:** CR0495
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0188
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an operator reading the discovery backlog after a bounded close
**I want** blockers sharing a cause filed as one artefact listing the units it covers
**So that** one owed sign-off does not arrive as 23 identical change requests

## Acceptance Criteria

### AC1: blockers sharing a cause are filed as one artefact

- **Given** a batch whose units are all blocked by one missing approval
- **When** the bounded exit files them
- **Then** one artefact is filed naming the cause and listing every unit it covers, rather than one per unit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::FileAndCloseGroupingTests::test_one_cause_files_one_artefact_listing_its_units
- **Verified:** yes (2026-07-28)

### AC2: genuinely different remedies stay separate

- **Given** a batch holding two blockers with different causes and remedies
- **When** the bounded exit files them
- **Then** two artefacts are filed, so grouping does not merge unrelated blockers
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::FileAndCloseGroupingTests::test_distinct_causes_are_filed_separately
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
