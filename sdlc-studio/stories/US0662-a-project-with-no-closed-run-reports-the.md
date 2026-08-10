# US0662: A project with no closed run reports the plan-review requirement at the terminal transition instead of refusing, and names the condition that arms it

> **Status:** Draft
> **Delivers:** CR0541
> **Created:** 2026-08-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/plan_review.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0213
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A project with no closed run reports the plan-review requirement at the terminal transition instead of refusing, and names the condition that arms it
**So that** CR0541 is delivered by work that can be planned and checked

## Acceptance Criteria

> **Plan repaired after a REJECT at plan review (2026-08-09, qa seat, brief `392666879ac1`), and
> its premise replaced under D0134.** The seat found the arming fact lived in
> `sdlc-studio/.local/run-archive`, which `.gitignore` documents as state you can delete and lose
> nothing - so a fresh clone, a CI checkout or a cleaned `.local` re-granted the concession
> indefinitely, and a project that never runs a sprint was softened permanently. D0134 moves the
> answer to the COMMITTED retros under `sdlc-studio/retros/`: one per closed run, travelling with
> the repository, so a clone gives the same verdict as the machine that did the work.
>
> Two further findings changed the criteria rather than their wording. `transition.py requirements`
> returns 0 on every path, so it cannot carry a refusal - the When moves to `transition.py set`.
> And every row of the first plan passed on an implementation that deleted the gate outright, so
> the armed case is pinned HERE rather than only in the sibling unit.

### AC1

- **Given** a project holding no retro at all, and one story whose routed band trips the
  plan-review trigger
- **When** `transition.py set --id <story> --status Done` is run through the shipped CLI
- **Then** it is not refused on plan-review grounds, and the requirement is REPORTED with the
  condition that will arm it named.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k a_project_with_no_retro_reports_the_plan_review_requirement
- **Verified:** yes (2026-08-10)
- **Mutant:** in `plan_review.py`, make the first-run branch return the refusal rather than the report.

### AC2

- **Given** the SAME fixture with one retro added under `sdlc-studio/retros/`
- **When** the identical transition is attempted
- **Then** it is REFUSED - so this unit proves the gate still exists, rather than leaving that to
  its sibling and shipping a commit in which the flagship gate is off with nothing able to notice.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k an_armed_project_still_refuses
- **Verified:** yes (2026-08-10)
- **Mutant:** in `plan_review.py`, make the softening unconditional rather than reading the retro count.

### AC3

- **Given** a project whose plan-review gate is dormant for an unrelated reason - schema v2, or
  `plan_review.enabled: false`
- **When** the same transition is attempted, with stdout, stderr and the exit status all captured
- **Then** all three are identical to a baseline captured from the SAME fixture with this unit's
  softening branch disabled, so the comparison is against the old behaviour rather than against a
  restatement of the new code.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py -k a_dormant_gate_is_unchanged_by_the_softening
- **Verified:** yes (2026-08-10)
- **Mutant:** in `plan_review.py`, change the dormancy check to `not active(root) and has_run_history(root)`, so a dormant project without history reaches the softening. Reordering the branch alone is EQUIVALENT - the dormant return carries no plan-review wording and sets `fired` False, so nothing observable moves; that was found by applying it.

### AC4

- **Given** the retro directory absent, unreadable, or holding files that are not retros
- **When** the arming predicate is evaluated
- **Then** it answers ARMED in every one of those cases: the direction this must not fail in is a
  long-lived project being silently softened, so anything it cannot read counts as history rather
  than as its absence.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py -k an_unreadable_history_counts_as_armed
- **Verified:** yes (2026-08-10)
- **Mutant:** in `plan_review.py`, return the softened verdict from the predicate's exception path.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `plan_review.py`, change the first-run branch to return the refusal rather than the report | |
| AC2 | in `plan_review.py`, change the softening to apply unconditionally instead of reading the retro count | |
| AC3 | in `plan_review.py`, change the dormancy check so a dormant project without history reaches the softening branch | |
| AC4 | in `plan_review.py`, change the arming predicate's exception path to return the softened verdict | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Created via `new` (deterministic) |
