# US1205: The hostile kit proves a shallow clone, a non-Claude harness and an over-long token change no result

> **Status:** Draft
> **Risk-class:** elevated
> **Delivers:** CR0675
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_verifier_hostile_env.py
> **Epic:** EP0328
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The hostile kit proves a shallow clone, a non-Claude harness and an over-long token change no result
**So that** CR0675 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The light-tier scope check holds in a shallow clone

- **Given** a fixture repository in which a unit's Affects widened after its light APPROVE was recorded, cloned in full and with `git clone --depth 1`
- **When** `conformance.py check --format json` is run in each clone
- **Then** both report the unit as not conformant at its tier: the shallow clone, which cannot name the commit that recorded the row, fails toward the full review and never reads conformant. Fails on: a shallow clone that reads the grafted boundary commit as the one that added the row and so passes the widened unit (BG1167's round-one finding)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verifier_hostile_env.py::HostileEnvTests::test_the_scope_check_holds_in_a_depth_one_clone

### AC2: Results do not change under a non-Claude harness environment

- **Given** a scratch run with recorded lane sessions, read once with `CLAUDECODE` set and once with `CLAUDECODE` unset and `CURSOR_AGENT=1`
- **When** `sprint.py status --format json` and `verify_ac.py run` are run under each environment
- **Then** the criteria results are identical under both, and the run's token reading under the second either equals the first or is refused by name as unmetered; neither command exits with a traceback. Fails on: a result that depends on the harness the command happened to be run from (US0986's round-one finding)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verifier_hostile_env.py::HostileEnvTests::test_results_do_not_change_under_a_non_claude_harness

### AC3: A 300-character Verify token does not crash the verify lane

- **Given** a story whose Verify line is `grep -q <300 characters> README.md` beside a story with an ordinary passing criterion
- **When** the release verify lane is run over both through `gate.py`
- **Then** the lane completes, the long-token criterion is reported with its own result and the other criterion is read as passing. Fails on: an `OSError` for the over-long name that stops the whole lane, the recorded mutant of US1113 in which each token is tested as a directory unguarded
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verifier_hostile_env.py::HostileEnvTests::test_an_over_long_verify_token_does_not_crash_the_lane

### AC4: The module is selected by a change to the verifier core and stays quick

- **Given** the commit gate's test selection and this module
- **When** the selection is asked for a staged change to `verify_ac.py`, to `gate.py` and to `lib/run_state.py`, and the module is run
- **Then** the module is selected for each of the three, opens no network connection and finishes in under 10 seconds, its share of the kit's 30. Fails on: a kit nothing runs when the verifier core changes, or one too slow to stay in a commit's selection
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verifier_hostile_env.py::HostileEnvTests::test_the_module_is_selected_by_the_verifier_core_and_is_quick

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
