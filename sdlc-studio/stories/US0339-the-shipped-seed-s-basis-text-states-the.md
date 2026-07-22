# US0339: The shipped seed's basis text states the condition under which a base term did worse, instead of claiming it flatly

> **Status:** Draft
> **Delivers:** CR0391
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-sprint.md,.claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0114
> **Points:** 2

## User Story

**As a** reader deciding whether to trust the shipped estimator
**I want** the "no base term" finding to name the data it was measured on
**So that** a result true of runner-era per-unit measurements is not read as a result about a
sprint that carries ceremony, review rounds and a close

## Context

The seed's basis says flatly that fitting a base term does worse than not fitting one. That
was true of what it measured: 19 units of runner-era per-unit actuals with no sprint ceremony
in the numerator. Applied to whole sprints the same claim is false by roughly 300 times, per
CR0391. The estimator is not wrong about what it measured; the sentence is wrong about where
it applies, and it is the sentence a future author would use to reject US0336.

## Acceptance Criteria

### AC1: the seed's basis names the data the finding was measured on

- **Given** the shipped seed basis a plan quotes when a project has measured no rate of its own
- **When** it is read
- **Then** it states that the no-base-term result was measured on per-unit actuals with no
  sprint ceremony, review rounds or close, instead of asserting unconditionally that fitting a
  base term does worse
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheSeedBasisNamesItsConditionTests::test_the_seed_basis_states_the_data_the_no_base_term_finding_was_measured_on

### AC2: the basis travelling with every forecast carries the same qualification

- **Given** the basis string the forecast returns on every plan, which is printed wherever the
  number is
- **When** it is read
- **Then** it no longer claims a base term does worse without saying on what, so the
  qualification cannot be separated from the figure it qualifies
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheSeedBasisNamesItsConditionTests::test_the_forecast_basis_no_longer_makes_the_unconditional_claim

### AC3: the reference document and the code do not disagree

- **Given** the estimator section of `reference-sprint.md`
- **When** a reader reaches its account of what a point costs and why the model has no base term
- **Then** the section states the condition under which that held, matching the code's basis,
  so the doc cannot be cited against the fixed term the same release ships
- **Verify:** manual - read the estimator section of `.claude/skills/sdlc-studio/reference-sprint.md` and confirm the no-base-term finding is stated with the data it was measured on, not as an unconditional claim

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
