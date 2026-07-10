# US0116: Unit-lifecycle ergonomics: annotate verb, batched gate refusals, close orchestrator

> **Status:** Done
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio new
> **Epic:** EP0026
> **Persona:** delivery agent (dogfooding)
> **CR:** CR0209

## User Story

**As a** delivery agent closing a unit
**I want** one verb per intent (stamp a field, see every unmet gate at once, close in one call)
**So that** the close ceremony stops costing hand-edits and one refusal round-trip per gate

## Context

Dogfooded in the RV0007 fix pack: recording `Verification depth` meant hand-editing nine
artefact bodies; a v3 close took three attempts (depth gate, then triage gate, then done);
each unit close was four coupled invocations. Filed as CR0209 from that experience.

## Acceptance Criteria

### AC1: a deterministic metadata-stamp verb

- **Given** any artefact
- **When** `transition.py annotate --id BG0001 --field "Verification depth" --value "functional (...)"` runs
- **Then** the field is inserted (or updated in place) in the metadata block, atomically, without touching the index
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k annotate
- **Verified:** yes (2026-07-10)

### AC2: a blocked transition reports every unmet gate in one refusal

- **Given** a v3 finding missing BOTH a verification depth and a triage record
- **When** it is transitioned to Fixed
- **Then** the single refusal names both requirements (not the first only)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k AllGates
- **Verified:** yes (2026-07-10)

### AC3: one close call performs stamp + verdict + close

- **Given** a unit with its depth text, verdict, reviewer and author known
- **When** `artifact.py close --id X --depth "..." --verdict APPROVE --reviewer R --author A` runs
- **Then** the depth is stamped, the critic verdict recorded (reviewer != author enforced by critic), and the terminal transition performed - one command, re-runnable if a later gate refuses
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py -k orchestrated_close
- **Verified:** yes (2026-07-10)

### AC4: the new verbs are catalogued

- **Given** the docs
- **When** an agent reads help/arguments.md or reference-scripts-verify.md
- **Then** annotate and the close orchestration flags are documented
- **Verify:** grep -q "annotate" .claude/skills/sdlc-studio/help/arguments.md
- **Verified:** yes (2026-07-10)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | sdlc | Created via `new` (deterministic) |
| 2026-07-10 | sprint (CR0209 decomposition) | ACs authored from the dogfood friction list |
