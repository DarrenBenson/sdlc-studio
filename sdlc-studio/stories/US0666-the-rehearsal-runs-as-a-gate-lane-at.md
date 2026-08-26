# US0666: The rehearsal runs as a gate lane at the push and release boundaries, with its cost recorded and its fixtures proven to write outside the working tree

> **Status:** Done
> **Delivers:** CR0542
> **Created:** 2026-08-10
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, AGENTS.md, tools/tests/test_check_spec_claims.py
> **Epic:** EP0214
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The rehearsal runs as a gate lane at the push and release boundaries, with its cost recorded and its fixtures proven to write outside the working tree
**So that** CR0542 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1

- **Given** the gate's lane roster
- **When** `gate.py --boundary push` and `gate.py --boundary release` are run
- **Then** the `release-rehearsal` lane runs at both, and does NOT run on a plain per-commit gate -
  the gate is already over its budget on most commits, and a guard whose cost is paid on every
  commit gets switched off.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py -k the_rehearsal_lane_runs_at_the_push_and_release_boundaries
- **Verified:** yes (2026-08-26)

### AC2

- **Given** a tree in which the greenfield or upgrade rehearsal fails
- **When** the boundary gate runs
- **Then** the lane reports the failure with the failing rehearsal named, and the lane's measured
  duration is recorded alongside the other lanes rather than being untimed.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py -k the_rehearsal_lane_names_its_failing_half_and_records_its_cost
- **Verified:** yes (2026-08-26)

### AC3

- **Given** `AGENTS.md`'s roster of pre-commit lanes, which a review once found to be an
  incomplete account of this repository's own gates
- **When** the roster is read
- **Then** it names the rehearsal lane and states that it runs at the push and release boundaries
  rather than per commit, and a guard checks the roster names it.

- **Verify:** pytest tools/tests/test_check_spec_claims.py -k the_lane_roster_names_the_release_rehearsal
- **Verified:** yes (2026-08-10)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `gate.py`, change the rehearsal lane's boundary set to include the per-commit gate | |
| AC2 | in `gate.py`, change the rehearsal lane to report a bare pass or fail without naming which half failed | |
| AC3 | in `AGENTS.md`, delete the rehearsal lane from the pre-commit roster | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-10 | sdlc-studio | Created via `new` (deterministic) |
