# US0426: reference-sprint.md states the plan critic has less information than the builder, and that Ponytail's rate is not evidence here

> **Status:** Done
> **Delivers:** RFC0050
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-sprint.md
> **Epic:** EP0158
> **Points:** 2

## User Story

**As a** reader of reference-sprint.md
**I want** it to state that the plan critic has strictly less information than the builder
**So that** a plan-time finding is trusted only as far as its evidence reaches

## Acceptance Criteria

### AC1: the document states the plan critic's information limit

- **Given** reference-sprint.md
- **When** a reader asks how far to trust a plan-time finding
- **Then** it carries a `## What the plan critic cannot see` section stating that the critic has strictly LESS information than the builder will have, so its findings are cheaper to act on but more speculative
- **Verify:** grep '## What the plan critic cannot see' .claude/skills/sdlc-studio/reference-sprint.md
- **Verified:** yes (2026-07-24)

### AC2: Ponytail's published rate is recorded as not evidence here

- **Given** the borrowed decision ladder
- **When** a reader meets the technique
- **Then** the document states that Ponytail's gains are self-reported over 12 tasks on one repository with no control methodology, so the technique is adopted on its reasoning and must be re-measured here - never cited as an established rate. The check anchors on `Ponytail`, not on `self-reported`: that phrase already appears at reference-sprint.md:581 about harness telemetry, so greping it would have passed before the section was written - caught by the ledger, not by the pre-check, which tested only the other anchor
- **Verify:** grep 'Ponytail' .claude/skills/sdlc-studio/reference-sprint.md
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
