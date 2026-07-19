# US0266: sprint plan prints the unit lifecycle and the gates each unit will meet, generated from the gate definitions rather than hand-written prose

> **Status:** Done
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
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_briefing_names_unmet_requirements
- **Verified:** yes (2026-07-19)

### AC2: the briefing is generated, not restated

- **Given** the set of checks the gate defines
- **When** a check is added to or removed from that set
- **Then** the briefing changes with it, because it is composed from the definitions - a test
  fails if the briefing carries a hand-maintained list of check names
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_briefing_is_generated_from_definitions
- **Verified:** yes (2026-07-19)

### AC3: the briefing covers every refusal the SKILL's own gates can raise for the batch

- **Given** a batch whose units have unmet terminal-transition requirements
- **When** the briefing is produced
- **Then** every such requirement is named per unit, and the commit-path checks the skill
  defines are carried on the briefing in full
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_briefing_is_generated_from_definitions
- **Verified:** yes (2026-07-19)

> **Amended at build time, and why.** This AC first named the five refusal classes recorded
> against CR0361. Two of them - an internal provenance tag in a consuming-facing file, and a
> multi-id commit subject needing `Refs:` trailers - come from THIS repo's own
> `tools/lint-style.sh` and `.githooks/commit-msg`, not from the skill. The skill is
> project-neutral and cannot know them. Worse, hardcoding the five would be a restatement,
> which AC2 forbids: the two criteria contradicted each other as written. The briefing
> therefore covers what the skill can derive, and says plainly that repo-local guards belong
> to the consuming project's own hook rather than pretending to enumerate them.

### AC4: the briefing does not bloat the plan into noise

- **Given** a batch whose units are all one type
- **When** the plan is printed
- **Then** the briefing reports only the requirements that batch can actually meet, not the
  whole catalogue - the plan already risks being skimmed, and an irrelevant checklist is how a
  relevant one stops being read
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_briefing_is_scoped_to_the_batch
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-19 | sdlc-studio | Groomed: ACs anchored on the five refusal classes recorded against CR0361 |
