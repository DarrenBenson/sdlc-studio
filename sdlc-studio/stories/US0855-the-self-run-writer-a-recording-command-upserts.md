# US0855: the self-run WRITER: a recording command upserts a Self-run field carrying lane, verdict, wall clock and a hash over the unit's gate-surface bytes

> **Status:** Draft
> **Supersedes:** US0817
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .githooks/pre-push, tools/tests/test_pre_push_hook.py, AGENTS.md
> **Epic:** EP0248
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an agent delivering a change to the gate surface
**I want** a shipped command that RECORDS a self-run into the unit, with the bytes it ran against
**So that** the gate that reads it has one writer to trust, rather than a field anybody can type

## Acceptance Criteria

Carried VERBATIM from US0817 (criterion AC2), which was groomed and goal-reviewed before it was split. The words are unchanged so the scope is provably the same as the parent's; what changes is that they are now sized where estimation is reliable.

- [ ] **AC2** Given the recording command run on the repository, when it finishes, then a `Self-run:` field is upserted INTO the unit's artefact (tracked, beside `Verification depth`) carrying the lane or script, the verdict, the wall clock in seconds and a hash over the unit's gate-surface files, with `.local/self-runs.json` as the scratch copy only; a lane not in the boundary registry is refused naming the registry; the reader in transition.py and this writer share one function, round-tripped in the test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::SelfRunRecordTests::test_the_record_carries_unit_lane_verdict_clock_and_hash

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-21 | decomposition | Split from US0817 (8 points, at the ceiling where estimation reliability falls off) in RUN-01M306PY under D0222. Criteria carried verbatim rather than rewritten, so nothing is silently dropped or widened in the split. |
