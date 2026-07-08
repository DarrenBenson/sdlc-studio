# US0083: route.py: deterministic difficulty estimator, tier pick and escalation stepper

> **Status:** Done
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Epic:** EP0008
> **Persona:** Dani Okafor (Engineering)
> **CR:** CR-0189 (RFC-0026 WS1)

## User Story

**As an** orchestrator running the sprint loop
**I want** a deterministic difficulty score and tier recommendation per work unit
**So that** each unit can be delivered by an appropriately-sized model instead of everything defaulting to the session's model

## Acceptance Criteria

### AC1: Estimate emits the full signal set with missing-signal defaults

- **Given** a story with an Affects list, ACs and story points
- **When** `route.py estimate --unit <path>` runs
- **Then** it emits {difficulty_score 0-100, difficulty_band, confidence, missing[], signals, subscores}; any subscore whose inputs did not resolve defaults to 0.5 (never 0) and is listed in `missing`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py -k estimate
- **Verified:** yes (2026-07-08)

### AC2: Pick applies bands, floors and the critic rule

- **Given** a unit whose band maps below a configured kind floor, and a critic pick for a code unit
- **When** `route.py pick --unit <path> --role author|critic` runs
- **Then** the kind floor lifts the tier; low confidence bumps one tier up; the critic tier matches the author's, floored at medium for code/security/data-loss
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py -k pick
- **Verified:** yes (2026-07-08)

### AC3: Sparse model maps degrade upward only

- **Given** `routing.models` declaring only {small, large}
- **When** tiers resolve
- **Then** tiny->small, medium->large, xlarge->large; an empty map yields tier names with model: null
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py -k degrad
- **Verified:** yes (2026-07-08)

### AC4: Escalate steps to the next declared tier

- **Given** a declared map and a current tier
- **When** `route.py escalate --tier <t>` runs
- **Then** it returns the next declared tier up, or reports already-at-max
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py -k escalate
- **Verified:** yes (2026-07-08)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | sprint: CR0189 | Created via `new` (deterministic) |
