# US0863: `sprint close` derives the goal verdict from the clause results, and `--goal-verdict` becomes an override that must carry its justification

> **Status:** Draft
> **Delivers:** RFC0060
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0258
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** `sprint close` derives the goal verdict from the clause results, and `--goal-verdict` becomes an override that must carry its justification
**So that** RFC0060 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1: the verdict is DERIVED from the clause results.**
  - **Given** a run whose clauses all evaluated green
  - **When** the close runs
  - **Then** the recorded verdict is `achieved`, computed from those results rather than taken from a flag
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DerivedGoalVerdictTests::test_every_clause_green_derives_achieved
- [ ] **AC2: some green derives `partial`, and the failing clauses are named.**
  - **Given** a run with one green clause and one failed
  - **When** the close runs
  - **Then** the verdict is `partial` and the failed clause is named - this is exactly RUN-01M306PY, which recorded `achieved` with its second clause unmet
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DerivedGoalVerdictTests::test_one_failed_clause_derives_partial_and_names_it
- [ ] **AC3: an `unknown` clause degrades the verdict rather than being read as green.**
  - **Given** a run whose only non-green clause could not be run
  - **When** the close runs
  - **Then** the verdict is `partial`, not `achieved`, and the clause is named as unmeasured
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DerivedGoalVerdictTests::test_an_unknown_clause_degrades_the_verdict
- [ ] **AC4: no clause green derives `missed`.**
  - **Given** a run whose clauses all failed
  - **When** the close runs
  - **Then** the verdict is `missed` - the discriminating floor, because a derivation that never reaches its worst value is not deriving
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DerivedGoalVerdictTests::test_no_clause_green_derives_missed
- [ ] **AC5: `--goal-verdict` becomes an override that must carry its justification.**
  - **Given** a close passing `--goal-verdict achieved` over a derivation of `partial`, with no reason
  - **When** the close runs
  - **Then** it refuses; with a reason, it records the override AND the derived verdict beside it - D0238, so an override is a reasoned exception rather than the normal path
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DerivedGoalVerdictTests::test_an_override_needs_a_reason_and_records_the_derived_verdict_beside_it

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint.py`, keep taking the verdict from the `--goal-verdict` flag and ignore the clause results - the shipped behaviour | all green derives achieved |
| AC2 | in `sprint.py`, derive `achieved` whenever ANY clause is green rather than requiring every one | one failure derives partial |
| AC3 | in `sprint.py`, count an `unknown` clause as green when deriving the verdict | unknown degrades the verdict |
| AC4 | in `sprint.py`, floor the derivation at `partial` so `missed` is unreachable | no clause green derives missed |
| AC5 | in `sprint.py`, accept `--goal-verdict` with no reason and record it as the verdict, dropping the derived one | an override is reasoned and disclosed |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Created via `new` (deterministic) |
