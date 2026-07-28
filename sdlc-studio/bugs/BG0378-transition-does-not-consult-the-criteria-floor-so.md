# BG0378: transition does not consult the criteria floor, so the terminal status is set and only the commit that records it is refused

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; each load-bearing predicate mutation-killed)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (closing BG0370, RUN-01KYKVZM); agent; skill v5.0.0

## Summary

BG0370 closed the criteria floor at the validate layer, which the pre-commit gate enforces, so a bug can no longer LAND at a terminal status with no acceptance criteria. The transition verb itself still performs the change: it checks verification depth and triage separation and never asks whether the unit has a criterion. The artefact is therefore mutated on disk and the refusal arrives later, from a different tool, phrased as a validation error rather than as a blocked transition. Defence at the gate rather than at the verb, which is weaker than the rule reads and leaves the working tree in the state the rule forbids.

## Steps to Reproduce

Observed while closing BG0370 on a fresh project. transition set <bug> Fixed on a bug carrying only the auto-written stated absence succeeds and writes the status; validate check then reports no-ac as an error against the same file.

## Proposed Fix

Add the criteria floor to the transition requirements for a terminal target, reading the same predicate validate uses rather than a second copy, so the refusal happens where the change is attempted and names the missing criteria alongside the other blocked requirements.

## Acceptance Criteria

### AC1: The transition verb refuses a delivered-terminal target on a unit with no criteria, and the artefact is not mutated

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::CriteriaFloorAtTheVerbTests::test_a_terminal_transition_with_no_criteria_is_refused_at_the_verb
- **Verified:** yes (2026-07-28)

### AC2: A unit that carries criteria still transitions, so the floor is a gate and not a wall

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::CriteriaFloorAtTheVerbTests::test_a_unit_with_criteria_still_transitions
- **Verified:** yes (2026-07-28)

### AC3: A decision-terminal status needs no criteria: a unit ruled rather than built owes no contract

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::CriteriaFloorAtTheVerbTests::test_a_decision_terminal_status_needs_no_criteria
- **Verified:** yes (2026-07-28)

### AC4: The verb and the validator answer with ONE predicate, asserted as agreement rather than two expected answers

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::CriteriaFloorAtTheVerbTests::test_the_verb_and_the_validator_use_one_predicate
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (closing BG0370, RUN-01KYKVZM) | Filed |
| 2026-07-28 | Claude Opus 5 | Criteria authored at delivery, replacing the auto-written stated absence the filer produced. Executable, because BG0356/BG0360 made a bug's Verify lines run. |
