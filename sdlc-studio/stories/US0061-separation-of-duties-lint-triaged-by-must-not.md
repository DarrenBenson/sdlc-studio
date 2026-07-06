# US0061: Separation-of-duties lint: triaged_by must not equal raised_by

> **Status:** Draft
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0013
> **Persona:** Skill Maintainer
> **Source:** CR-0170
> **Depends on:** US0060

## User Story

**As a** skill maintainer
**I want** a lint rule that a triager cannot equal the raiser
**So that** the adversarial-review discipline is enforced by a check, not by memory, as teams scale

## Acceptance Criteria

### AC1: Same raiser and triager fails

- **Given** an artefact whose triaged_by deep-equals raised_by
- **When** validate / the consolidated lint / gate runs
- **Then** it fails, naming the rule; transition.py refuses the triage at write time
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k separation_of_duties

### AC2: Solo-human carve-out

- **Given** a solo human operator with no second identity
- **When** they self-triage a `type: human` artefact
- **Then** it warns, not errors (solo-first stays the primary shape)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k sod_solo_warn

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
