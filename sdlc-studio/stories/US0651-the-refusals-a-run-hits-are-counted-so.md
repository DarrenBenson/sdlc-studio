# US0651: The refusals a run hits are counted, so the round-trip saving is a figure in the retro

> **Status:** Ready
> **Delivers:** CR0535
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0210
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The refusals a run hits are counted, so the round-trip saving is a figure in the retro
**So that** CR0535 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: refusals are counted per run

- **Given** a run in which verbs refuse
- **When** the run state is read at the close
- **Then** the refusals are counted - the reporter exists to reduce them, and a saving nobody counts is an assertion
- **Mutant:** count invocations instead of refusals - the number moves with activity rather than with friction
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::RefusalsAreCountedTests::test_refusals_are_counted_per_run

### AC2: the retro carries the figure

- **Given** a closed run
- **When** its retro is rendered
- **Then** the refusal count appears in it, beside the cost figures, so the saving is readable run to run
- **Mutant:** compute it and not render it - the figure exists and no reader meets it, which is the inert-mechanism class
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::RefusalsAreCountedTests::test_the_retro_renders_the_count

### AC3: a run with no refusals says zero rather than nothing

- **Given** a run that hit none
- **When** the retro is rendered
- **Then** it states zero - an absent figure and a measured zero are different facts, and blank reads as unmeasured
- **Mutant:** omit the line when the count is zero - the best case is indistinguishable from the unmeasured one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::RefusalsAreCountedTests::test_zero_is_stated_rather_than_omitted

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Created via `new` (deterministic) |
