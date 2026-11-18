# US1203: The hostile kit proves the verifier dies with its caller, exits on an interrupt and leaves no orphan

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0675
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verifier_hostile_signals.py
> **Epic:** EP0328
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The hostile kit proves the verifier dies with its caller, exits on an interrupt and leaves no orphan
**So that** CR0675 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The verifier dies with its caller's process group

- **Given** a scratch consumer tree whose unit has a verifier that spawns a child and sleeps, and `verify_ac.py run` started on it in a process group of its own
- **When** SIGTERM is sent to that group
- **Then** within 5 seconds no process of the run is left alive: not `verify_ac.py`, the verifier or the verifier's child. Fails on: a verifier that outlives its caller, as under the recorded mutant of BG1190 in which the verifier's new session is never relayed the group's signal
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verifier_hostile_signals.py::HostileSignalTests::test_a_group_sigterm_leaves_no_verifier_alive

### AC2: An interrupt exits 130 within seconds

- **Given** the same run, mid-verifier, with a verifier ceiling of 300 seconds
- **When** SIGINT is sent to `verify_ac.py run`
- **Then** it exits 130 within 5 seconds and the verifier and its child are gone. Fails on: an interrupt that waits for the verifier's ceiling, as when the wait runs in a worker thread that never sees it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verifier_hostile_signals.py::HostileSignalTests::test_an_interrupt_exits_130_within_seconds

### AC3: Nested callers leave no orphan

- **Given** a verifier that itself runs `verify_ac.py run` on a second unit whose verifier spawns a grandchild, under a ceiling shorter than the grandchild's sleep
- **When** the outer `verify_ac.py run` times the verifier out
- **Then** the criterion is reported as timed out and, within 5 seconds of the run's exit, neither the inner runner nor the grandchild is alive. Fails on: a kill of the outer group that leaves the inner caller's own group running, BG1190's round-two finding
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verifier_hostile_signals.py::HostileSignalTests::test_nested_callers_leave_no_orphan

### AC4: The module is selected by a change to the verifier core and stays quick

- **Given** the commit gate's test selection and this module
- **When** the selection is asked for a staged change to `verify_ac.py`, to `gate.py` and to `lib/run_state.py`, and the module is run
- **Then** the module is selected for each of the three, opens no network connection and finishes in under 10 seconds, its share of the kit's 30. Fails on: a kit nothing runs when the verifier core changes, or one too slow to stay in a commit's selection
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verifier_hostile_signals.py::HostileSignalTests::test_the_module_is_selected_by_the_verifier_core_and_is_quick

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
