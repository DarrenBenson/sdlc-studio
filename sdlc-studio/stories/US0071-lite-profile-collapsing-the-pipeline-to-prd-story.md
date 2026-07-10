# US0071: Lite profile collapsing the pipeline to PRD, story, implement

> **Status:** Done
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0016
> **Persona:** Maya Okafor (solo founder-engineer)
> **Source:** CR-0176

## User Story

**As a** solo founder-engineer on a small repo
**I want** a lite profile that collapses the pipeline to PRD, story, implement
**So that** I get the discipline without accumulating more workflow markdown than source

## Acceptance Criteria

### AC1: No epic/plan ceremony, discipline intact

- **Given** a lite-profile project
- **When** it runs PRD then story then implement
- **Then** zero epic/plan artefacts are created and no command nags about their absence, while
  executable-AC verification and reconcile work identically
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lite_profile.py
- **Verified:** yes (2026-07-10)

### AC2: Promotable to full

- **Given** a lite fixture project
- **When** it upgrades to the full profile
- **Then** epics are inserted above existing stories and reconcile is clean
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lite_profile.py -k promote
- **Verified:** yes (2026-07-10)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
