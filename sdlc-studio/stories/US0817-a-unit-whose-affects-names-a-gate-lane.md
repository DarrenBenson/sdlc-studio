# US0817: A unit whose Affects names a gate lane, a hook or the suite runner cannot reach Fixed or Done without a recorded green self-run of the affected lane on this repository

> **Status:** Ready
> **Delivers:** CR0565
> **Created:** 2026-09-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .githooks/pre-push, tools/tests/test_pre_push_hook.py, AGENTS.md
> **Epic:** EP0248
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A unit whose Affects names a gate lane, a hook or the suite runner cannot reach Fixed or Done without a recorded green self-run of the affected lane on this repository
**So that** a push does not refuse itself - Maya Okafor's gate-lane change is proved where the hook runs it before the first pusher meets it

## Acceptance Criteria

- [ ] **AC1** Given a unit whose Affects names a file of the gate surface - `scripts/gate.py`, and every script `.githooks/pre-push` or `gate.py`'s boundary registry invokes, DERIVED by reading them (today `tools/skill-tests.sh`, `tools/rehearse-release.sh`, `tools/gate_timing.py`, `tools/boundary_roster.py`, `tools/verify-corpus.sh`), pinned by a test that the derived set contains `.githooks/pre-push`, `tools/skill-tests.sh` and `tools/rehearse-release.sh` - and no self-run recorded, when `transition.py set <unit> Fixed` or `Done` runs, then it refuses naming each such file and the recording command for it; with a green self-run recorded by the shipped writer (AC2) against the unit's current gate-surface bytes it passes - the paired control, produced through the writer and never hand-written. The recording command per file: `gate.py` -> `gate.py --boundary push --self-run-for <unit>` (every bound lane); `.githooks/pre-push` -> the hook itself under `SDLC_PRE_PUSH_SELF_RUN=1`, which runs it against HEAD and pushes nothing; any other surface script -> that script. A consuming project with no `.githooks/` derives a surface of `gate.py` alone.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SelfRunGateTests::test_a_gate_surface_change_without_a_self_run_is_refused_and_a_recorded_green_passes
- [ ] **AC2** Given the recording command run on the repository, when it finishes, then a `Self-run:` field is upserted INTO the unit's artefact (tracked, beside `Verification depth`) carrying the lane or script, the verdict, the wall clock in seconds and a hash over the unit's gate-surface files, with `.local/self-runs.json` as the scratch copy only; a lane not in the boundary registry is refused naming the registry; the reader in transition.py and this writer share one function, round-tripped in the test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::SelfRunRecordTests::test_the_record_carries_unit_lane_verdict_clock_and_hash
- [ ] **AC3** Given a record whose hash no longer matches the unit's gate-surface bytes, when the transition runs, then the record is stale and the gate refuses naming it stale and the re-run command.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SelfRunGateTests::test_a_stale_self_run_does_not_satisfy_the_gate
- [ ] **AC4** Given a self-run recorded RED on the current bytes, when the transition runs, then it refuses citing the red verdict - a record is not a pass.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SelfRunGateTests::test_a_red_self_run_does_not_satisfy_the_gate
- [ ] **AC5** Given a unit whose Affects names none of the derived gate surface, when the transition runs, then the gate is silent and reads no record.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SelfRunGateTests::test_a_unit_outside_the_gate_surface_is_untouched
- [ ] **AC6** Given `.githooks/pre-push` invoked with `SDLC_PRE_PUSH_SELF_RUN=1` in a fixture repository, when it runs, then it executes its gate against HEAD, records the verdict and pushes nothing - the mode the recording command for a hook change depends on, driven through the hook by subprocess.
  - **Verify:** pytest tools/tests/test_pre_push_hook.py::SelfRunModeTests::test_the_self_run_flag_runs_the_gate_against_head_and_pushes_nothing

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/transition.py, remove the refusal so Affects is read and never refused | Given a unit whose Affects names a file of the gate surface - `scripts/gate.py`, and every script `.githooks/pre-push` or `gate.py`'s boundary registry invokes, DERIVED by reading them (today `tools/skill-tests.sh`, `tools/rehearse-release.sh`, `tools/gate_timing.py`, `tools/boundary_roster.py`, `tools/verify-corpus.sh`), pinned by a test that the derived set contains `.githooks/pre-push`, `tools/skill-tests.sh` and `tools/rehearse-release.sh` - and no self-run recorded, when `transition.py set <unit> Fixed` or `Done` runs, then it refuses naming each such file and the recording command for it; with a green self-run recorded by the shipped writer (AC2) against the unit's current gate-surface bytes it passes - the paired control, produced through the writer and never hand-written. The recording command per file: `gate.py` -> `gate.py --boundary push --self-run-for <unit>` (every bound lane); `.githooks/pre-push` -> the hook itself under `SDLC_PRE_PUSH_SELF_RUN=1`, which runs it against HEAD and pushes nothing; any other surface script -> that script. A consuming project with no `.githooks/` derives a surface of `gate.py` alone. |
| AC2 | in .claude/skills/sdlc-studio/scripts/gate.py, delete the `hash` key from the dict `record_self_run` writes | Given the recording command run on the repository, when it finishes, then a `Self-run:` field is upserted INTO the unit's artefact (tracked, beside `Verification depth`) carrying the lane or script, the verdict, the wall clock in seconds and a hash over the unit's gate-surface files, with `.local/self-runs.json` as the scratch copy only; a lane not in the boundary registry is refused naming the registry; the reader in transition.py and this writer share one function, round-tripped in the test. |
| AC3 | in .claude/skills/sdlc-studio/scripts/transition.py, drop the hash comparison so a record matches on the unit alone | Given a record whose hash no longer matches the unit's gate-surface bytes, when the transition runs, then the record is stale and the gate refuses naming it stale and the re-run command. |
| AC4 | in .claude/skills/sdlc-studio/scripts/transition.py, remove the verdict check so any record on the current bytes satisfies the gate | Given a self-run recorded RED on the current bytes, when the transition runs, then it refuses citing the red verdict - a record is not a pass. |
| AC5 | in .claude/skills/sdlc-studio/scripts/transition.py, widen the gate to every unit | Given a unit whose Affects names none of the derived gate surface, when the transition runs, then the gate is silent and reads no record. |
| AC6 | in .githooks/pre-push, remove the SDLC_PRE_PUSH_SELF_RUN branch so the hook still requires a ref on stdin | Given `.githooks/pre-push` invoked with `SDLC_PRE_PUSH_SELF_RUN=1` in a fixture repository, when it runs, then it executes its gate against HEAD, records the verdict and pushes nothing - the mode the recording command for a hook change depends on, driven through the hook by subprocess. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-07 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-07 | sdlc-studio | Draft -> Ready |
| 2026-09-07 | Claude Fable 5.1 | Groomed: criteria authored with a named mutant each, one selector per criterion; the self-run on this repository is a delivery obligation recorded in this table, not a criterion, because the plan gate refuses an unnameable row |
| 2026-09-07 | Claude Fable 5.1 | Goal review round 1 (engineering, product, qa all partial): the surface is DERIVED from the hook and the registry with a pin, the recording command is per file, the record is a tracked field written and read by one function, the hook gains a self-run mode (AC6); 3 -> 8 points. DEFERRED from this run's batch to the next: the seats found four open design questions and this run cannot carry an eight-point redesign beside the two coverage stories |
| 2026-09-07 | Claude Fable 5.1 | Goal review round 3 (all seats yes): Test Plan rows name the file, titles re-synced |
| 2026-09-07 | Claude Fable 5.1 | Test Plan rows rewritten as edits led by a verb and the Mutant sentences moved out of the criteria, so `testplan derive` reads the plan as its own shape |
