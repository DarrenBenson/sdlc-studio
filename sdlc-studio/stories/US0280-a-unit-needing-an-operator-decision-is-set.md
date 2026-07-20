# US0280: A unit needing an operator decision is set aside and the batch continues; accumulated decisions are asked together at the stop

> **Status:** Review
> **Delivers:** CR0369
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Epic:** EP0092
> **Depends on:** US0281
> **Points:** 5

## User Story

**As a** sprint operator
**I want** a run to set aside a unit that needs my decision and carry on
**So that** one undecidable unit never stalls units that were never blocked

## Acceptance Criteria

### AC1: the blocked unit is set aside and the batch continues

- **Given** a batch where one unit needs an operator decision and others do not
- **When** the run reaches that unit
- **Then** it is set aside and the remaining units continue, so the run stops only when it can
  make no further progress
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_undecidable_unit_is_set_aside_and_batch_continues
- **Verified:** yes (2026-07-20)

### AC2: accumulated decisions are asked together at the stop

- **Given** several decisions accumulated while the run continued
- **When** the run finally stops
- **Then** they are presented together rather than one stop per decision
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_accumulated_decisions_are_asked_together
- **Verified:** yes (2026-07-20)

### AC3: a non-interactive run never silently defaults a decision

- **Given** a non-interactive (autonomous) run
- **When** a unit needs an operator decision
- **Then** the question is recorded and the unit is marked Blocked, exactly as today - never
  answered by default
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_autonomous_run_records_and_blocks_never_defaults
- **Verified:** yes (2026-07-20)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Created via `new` (deterministic) |
