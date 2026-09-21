# US0856: the self-run GATE: a unit whose Affects names the derived gate surface cannot reach Fixed or Done without a green, current self-run

> **Status:** Draft
> **Supersedes:** US0817
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .githooks/pre-push, tools/tests/test_pre_push_hook.py, AGENTS.md
> **Epic:** EP0248
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** a reviewer of a change to the gate surface
**I want** the transition to refuse a gate-surface unit with no green, current self-run, and stay silent for units outside that surface
**So that** a change to the thing that judges every other change is itself judged, and BG0649's class cannot recur unnoticed

## Acceptance Criteria

Carried VERBATIM from US0817 (criteria AC1, AC3, AC4, AC5), which was groomed and goal-reviewed before it was split. The words are unchanged so the scope is provably the same as the parent's; what changes is that they are now sized where estimation is reliable.

- [ ] **AC1** Given a unit whose Affects names a file of the gate surface - `scripts/gate.py`, and every script `.githooks/pre-push` or `gate.py`'s boundary registry invokes, DERIVED by reading them (today `tools/skill-tests.sh`, `tools/rehearse-release.sh`, `tools/gate_timing.py`, `tools/boundary_roster.py`, `tools/verify-corpus.sh`), pinned by a test that the derived set contains `.githooks/pre-push`, `tools/skill-tests.sh` and `tools/rehearse-release.sh` - and no self-run recorded, when `transition.py set <unit> Fixed` or `Done` runs, then it refuses naming each such file and the recording command for it; with a green self-run recorded by the shipped writer (AC2) against the unit's current gate-surface bytes it passes - the paired control, produced through the writer and never hand-written. The recording command per file: `gate.py` -> `gate.py --boundary push --self-run-for <unit>` (every bound lane); `.githooks/pre-push` -> the hook itself under `SDLC_PRE_PUSH_SELF_RUN=1`, which runs it against HEAD and pushes nothing; any other surface script -> that script. A consuming project with no `.githooks/` derives a surface of `gate.py` alone.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SelfRunGateTests::test_a_gate_surface_change_without_a_self_run_is_refused_and_a_recorded_green_passes

- [ ] **AC3** Given a record whose hash no longer matches the unit's gate-surface bytes, when the transition runs, then the record is stale and the gate refuses naming it stale and the re-run command.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SelfRunGateTests::test_a_stale_self_run_does_not_satisfy_the_gate

- [ ] **AC4** Given a self-run recorded RED on the current bytes, when the transition runs, then it refuses citing the red verdict - a record is not a pass.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SelfRunGateTests::test_a_red_self_run_does_not_satisfy_the_gate

- [ ] **AC5** Given a unit whose Affects names none of the derived gate surface, when the transition runs, then the gate is silent and reads no record.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::SelfRunGateTests::test_a_unit_outside_the_gate_surface_is_untouched

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-21 | decomposition | Split from US0817 (8 points, at the ceiling where estimation reliability falls off) in RUN-01M306PY under D0222. Criteria carried verbatim rather than rewritten, so nothing is silently dropped or widened in the split. |
