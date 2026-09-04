# BG0645: critic.py brief --rejoinder ignores --phase plan-review and renders the delivery brief, so a re-review of a rejected test plan is briefed with a diff scope that does not exist

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-09-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

critic.py brief --unit X --seat Y --phase plan-review --rejoinder <verdict file> emits the DELIVERY re-review brief: 'You did NOT author this diff', a 'Diff scope (the unit's declared Affects - inspect with git diff/status)' block, and no test-plan section or plan-review return contract. The plan-review phase, which the same command renders correctly without --rejoinder, is dropped on the rejoinder path. A round-two plan review is therefore briefed to look for a diff before any code exists, which is the exact failure the plan-review brief's own text warns against. Hit on 2026-09-04 briefing round two of a six-unit plan review after three seats rejected in round one.

## Steps to Reproduce

1. critic.py brief --unit BG0641 --seat qa --phase plan-review > a.md (correct: test-plan section, no diff scope). 2. critic.py brief --unit BG0641 --seat qa --phase plan-review --rejoinder <a VERDICT/ISSUES/BLOCKING file> > b.md. 3. b.md carries 'Diff scope' and 'this diff' and no test plan; the phase flag had no effect.

## Proposed Fix

Route the rejoinder through the same phase switch as the first-round brief: a plan-review rejoinder quotes the prior verdict verbatim, restates the criteria and the CURRENT test plan (the artefact has been re-authored since the rejection - that is what a re-review judges), demands the probes be re-executed, and returns the plan-review contract. Pin it with a test that renders a plan-review rejoinder and asserts the absence of a diff scope and the presence of the test plan, beside the delivery-rejoinder control.

## Acceptance Criteria

- [ ] **AC1** Given a plan-review rejection recorded for a unit, when critic.py brief --phase plan-review --rejoinder is rendered, then the brief carries no diff scope, quotes the prior verdict, carries the unit's current test plan and returns the plan-review contract
  - **Verify:** manual - render the two briefs in the steps and compare; the executable verifier is authored when this is groomed, because its test does not exist yet (BG0643)
- [ ] **AC2** Given a delivery rejection, when the rejoinder is rendered with the default phase, then it carries the diff scope as today - the control
  - **Verify:** manual - render a delivery rejoinder for a Fixed unit with a recorded delivery REJECT and confirm the diff scope is present

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-04 | sdlc-studio | Filed |
