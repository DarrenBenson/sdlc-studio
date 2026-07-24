# US0370: record the AC-correction cases as AC defects

> **Status:** Draft
> **Delivers:** CR0365
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0129
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-verify.md

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: an AC corrected rather than met is recorded as an AC defect

- **Given** a story whose acceptance criterion was found wrong and amended during delivery, as US0375's was
- **When** the unit is closed
- **Then** the amendment is recorded as an AC DEFECT distinct from an ordinary revision - a criterion that specified the wrong behaviour is a spec failure, and counting it as a normal edit hides the most expensive class of defect this project has found
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::AcDefectTests::test_an_amended_criterion_is_recorded_as_an_ac_defect

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
