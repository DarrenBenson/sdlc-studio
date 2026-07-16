# US0195: definition-of-ready and definition-of-done templates with tagged machine-checkable criteria resolving through one registry authority; unknown check id is a loud validation error

> **Status:** Ready
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/core/definition-of-ready.md, .claude/skills/sdlc-studio/templates/core/definition-of-done.md, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/reference-decisions.md
> **Epic:** EP0065
> **Points:** 5

## User Story

**As** Maya Okafor (solo founder-engineer, the Primary)
**I want** the project's ready and done bars as two editable documents whose enforceable criteria carry registered check ids
**So that** the quality bar is visible and editable in one place, and human intent cannot drift from the enforced rule

## Acceptance Criteria

### AC1: the two templates ship with a check-id registry in one authority module

- **Given** the shipped skill payload
- **When** the definition-of-ready and definition-of-done templates are inspected against the registry
- **Then** The two templates ship with default criteria per level, each enforceable one tagged with a registered check id; the registry lives in one authority module
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_dor_dod.py -k Registry

### AC2: an unknown check id fails loudly

- **Given** a project document carrying a `[check: ...]` tag not in the registry
- **When** validation runs over the document
- **Then** An unknown check id in either document is a loud validation error, never silently unenforced
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_dor_dod.py -k UnknownCheckId

### AC3: the never-weaken rule is documented

- **Given** the shipped reference documentation
- **When** a reader opens the DoR/DoD guidance
- **Then** Documentation states the non-negotiable rule: under pressure cut scope, never weaken the bar
- **Verify:** grep "never weaken the bar" .claude/skills/sdlc-studio/reference-decisions.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-16 | Claude Fable 5 | Design rung: ACs made executable |
