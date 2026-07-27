# US0444: Docs and supersession: rewrite help/init.md and reference for the guided flow, mark RFC0019 superseded

> **Status:** Done
> **Delivers:** RFC0055
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/help/init.md, sdlc-studio/rfcs/RFC0019-authoring-autosprint-a-guardrailed-prd-to-epics-to.md
> **Epic:** EP0163
> **Points:** 2

## User Story

**As a** user meeting SDLC Studio for the first time
**I want** the init help to document the guided flow, and the old first-mile RFC marked as superseded
**So that** I can discover `init guided` from the help, and the design record shows what realised it

## Acceptance Criteria

### AC1: init help documents the guided onboarding flow

- **Given** the init help page
- **When** a user reads it
- **Then** it documents `init guided` - the one-command walk from zero to a first sprint plan
  across AGENTS.md, PRD, TRD, TSD, personas and decomposition, with resume and `--confirm`/`--skip`
- **Verify:** grep "init guided" .claude/skills/sdlc-studio/help/init.md
- **Verified:** yes (2026-07-26)

### AC2: the superseded first-mile RFC is marked as such

- **Given** RFC0019 (the earlier greenfield first-mile authoring loop), whose intent the guided
  flow now realises and generalises to brownfield
- **When** its status is read
- **Then** it is marked Superseded, so the design record points forward rather than reading as live
- **Verify:** grep "Superseded" sdlc-studio/rfcs/RFC0019-authoring-autosprint-a-guardrailed-prd-to-epics-to.md
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
