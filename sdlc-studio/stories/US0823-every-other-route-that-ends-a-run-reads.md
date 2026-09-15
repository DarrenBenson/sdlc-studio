# US0823: every other route that ends a run reads the same unanswered-unit predicate as the close, and stop --force records what it waived

> **Status:** Ready
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py
> **Epic:** EP0206
> **Points:** 3
> **Depends on:** US0626
> **Persona:** Maya Okafor

## User Story

**As a** reviewer of record reading how a run ended
**I want** every route that can end a run to judge unfinished units the way the close does
**So that** a run cannot be ended around the stop-ship question through a side door

## Acceptance Criteria

### AC1: --file-and-close refuses an unanswered unit

- **Given** US0626 AC5's fixture batch - every answered and unanswered shape, including a bug rejected after Fixed, which a route fed `_remaining_units` (it drops Fixed units) would miss
- **When** `sprint.py close --file-and-close` runs
- **Then** it refuses, naming the unit, through the same predicate US0626 ships
- **Mutant:** leave --file-and-close ungated - the same unfinished batch closes through the other door
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EveryRunEndReadsThePredicateTests::test_file_and_close_refuses_an_unanswered_unit

### AC2: stop --force proceeds and records what it waived

- **Given** the same run
- **When** `sprint.py stop --force` runs
- **Then** it stops, and the run record names each unit the SHARED predicate calls unanswered - including any unit whose standing REJECT `critic.coverage_state` does not read as repaired (D0196c), which today's `could_have_proceeded` record cannot see - so an override leaves the stop-ship question on the record rather than only the units that could have proceeded
- **Mutant:** stop without recording the waived units
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EveryRunEndReadsThePredicateTests::test_stop_force_records_the_waived_units

### AC3: the boundary stops and handoff --outcome name unanswered units rather than closing silently

- **Given** a run ended by a boundary stop, and one ended by `handoff.py generate --outcome`, each holding an unanswered unit
- **When** the run closes
- **Then** its outcome record names the unanswered units by id - a breaker must still stop, so these report rather than refuse
- **Mutant:** close the run with the unanswered units unrecorded
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff.py::HandoffOutcomeUnansweredTests::test_every_non_close_end_names_unanswered_units

### AC4: an answered batch ends by every route as today

- **Given** a run whose every unit is answered, one of them a Review unit whose REJECT is completely repaired
- **When** it is ended by each route in turn
- **Then** none refuses and none records a waived unit - the paired control
- **Mutant:** refuse unconditionally - a gate that refuses every end is not a gate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::EveryRunEndReadsThePredicateTests::test_an_answered_batch_ends_by_every_route

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-15 | sprint planning 2026-09-15 | Split from US0626 at the sprint goal review: close_run has six callers, and D0193 requires every route that ends a run to read the one unanswered-unit predicate - --file-and-close refuses, stop --force records what it waived, the boundary stops and handoff --outcome name what they left. |
| 2026-09-15 | sprint planning 2026-09-15 | Goal review round 2 repairs: AC2 now demands new behaviour: stop --force records the shared predicate's unanswered set, which today's could_have_proceeded record cannot see - as first written it was already green at HEAD. |
| 2026-09-15 | sprint planning 2026-09-15 | Goal review round 3: AC2's unanswered set is D0196c's - any unit whose standing REJECT critic.coverage_state does not read as repaired. |
| 2026-09-15 | sprint planning 2026-09-15 | Goal review round 4 notes (all three seats YES): AC1-AC3 reuse US0626 AC5's full fixture batch, so a route fed _remaining_units (which drops Fixed units) fails; AC4's answered batch holds a completely repaired unit. |
