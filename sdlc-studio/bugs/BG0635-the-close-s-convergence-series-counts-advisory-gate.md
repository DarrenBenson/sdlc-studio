# BG0635: the close's convergence series counts ADVISORY gate lanes as outstanding blockers, so the review-repair loop can never converge and every close eventually hits the round cap

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, sdlc-studio/.config.yaml
> **Verification depth:** functional [[derived: criteria 4; plan rows 5; executed 5; killed 5; survived 0; not-run 0; entry point 0 of 4 criteria through the shipped CLI, 4 in-process | fp 05a1630bbd39 ]] (every criterion driven through the shipped command in a throwaway fixture, with the paired control beside each refusal)
> **Created:** 2026-08-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`loop_termination`short-circuits to CONVERGED when the latest attempt's outstanding count is zero, and its own comment says why: the cap read only the LENGTH, so a finished loop was refused, and raising the cap merely moves the number at which that happens. But the count it reads is`len(pre['blockers'])`, and `pre['blockers']`includes the gate lanes the very same pre-flight prints as`[gate, reported not blocking]`. This repository always carries four of them - constitution, doc-surface, disclosure and mutation - so the series can never reach zero, the converged branch is unreachable, and every close is stopped by the cap with the message 'the review-repair loop is NOT converging' while the real blocker set is empty. RUN-01M11MEP recorded 5, 5, 4, 4 with all ten units signed off, every rejection repaired and zero outstanding findings.

## Steps to Reproduce

1. Take a run whose real blockers are cleared but whose repo carries any advisory gate lane.
2. Run `sprint.py close --retro RETROxxxx`up to`review.max_rounds` times.
3. Each attempt records `outstanding` equal to the advisory-lane count, never 0.
4. The close stops with 'the review-repair loop is NOT converging' and 'Hand off with the outstanding set named' - while the outstanding set contains only lanes it has just described as not blocking.
5. Raising `review.max_rounds` does not help: the next attempt records the same non-zero count.

## Proposed Fix

Count only BLOCKING blockers into the convergence series. The pre-flight already distinguishes them - it prints `[gate, reported not blocking]`for the advisory ones - so the information is present at the point the count is taken and is simply not used.`loop_termination`itself is correct and needs no change; the defect is in what is handed to it. Assert the property rather than the instance: a pre-flight whose every blocker is non-blocking must record`outstanding` 0, so the converged branch its own comment describes becomes reachable.

## Acceptance Criteria

- [ ] **AC1** Given a close pre-flight whose blockers ALL carry `blocking: false`, when the attempt is recorded, then the row reads `outstanding: 0`AND its`stages`list is EMPTY. Both cells, because they are written from different expressions:`sprint.py`:7691 counts `pre["blockers"]`while`:7693`derives`stages`from the same unfiltered list, so fixing only the count writes the self-contradictory row`outstanding: 0, stages: ["gate"]` - a converged attempt that still names the lane it converged past
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LoopConvergenceTests::test_an_all_advisory_preflight_records_zero_and_no_stages
- [ ] **AC2** Given a pre-flight carrying one BLOCKING lane alongside advisory ones, when the attempt is recorded, then `outstanding`counts the blocking lane ONLY and`stages`names only its stage. The positive control: counting nothing at all, or emptying`stages` unconditionally, satisfies AC1 on its own
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LoopConvergenceTests::test_a_blocking_lane_is_still_counted_and_named
- [ ] **AC3** Given a run whose recorded attempts already equal the cap and whose real blocker set is empty, when `sprint.py close`is run as a SUBPROCESS, then it proceeds past the convergence check and prints a stage BEYOND it - asserted on a marker the close emits after that point, never on the ABSENCE of the non-convergence message, because`_record_close_attempt` sits after two earlier returns and a close that exits early omits that message for an unrelated reason
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LoopConvergenceTests::test_a_converged_run_at_the_cap_reaches_a_later_stage
- [ ] **AC4** Given this repository's own config, when the fix lands, then the `review.max_rounds`key is REMOVED rather than set to a number, and each consumer takes its own shipped default. No single value is correct for both:`sprint.py`'s close-attempt cap defaults to 4 and `critic.py`'s review-round ceiling to 3, and the one key feeds both - so 4 loosens the review ceiling past the operator's D0175 ruling and 3 tightens the close budget below stock. Removal is the precedent the corpus already carries from BG0517, and D0177's authorisation of the interim value expires on this commit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LoopConvergenceTests::test_the_project_config_pins_no_round_cap

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/sprint.py`, drop the `held_blockers`call from the count expression | Given a close pre-flight whose blockers ALL carry`blocking: false`, when the attempt is recorded, then the row reads `outstanding: 0`AND its`stages`list is EMPTY. Both cells, because they are written from different expressions:`sprint.py`:7691 counts `pre["blockers"]`while`:7693`derives`stages`from the same unfiltered list, so fixing only the count writes the self-contradictory row`outstanding: 0, stages: ["gate"]` - a converged attempt that still names the lane it converged past |
| AC1 | in `.claude/skills/sdlc-studio/scripts/sprint.py`, swap the `stages`comprehension back to the unfiltered list, leaving the count alone | Given a close pre-flight whose blockers ALL carry`blocking: false`, when the attempt is recorded, then the row reads `outstanding: 0`AND its`stages`list is EMPTY. Both cells, because they are written from different expressions:`sprint.py`:7691 counts `pre["blockers"]`while`:7693`derives`stages`from the same unfiltered list, so fixing only the count writes the self-contradictory row`outstanding: 0, stages: ["gate"]` - a converged attempt that still names the lane it converged past |
| AC2 | in `.claude/skills/sdlc-studio/scripts/sprint.py`, set the count to a literal zero so no lane is ever counted, advisory or not | Given a pre-flight carrying one BLOCKING lane alongside advisory ones, when the attempt is recorded, then `outstanding`counts the blocking lane ONLY and`stages`names only its stage. The positive control: counting nothing at all, or emptying`stages` unconditionally, satisfies AC1 on its own |
| AC3 | in `.claude/skills/sdlc-studio/scripts/sprint.py`, delete the cap check from `loop_termination`so the loop never stops at all | Given a run whose recorded attempts already equal the cap and whose real blocker set is empty, when`sprint.py close`is run as a SUBPROCESS, then it proceeds past the convergence check and prints a stage BEYOND it - asserted on a marker the close emits after that point, never on the ABSENCE of the non-convergence message, because`_record_close_attempt` sits after two earlier returns and a close that exits early omits that message for an unrelated reason |
| AC4 | in `sdlc-studio/.config.yaml`, insert a `max_rounds`line under the`review:`key in the project config | Given this repository's own config, when the fix lands, then the`review.max_rounds`key is REMOVED rather than set to a number, and each consumer takes its own shipped default. No single value is correct for both:`sprint.py`'s close-attempt cap defaults to 4 and `critic.py`'s review-round ceiling to 3, and the one key feeds both - so 4 loosens the review ceiling past the operator's D0175 ruling and 3 tightens the close budget below stock. Removal is the precedent the corpus already carries from BG0517, and D0177's authorisation of the interim value expires on this commit |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-29 | sdlc-studio | Filed |
