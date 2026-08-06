# US0633: a criterion whose mutant cannot be named is refused at grooming

> **Status:** Done
> **Delivers:** CR0525
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0207
> **Depends on:** US0629
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** maintainer grooming a batch
**I want** a criterion whose falsifying change nobody can name to be refused before the batch is planned
**So that** the unanswerable question is asked while the criterion can still be rewritten, rather than at delivery when the only remaining move is to waive it

## Acceptance Criteria

### AC1: a batch carrying an unnameable mutant is not plannable

- **Given** a batch in which one unit's test plan carries a row marked `unnameable`
- **When** `sprint.py breakdown` reports and `sprint.py plan --write` runs over that batch
- **Then** `breakdown` names the unit and the criterion read-only, and `plan --write` refuses, on the same terms it already refuses a unit lacking `Affects` or `Points`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UnnameableMutantTests::test_an_unnameable_mutant_refuses_the_plan
- **Caller:** `sprint.py plan --write` (the command that opens a run)
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - reducing the refusal to a warning must turn this test red
- **Verified:** yes (2026-08-06)

### AC2: `unnameable` must carry its reason, so the state cannot be used as a silent exit

- **Given** a row marked `unnameable` with no reason recorded
- **When** the batch is read
- **Then** it is refused as malformed rather than accepted as a declared exemption, because a state that costs nothing to enter is the state every awkward criterion ends up in
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::UnnameableMutantTests::test_unnameable_without_a_reason_is_malformed
- **Caller:** `sprint.py breakdown` and `sprint.py plan --write`
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - accepting a reasonless `unnameable` must turn this test red
- **Verified:** yes (2026-08-06)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | sdlc-studio | Groomed: criteria authored against the `sprint.py` grooming refusal slice |
| 2026-08-06 | sdlc-studio | Declared `Depends on:` at plan time - the planner reported all six units parallel because no dependency was stated, which is false: the plan is derived (US0629) before it can be reviewed, gated, executed or measured |
