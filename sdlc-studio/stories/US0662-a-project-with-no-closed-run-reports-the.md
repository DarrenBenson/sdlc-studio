# US0662: A project with no closed run reports the plan-review requirement at the terminal transition instead of refusing, and names the condition that arms it

> **Status:** Draft
> **Delivers:** CR0541
> **Created:** 2026-08-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py
> **Epic:** EP0213
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A project with no closed run reports the plan-review requirement at the terminal transition instead of refusing, and names the condition that arms it
**So that** CR0541 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1

**Given** a project created by `init run` that has never closed a run, holding one ordinary
sized story whose routed band trips the plan-review trigger
**When** `transition.py requirements --id <story> --status Done` is invoked through the shipped
CLI
**Then** the plan-review requirement is REPORTED and the transition is not refused on that
ground, and the reported line names the condition that will arm it.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k first_run_reports_plan_review
- **Mutant:** in `transition.py`, make the first-run branch return the refusal string instead of the report - the test must fail on the exit status, not only on the wording.

### AC2

**Given** the same fixture
**When** the reported condition is read back and compared with the predicate the gate itself
evaluates
**Then** they are the same expression, so the report cannot describe a condition the gate does
not use.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py -k arming_condition_is_the_gate_predicate
- **Mutant:** restate the condition in the message as a literal string rather than deriving it from the predicate - the test must fail (LL0042: derive a message from the guard, never restate it beside it).

### AC3

**Given** a project whose plan-review gate is DORMANT for a reason unrelated to run history
(schema v2, or `plan_review.enabled: false`)
**When** the same transition is attempted
**Then** the output is byte-identical to the current behaviour, so the softening did not become
a second way of switching the gate off.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k dormant_gate_unchanged_by_first_run_softening
- **Mutant:** make the first-run branch run before the dormancy check - the test must fail.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `transition.py`, make the first-run branch return the refusal string instead of the report - the test must fail on the exit status, not only on the wording | |
| AC2 | restate the arming condition in the message as a literal string rather than deriving it from the predicate - the test must fail (LL0042) | |
| AC3 | run the first-run branch before the dormancy check - the dormant-gate fixture's output must change, and the test must fail | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Created via `new` (deterministic) |
