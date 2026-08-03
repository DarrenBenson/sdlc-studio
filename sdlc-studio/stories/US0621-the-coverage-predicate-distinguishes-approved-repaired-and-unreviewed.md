# US0621: the coverage predicate distinguishes approved, repaired and unreviewed rather than two states

> **Status:** Ready
> **Delivers:** CR0506
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0205
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** an operator reading a coverage figure to decide whether a run can close
**I want** a rejected-and-repaired unit told apart from one nobody ever opened
**So that** the number stops sending me to review eighteen units that need nothing

## Notes

Delivers criterion 2 of CR0506, and it is the criterion the whole CR was filed for.
`critic.sprint_covers_independently` is satisfied only by an APPROVE, so a batch that was
reviewed, rejected, repaired and mutation-verified reports with the same word as one nobody
looked at.

Measured three times in four days: **41 units** across three batches. On RUN-01KYPZ1G the
preflight said "28 of 44 unit(s) are covered by no independent review", and 18 of those 28
carried a real REJECT whose every finding had been repaired in-run. **The number was wrong by
18 out of 19, and wrong in the direction that hides the one real gap inside a crowd of false
ones.**

Both failure directions must be closed, and that is what makes this 5 points rather than 2.
Reading the middle state as uncovered manufactures work; reading it as covered would clear the
gate on an unrepaired rejection. A REJECT with no repair record must stay uncovered.

## Acceptance Criteria

### AC1: three states are reported, and the middle one is neither outer one

- **Given** three units - one with an APPROVE, one with a REJECT whose findings all carry repair
  records, one with no verdict at all
- **When** the coverage predicate runs
- **Then** it reports three distinct states, and the repaired unit is reported as neither
  approved nor unreviewed - a result that collapses the middle into either outer state is the
  defect this is filed from
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ThreeStateCoverageTests::test_approved_repaired_and_unreviewed_are_three_distinct_states

### AC2: an unrepaired REJECT stays uncovered

- **Given** a unit carrying a REJECT with no repair record, and one whose repair covers only some
  findings
- **When** the predicate runs
- **Then** neither counts as covered - the new state is earned by a recorded repair, so the route
  back to covered cannot be taken by having been rejected
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ThreeStateCoverageTests::test_an_unrepaired_or_partly_repaired_reject_stays_uncovered

### AC3: conformance reports the repaired state rather than "missing critiqued"

- **Given** a repaired unit reaching the conformance gate
- **When** conformance runs
- **Then** it names the repaired state instead of `missing critiqued (independent APPROVE
  verdict)` - the words it used for all eighteen units of RUN-01KYZKY5 and for units nobody
  opened alike, which is what sent that close to a waiver sweep
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::ThreeStateCoverageTests::test_conformance_names_the_repaired_state_not_missing_critiqued

### AC4: the gate's verdict on a repaired unit is stated, not inferred

- **Given** a batch whose units are all rejected-and-repaired
- **When** the close gate reads coverage
- **Then** whether that satisfies the gate is a single declared rule with a test either way, so
  a future reader learns the answer from the code rather than from whichever branch happened to
  run - `sprint_covers_independently` today answers this by accident of the APPROVE check
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ThreeStateCoverageTests::test_the_gates_treatment_of_a_repaired_unit_is_declared_and_tested_both_ways

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | Claude Opus 5 | Groomed against CR0506 criterion 2; both failure directions made separate criteria, and `Affects` widened to the critic test module the predicate's own tests land in |
