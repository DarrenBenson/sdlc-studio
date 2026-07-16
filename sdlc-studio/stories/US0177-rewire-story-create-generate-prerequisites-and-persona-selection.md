# US0177: Rewire story create/generate prerequisites and persona selection to the personas/ registry with legacy fallback

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Fable 5; agent; CR0283 delivery
> **Affects:** .claude/skills/sdlc-studio/reference-story.md, .claude/skills/sdlc-studio/help/story.md
> **Epic:** EP0049
> **Points:** 3

## User Story

**As** Maya Okafor (solo founder-engineer, the declared Primary)
**I want** story generation to read personas from the personas/ registry my persona commands actually write to
**So that** the Primary I declared shapes every story, instead of the workflow STOPping on a legacy file I never created

## Acceptance Criteria

### AC1: Prerequisites resolve the registry first

- **Given** a project whose personas live in sdlc-studio/personas/ (index.md + cards)
- **When** story create or generate checks prerequisites
- **Then** the registry is used as the persona source and the workflow proceeds
- **Verify:** grep "Resolve personas, registry first" .claude/skills/sdlc-studio/reference-story.md
- **Verified:** yes (2026-07-16)

### AC2: A registry-only project is never STOPped on personas.md

- **Given** a project with personas/ cards and no personas.md
- **When** prerequisites run
- **Then** personas.md is only a documented legacy fallback, created solely when neither layout exists
- **Verify:** grep "personas/ contains persona cards" .claude/skills/sdlc-studio/reference-story.md
- **Verified:** yes (2026-07-16)

### AC3: Persona selection defaults to the declared Primary

- **Given** the registry's index.md declares a Primary (and possibly Negative personas)
- **When** step 3 selects a story's persona
- **Then** the Primary is the default target and a Negative persona is never a story target
- **Verify:** grep "default to the declared" .claude/skills/sdlc-studio/reference-story.md
- **Verified:** yes (2026-07-16)

### AC4: Help and reference agree on where personas live

- **Given** an operator reading help/story.md
- **When** they check the prerequisites and validation tables
- **Then** the registry-first rule matches reference-story.md
- **Verify:** grep "personas/. registry" .claude/skills/sdlc-studio/help/story.md
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-16 | Claude Fable 5 | ACs written and delivered (CR0283) |
