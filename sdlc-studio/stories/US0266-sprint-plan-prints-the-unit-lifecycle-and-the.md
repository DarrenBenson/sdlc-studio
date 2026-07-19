# US0266: sprint plan prints the unit lifecycle and the gates each unit will meet, generated from the gate definitions rather than hand-written prose

> **Status:** Ready
> **Delivers:** CR0361
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/gate.py
> **Epic:** EP0086
> **Points:** 5

## User Story

**As an** agent starting a sprint
**I want** the plan to tell me the lifecycle each unit will travel and the gates it will meet
**So that** I work to the requirements instead of discovering them one refusal at a time

## Context

`sprint plan` already prints the batch, the wave order, the token forecast, the capacity read
and the lessons digest. It does not print what a unit must satisfy to reach terminal, which is
the one thing needed for every unit, every time.

The knowledge is not missing - it is spread across `AGENTS.md`, `reference-scripts.md`, `help/`,
`reference-test-best-practices.md` and each guard's own remedy text, which is correct for
progressive disclosure and wrong for a per-unit checklist.

The generation rule is the load-bearing part. `gate.DEFAULT_CHECKS` maps check names to their
functions and `transition`'s requirement functions return a reason or `None`. A briefing composed
from THOSE stays correct when a gate changes; a briefing written as prose is a second copy that
drifts, which is what CR0361's third acceptance criterion forbids.

## Acceptance Criteria

### AC1: the plan names the gates each unit type will meet

- **Given** a planned batch containing a story and a bug
- **When** `sprint plan` runs
- **Then** its output names the terminal-transition requirements for each unit type in the batch
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k plan_briefs_the_gates

### AC2: the briefing is generated, not restated

- **Given** the set of checks the gate defines
- **When** a check is added to or removed from that set
- **Then** the briefing changes with it, because it is composed from the definitions - a test
  fails if the briefing carries a hand-maintained list of check names
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k briefing_is_generated_from_definitions

### AC3: the briefing covers the refusals actually hit in practice

- **Given** the five refusal classes recorded against CR0361 - a bug's `Verification depth`
  before Fixed, a CR's T-shirt `Size`, a bug's `Severity`, an internal provenance tag in a
  consuming-facing file, and a multi-id commit subject needing `Refs:` trailers
- **When** the briefing is produced for a batch that can hit them
- **Then** each is named before the work
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k briefing_covers_the_known_refusals

### AC4: the briefing does not bloat the plan into noise

- **Given** a batch whose units are all one type
- **When** the plan is printed
- **Then** the briefing reports only the requirements that batch can actually meet, not the
  whole catalogue - the plan already risks being skimmed, and an irrelevant checklist is how a
  relevant one stops being read
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k briefing_is_scoped_to_the_batch

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-19 | sdlc-studio | Groomed: ACs anchored on the five refusal classes recorded against CR0361 |
