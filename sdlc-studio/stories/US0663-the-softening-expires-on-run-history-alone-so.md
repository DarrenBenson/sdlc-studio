# US0663: The softening expires on run history alone, so a second run refuses and an upgrading project is unaffected byte-for-byte

> **Status:** Draft
> **Delivers:** CR0541
> **Created:** 2026-08-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md
> **Epic:** EP0213
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The softening expires on run history alone, so a second run refuses and an upgrading project is unaffected byte-for-byte
**So that** CR0541 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1

**Given** the greenfield fixture from US0662 after ONE run has been closed
**When** the same story shape is transitioned to Done through the shipped CLI
**Then** the plan-review requirement REFUSES, proving the softening expires on run history rather
than persisting.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k second_run_refuses_after_softening
- **Mutant:** make the first-run predicate read a config key instead of the run history - the test must fail, because a key would not expire.

### AC2

**Given** a project that already carries closed-run history - the upgrading case
**When** the transition is attempted
**Then** the output is byte-identical to the behaviour before this epic, asserted against a
recorded baseline rather than against a restatement of the new code.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k upgrading_project_output_unchanged
- **Mutant:** widen the first-run predicate to "no run open" instead of "no run ever closed" - the test must fail, because an upgrading project between runs would then be softened.

### AC3

**Given** the shipped configuration reference and defaults
**When** they are read for the plan-review section
**Then** they state that the first run reports rather than refuses, and no configuration key was
added that could leave a project permanently softened.

- **Verify:** shell python3 -c "import pathlib,sys; t=pathlib.Path('.claude/skills/sdlc-studio/reference-config.md').read_text(); sys.exit(0 if 'first run' in t and 'plan_review' in t else 1)"
- **Mutant:** introduce a `plan_review.first_run: report|block` key - the test must fail, because the concession must expire on its own rather than be held open by a setting.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | make the first-run predicate read a config key instead of the run history - the second-run fixture must stop refusing, because a key would not expire | |
| AC2 | widen the first-run predicate to `no run open` instead of `no run ever closed` - the upgrading-project fixture would then be softened, and the byte-identical assertion must fail | |
| AC3 | introduce a `plan_review.first_run` key taking report or block - the test must fail, because the concession must expire on its own rather than be held open by a setting | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Created via `new` (deterministic) |
