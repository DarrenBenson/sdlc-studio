# BG0279: the close chain runs its gate BEFORE --apply-signoff moves units to Done, so the green it reports is measured against a state the close then changes: a unit can pass at Review and be non-conformant the moment it becomes Done

> **Status:** Open
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Severity:** Medium
> **Points:** 3

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Detail

Found when a routine commit failed the gate on `main` the day after RUN-01KY7W1F closed green.

`US0412` was reported non-conformant, missing `verified`. It had closed **Done** in Sprint 1, in a
run whose own close chain printed `close [4/6] gate: ok - PASS`.

Both are true, because of the ORDER:

1. The close chain runs `gate` at step 4, while every unit still sits at **Review**.
2. `--apply-signoff` then runs AFTER the chain, recording sign-offs and transitioning units to
   **Done**.
3. Conformance requires a `- **Verified:**` annotation on a story at **Done**, not at Review.

So the gate judged a state that no longer existed by the time the close finished. The green was
honest about the tree it saw and silent about the tree it left. The next commit by anyone - here,
a parallel agent doing unrelated documentation work - inherits a red gate it did not cause.

This is the same shape as the run-state guarantee already honoured elsewhere: a step's report must
describe the state that step leaves behind, not an earlier one.

## Impact

Every close that uses `--apply-signoff`. The failure surfaces later, attributed to whoever commits
next, which is the most expensive way to learn it.

## Acceptance Criteria

### AC1: the close verifies the state it leaves behind

- **Given** a close that moves units to Done via `--apply-signoff`
- **When** the chain completes
- **Then** the gate (or an equivalent conformance check) is evaluated AFTER the transitions, so a green close means the resulting tree is green
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseGateOrderingTests::test_the_gate_is_evaluated_after_the_done_transitions

### AC2: a close that would leave the tree red says so rather than reporting green

- **Given** a batch whose units become non-conformant on reaching Done (a story with no Verified annotation against a manual AC)
- **When** the close runs with `--apply-signoff`
- **Then** it reports the failure and names the units, instead of printing a green gate from the pre-transition state
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseGateOrderingTests::test_a_close_that_would_leave_the_tree_red_reports_it

## Verification depth

Node-addressed pytest ACs over `test_sprint.py`, red before the code. Mutation-proven, and the
mutation mattered: the first three tests called the helper DIRECTLY, so deleting the call from
`_apply_signoff_tail` left them all green - a surviving mutant that proved the check was never
wired into the lane. That is LL0040 ("a library test is not a lane test"), walked into by the
author of the fix. A lane test driving the tail now kills it, and it immediately exposed a second
defect: the tail returns early on reconcile drift, so the report was swallowed in exactly the
messy closes that need it. It is now emitted above that early return, unconditionally.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Fixed and mutation-proven; a surviving mutant exposed the missing lane test |
