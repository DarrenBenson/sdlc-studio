# US1142: The sprint reference defines a wave boundary and runs the close in its own fresh session

> **Status:** Ready
> **Delivers:** CR0670
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/tests/test_wave_boundary_docs.py
> **Epic:** EP0302
> **Points:** 2
> **Depends on:** US1141
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The sprint reference defines a wave boundary and runs the close in its own fresh session
**So that** CR0670 is delivered by work that can be planned and checked

## Acceptance Criteria

- **AC1:** Given the shipped reference-sprint.md, then a section anchored `{#wave-boundary}` defines a wave boundary as every lane of the wave accepted and none in flight, states that a hand-back reaches only the session that spawned its agent so no boundary falls with a lane in flight, and names `sprint.py handoff` at the boundary and `sprint.py resume` in the fresh session, each a verb the sprint parser owns. Fails on: the section absent, the definition missing either condition, or a named verb the parser does not own.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_wave_boundary_docs.py::WaveBoundaryDocTests::test_the_reference_defines_the_boundary_and_names_parser_verbs
- **AC2:** Given the same reference, then it routes the close (retro, report, close and sign) through its own fresh session started from the resume brief, and the loop under `#the-loop` stays six steps. Fails on: the close left in the last wave's session, or a seventh loop step.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_wave_boundary_docs.py::WaveBoundaryDocTests::test_the_close_runs_in_its_own_fresh_session_and_the_loop_stays_six_steps
- **AC3:** Given the reference's "The handoff and the run object" section and reference-sprint-toolchain.md, then the section tells the resume brief (run-local under `sdlc-studio/.local/`, read by `sprint.py resume`) apart from the retired handoff record the signed report replaced, and the runbook carries one row for `sprint.py handoff` and one for `sprint.py resume`. Fails on: the section still saying no command writes a handoff with no word on the resume brief, or either runbook row missing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_wave_boundary_docs.py::WaveBoundaryDocTests::test_the_resume_brief_is_told_apart_from_the_retired_handoff_and_the_runbook_names_both

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-09 | Claude Opus 5.5 (run nine grooming) | Acceptance criteria and Verify lines authored at grooming |
