# US0820: sprint plan refuses a batch carrying an unruled green or unknown criterion

> **Status:** Draft
> **Delivers:** CR0569
> **Created:** 2026-09-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0250
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** sprint plan refuses a batch carrying an unruled green or unknown criterion
**So that** CR0569 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given `review.plan_falsifiability: block` and a batch in which one unit carries an unruled `green`, `never-fails` or `unreadable` criterion, when `sprint.py plan` runs, then it is REFUSED, and the refusal names the unit, the criterion, the class the probe returned, why that class is a finding, and the command that rules it. The three sibling gates on this path all name what, why and the fix; the remedy here is not one a reader can guess
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanFalsifiabilityGateTests::test_block_refuses_and_the_refusal_names_the_class_and_the_remedy
  - **Verified:** no
- [ ] **AC2** Given the SHIPPED DEFAULT and the same batch, when the plan runs, then it PROCEEDS at exit 0 with the finding reported. The default is `report`: every sibling review gate here is mode- or date-governed, and two ship advisory while their yield is measured, because a new blocking check on a command this size earns its place on a number rather than on assertion
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanFalsifiabilityGateTests::test_the_shipped_default_is_report_and_the_plan_proceeds
  - **Verified:** no
- [ ] **AC3** Given `off`, when the plan runs, then the probe is not driven at all and nothing is reported - including when the config spells it bare, which YAML reads as the boolean false rather than as the string, and which is the spelling the tooling itself prints; and given a value that is none of the three, the plan is REFUSED naming the key and the accepted set. A mode nobody recognises must not silently pick one
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanFalsifiabilityGateTests::test_off_collects_nothing_and_an_unknown_mode_is_refused_by_name
  - **Verified:** no
- [ ] **AC4** Given `block` and a batch whose every criterion is `red`, `not-yet-written`, `manual`, `not-probed`, `delivered` or ruled, when the plan runs, then it proceeds. The control, and its fixture carries a DELIVERED-but-not-transitioned unit, which is 4 of the 50 non-Draft, non-terminal units on this repository, measured, and the shape that would otherwise make the gate refuse the wrong thing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanFalsifiabilityGateTests::test_a_batch_whose_criteria_can_all_fail_proceeds_under_block
  - **Verified:** no
- [ ] **AC5** Given any of the above, when the criterion is exercised, then it is driven through `sprint.py plan` as the shipped command rather than through the gate function. The wiring is the half a library test does not reach, and this project has already shipped a gate that was green in-process while the command it was wired into printed nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanFalsifiabilityGateTests::test_the_gate_is_reached_through_the_shipped_plan_command
  - **Verified:** no
- [ ] **AC6** Given a batch containing an `unreadable` criterion - a class that appears in a refusal AND whose exit status, always non-zero, a second reader would take for `red` and let through - when the plan composes its message, then both the class it names and the refuse-or-proceed decision come from the probe's result rather than from a second reading of the exit code. Two readers of one question drift, and the reader that is wrong here is the one nobody runs by hand
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanFalsifiabilityGateTests::test_the_plan_reads_the_probe_rather_than_re_deriving_the_class
  - **Verified:** no

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/sprint.py, delete the falsifiability call from `cmd_plan` | Given `review.plan_falsifiability: block` and a batch in which one unit carries an unruled `green`, `never-fails` or `unreadable` criterion, when `sprint.py plan` runs, then it is REFUSED, and the refusal names the unit, the criterion, the class the probe returned, why that class is a finding, and the command that rules it. The three sibling gates on this path all name what, why and the fix; the remedy here is not one a reader can guess |
| AC1 | in .claude/skills/sdlc-studio/scripts/sprint.py, truncate the composed message to its leading tally | Given `review.plan_falsifiability: block` and a batch in which one unit carries an unruled `green`, `never-fails` or `unreadable` criterion, when `sprint.py plan` runs, then it is REFUSED, and the refusal names the unit, the criterion, the class the probe returned, why that class is a finding, and the command that rules it. The three sibling gates on this path all name what, why and the fix; the remedy here is not one a reader can guess |
| AC2 | in .claude/skills/sdlc-studio/scripts/sprint.py, flip the fallback literal for the mode to block | Given the SHIPPED DEFAULT and the same batch, when the plan runs, then it PROCEEDS at exit 0 with the finding reported. The default is `report`: every sibling review gate here is mode- or date-governed, and two ship advisory while their yield is measured, because a new blocking check on a command this size earns its place on a number rather than on assertion |
| AC3 | in .claude/skills/sdlc-studio/scripts/sprint.py, drive the probe under off and report what it returns | Given `off`, when the plan runs, then the probe is not driven at all and nothing is reported - including when the config spells it bare, which YAML reads as the boolean false rather than as the string, and which is the spelling the tooling itself prints; and given a value that is none of the three, the plan is REFUSED naming the key and the accepted set. A mode nobody recognises must not silently pick one |
| AC3 | in .claude/skills/sdlc-studio/scripts/sprint.py, compare the configured value as a string only, so the YAML boolean falls through to the refusal | Given `off`, when the plan runs, then the probe is not driven at all and nothing is reported - including when the config spells it bare, which YAML reads as the boolean false rather than as the string, and which is the spelling the tooling itself prints; and given a value that is none of the three, the plan is REFUSED naming the key and the accepted set. A mode nobody recognises must not silently pick one |
| AC3 | in .claude/skills/sdlc-studio/scripts/sprint.py, treat an unrecognised mode as report instead of refusing | Given `off`, when the plan runs, then the probe is not driven at all and nothing is reported - including when the config spells it bare, which YAML reads as the boolean false rather than as the string, and which is the spelling the tooling itself prints; and given a value that is none of the three, the plan is REFUSED naming the key and the accepted set. A mode nobody recognises must not silently pick one |
| AC4 | in .claude/skills/sdlc-studio/scripts/sprint.py, refuse whenever the probe returns any classified criterion | Given `block` and a batch whose every criterion is `red`, `not-yet-written`, `manual`, `not-probed`, `delivered` or ruled, when the plan runs, then it proceeds. The control, and its fixture carries a DELIVERED-but-not-transitioned unit, which is 4 of the 50 non-Draft, non-terminal units on this repository, measured, and the shape that would otherwise make the gate refuse the wrong thing |
| AC5 | in .claude/skills/sdlc-studio/scripts/sprint.py, leave the gate callable as a function and never call it from the plan command | Given any of the above, when the criterion is exercised, then it is driven through `sprint.py plan` as the shipped command rather than through the gate function. The wiring is the half a library test does not reach, and this project has already shipped a gate that was green in-process while the command it was wired into printed nothing |
| AC6 | in .claude/skills/sdlc-studio/scripts/sprint.py, recompute the label and the decision from each verifier's exit status | Given a batch containing an `unreadable` criterion - a class that appears in a refusal AND whose exit status, always non-zero, a second reader would take for `red` and let through - when the plan composes its message, then both the class it names and the refuse-or-proceed decision come from the probe's result rather than from a second reading of the exit code. Two readers of one question drift, and the reader that is wrong here is the one nobody runs by hand |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-09 | sdlc-studio | Created via `new` (deterministic) |
