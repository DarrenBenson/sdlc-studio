# US0207: Mark RFC0034 superseded by RFC0038, cross-link both and update the rfc index

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/rfcs/RFC0034-sprint-sizing-velocity-and-estimate-calibration-close-the.md, sdlc-studio/rfcs/_index.md
> **Epic:** EP0071
> **Points:** 2

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: RFC0034's D1 and D5 rows are marked overtaken/superseded by RFC0038 with in-file cross-links in

- **Given** RFC0034's D1/D5 rows did not record their supersession by RFC0038
- **When** both rows are marked superseded with cross-links in both RFCs and a revision row in each
- **Then** RFC0034's D1 and D5 rows are marked overtaken/superseded by RFC0038 with in-file cross-links in both RFCs and a revision row in each
- **Verify:** grep "Superseded by .RFC-0038" sdlc-studio/rfcs/RFC0034-sprint-sizing-velocity-and-estimate-calibration-close-the.md
- **Verified:** yes (2026-07-17)

### AC2: RFC0034's header records the partial supersession (D2-D4 remain live) or the file is marked

- **Given** RFC0034's header did not record the partial supersession
- **When** a header note records that D1/D5 are superseded while D2-D4 remain live
- **Then** RFC0034's header records the partial supersession (D2-D4 remain live) or the file is marked Superseded with the surviving decisions re-homed
- **Verify:** grep "Partially superseded by:" sdlc-studio/rfcs/RFC0034-sprint-sizing-velocity-and-estimate-calibration-close-the.md
- **Verified:** yes (2026-07-17)

### AC3: The rfcs index summary reflects the supersession state

- **Given** the rfcs index summary did not reflect the supersession
- **When** the RFC0034 index row is annotated with the partial-supersession state
- **Then** The rfcs index summary reflects the supersession state
- **Verify:** grep "D1 and D5 superseded by RFC-0038" sdlc-studio/rfcs/_index.md
- **Verified:** yes (2026-07-17)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
