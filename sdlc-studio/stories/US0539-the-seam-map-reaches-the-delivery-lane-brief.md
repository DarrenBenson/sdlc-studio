# US0539: The seam map reaches the delivery lane brief and the review brief, so a lane is told which neighbouring property it must not regress

> **Status:** Done
> **Delivers:** CR0468
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0184
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an agent delivering one unit of a batch
**I want** the seam map in my lane brief and in the review brief
**So that** I know which neighbouring property I must not regress, which reading my own unit can never tell me

## Acceptance Criteria

### AC1: the seam map reaches the lane brief and the review brief

- **Given** a batch whose seam map names a pair
- **When** a delivery lane is briefed and a review brief is produced
- **Then** each names the neighbouring property this unit must not regress, asserted on the brief's content rather than on the map's existence
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SeamBriefTests::test_the_brief_names_the_neighbouring_property
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
