# US0339: The shipped seed's basis text states the condition under which a base term did worse, instead of claiming it flatly

> **Status:** Done
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
- **Verified:** yes (2026-07-23)

### AC2: the qualification survives when the project HAS measured a rate of its own

- **Given** a project whose velocity record yields a usable rate, so the forecast quotes that
  rather than the shipped seed
- **When** the basis travelling with the figure is read
- **Then** it still states the condition rather than the bare no-base-term claim, because the
  two basis strings are the SAME string only while no local rate exists - a criterion checked
  solely in the seed case is satisfied by the same fixture as AC1 and discriminates nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheSeedBasisNamesItsConditionTests::test_the_qualification_survives_when_a_local_rate_replaces_the_seed
- **Verified:** yes (2026-07-23)

### AC3: the reference document and the code do not disagree

- **Given** the estimator section of `reference-sprint.md`
- **When** a reader reaches its account of what a point costs and why the model has no base term
- **Then** the section states the condition under which that held, matching the code's basis,
  so the doc cannot be cited against the fixed term the same release ships
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py::EstimatorBasisAgreesWithTheCodeTests::test_the_reference_no_base_term_account_carries_the_same_condition_as_the_code
- **Verified:** yes (2026-07-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
