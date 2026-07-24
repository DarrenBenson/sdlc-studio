# US0414: the duplicate check is advisory by default and refusable under --strict, with the escape recorded

> **Status:** Ready
> **Delivers:** CR0413
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Epic:** EP0156
> **Points:** 2

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the check is advisory by default

- **Given** a near-duplicate title and no `--strict`
- **When** `new` is invoked
- **Then** the artefact IS minted and the duplicate is reported - filing must never be blocked by a heuristic, or the heuristic becomes a reason not to file
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::DuplicateStrictTests::test_advisory_by_default_mints_and_reports

### AC2: --strict refuses and mints nothing

- **Given** the same title with `--strict`
- **When** `new` is invoked
- **Then** it exits non-zero and NO file and NO index row are written - a refusal that leaves a half-minted artefact is worse than no refusal
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::DuplicateStrictTests::test_strict_refuses_and_writes_nothing

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
