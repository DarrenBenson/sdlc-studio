# US0517: A finding's Affects names where the fix will land rather than where the evidence was read, and includes the test file

> **Status:** Review
> **Delivers:** CR0458
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Epic:** EP0178
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** planner sizing a batch from what its units declare
**I want** a finding's Affects to name where the fix will land, including the test file
**So that** collision analysis and the engagement floor read a real footprint rather than the place the evidence happened to be read

## Acceptance Criteria

### AC1: Affects names the fix site rather than the evidence site

- **Given** a finding whose evidence sits in a different file from its fix
- **When** it is filed
- **Then** the Affects names the paths the fix will touch, and the evidence location is recorded as evidence rather than as footprint
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::AffectsFootprintTests::test_affects_names_the_fix_site
- **Verified:** yes (2026-07-28)

### AC2: a source file's companion test is included when one exists by convention

- **Given** a finding whose fix lands in a source file with a conventional test partner
- **When** it is filed
- **Then** the test file is in the Affects, because a fix lands in both and a footprint naming one is understated
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::AffectsFootprintTests::test_the_companion_test_is_included
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
