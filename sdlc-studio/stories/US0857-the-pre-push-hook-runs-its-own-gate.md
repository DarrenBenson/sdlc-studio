# US0857: the pre-push hook runs its own gate against HEAD under SDLC_PRE_PUSH_SELF_RUN and pushes nothing, so a hook change can record a self-run

> **Status:** Draft
> **Supersedes:** US0817
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .githooks/pre-push, tools/tests/test_pre_push_hook.py, AGENTS.md
> **Epic:** EP0248
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** an agent changing .githooks/pre-push
**I want** the hook to run its own gate against HEAD and push nothing
**So that** a hook change can record the self-run its gate demands, which is otherwise impossible without pushing

## Acceptance Criteria

Carried VERBATIM from US0817 (criterion AC6), which was groomed and goal-reviewed before it was split. The words are unchanged so the scope is provably the same as the parent's; what changes is that they are now sized where estimation is reliable.

- [ ] **AC6** Given `.githooks/pre-push` invoked with `SDLC_PRE_PUSH_SELF_RUN=1` in a fixture repository, when it runs, then it executes its gate against HEAD, records the verdict and pushes nothing - the mode the recording command for a hook change depends on, driven through the hook by subprocess.
  - **Verify:** pytest tools/tests/test_pre_push_hook.py::SelfRunModeTests::test_the_self_run_flag_runs_the_gate_against_head_and_pushes_nothing

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-21 | decomposition | Split from US0817 (8 points, at the ceiling where estimation reliability falls off) in RUN-01M306PY under D0222. Criteria carried verbatim rather than rewritten, so nothing is silently dropped or widened in the split. |
