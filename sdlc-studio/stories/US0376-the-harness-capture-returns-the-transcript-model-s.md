# US0376: the harness capture returns the transcript model(s), mixed as mixed, and the close writes it to the Model cell

> **Status:** Draft
> **Delivers:** CR0373
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0134
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py

## User Story

**As a** operator running interactive sprints on more than one model
**I want** the harness token capture to record which model spent the tokens and the close to write it to the velocity row
**So that** the per-model rate machinery books each interactive sprint in the right (project, model) cell instead of an unrecorded-model bucket

## Acceptance Criteria

### AC1: the capture returns a single transcript model

- **Given** a session transcript whose usage records all name one model
- **When** `harness_tokens` reads it
- **Then** the result carries that model id alongside the token total
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::HarnessCaptureReportsModel::test_single_model_returned

### AC2: two models are reported as mixed

- **Given** a session transcript whose usage records name two different models
- **When** `harness_tokens` reads it
- **Then** the result reports the model as `mixed` rather than picking one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::HarnessCaptureReportsModel::test_two_models_report_mixed

### AC3: the interactive close writes the model to the Model cell

- **Given** an interactive close capturing tokens from a transcript on model M
- **When** `accuracy --write` records the velocity row
- **Then** the row's Model cell is M, so `measured_rate` books it in the (project, M) cell rather than the unrecorded-model cell
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::HarnessCaptureReportsModel::test_close_writes_model_to_velocity_row

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
