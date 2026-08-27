# BG0630: the test-plan gate is skipped on In Progress to Done, so a unit that entered before its rejection was recorded reaches terminal without it ever being checked

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** Found 2026-08-27 by an independent plan review of BG0629, which corrected that bug's own wrong claim that a direct Ready-to-Done escapes the gate - it does not. Condition quoted from transition.py:1046-1049 against `_IMPL_TARGETS` at :791. Population measured from the plan-review ledger: 44 units have ever carried a REJECT and 41 are at Done or Fixed.
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The test-plan gate fires when `target_canon in _IMPL_TARGETS and from_canon not in _IMPL_TARGETS`, and `_IMPL_TARGETS` is `{In Progress, Review, Done}`. So it fires on `Ready -> In Progress` and on a direct `Ready -> Done`, and is SKIPPED on `In Progress -> Done` and `Review -> Done`.

The skip is deliberate and documented as idempotency for a forward walk: a unit that passed the gate on entry should not be asked again at every later step. But it makes the gate order-dependent rather than strict. A rejection recorded AFTER a unit started is never checked by anything, because the only transition left is one the gate skips. 41 of the 44 units ever rejected at plan review are at Done or Fixed, which is what that looks like from the corpus.

This is filed separately from BG0629 on the reviewer's ruling, and the reasoning is recorded because it is easy to re-merge them: BG0629's evidence is three units that cannot ENTER In Progress, and it does not reach this. Reversing the skip is a second behaviour change with its own blast radius, not a detail of the first.

## Steps to Reproduce

1. Move a unit to In Progress while its plan review is clean. 2. Record a plan-review REJECT for it. 3. Transition it to Done. 4. It succeeds - `from_canon` is already in `_IMPL_TARGETS`, so the gate is skipped and the rejection is never consulted. Measured over the ledger: 41 of 44 ever-rejected units sit at Done or Fixed.

## Proposed Fix

Decide what the gate means, then make it mean that at both ends. Re-firing on the terminal transition is the obvious repair and it is not free: every unit currently In Progress or Review carrying a standing rejection is walled, and every Fixed bug re-opened and re-fixed re-enters the gate. Three constraints on whichever answer ships. It must sit INSIDE `_plan_gate_active`'s `review.test_plan_after` cutoff - RETRO0098 records that exact mistake already being made once, a lane placed outside the cutoff it belonged in, and `_plan_gate_active`'s docstring says why: a gate that refuses every unit in a backlog is one that gets switched off wholesale rather than satisfied. It must land AFTER BG0629, or it walls units whose rejections no action can clear. And it must state what happens to the 16 Fixed bugs on any future re-fix.

## Acceptance Criteria

- [ ] **AC1** Given a unit that entered In Progress before its plan-review REJECT was recorded, when it is transitioned to Done, then it is REFUSED - the verdict is consulted at the transition that makes the work permanent, not only at the one that starts it
- [ ] **AC2** Given a unit whose plan review is clean, when it walks Ready to In Progress to Review to Done, then no step is refused and the gate is not re-litigated at each - the paired control, preserving the idempotency the skip exists for
- [ ] **AC3** Given a workspace where `review.test_plan_after` is unset, when any unit reaches Done, then the gate does not fire at all - the new firing sits INSIDE the adoption cutoff, per RETRO0098, because a gate that refuses a whole backlog is switched off rather than satisfied
- [ ] **AC4** Given a Fixed bug that is re-opened and re-fixed, when it reaches Fixed again, then the behaviour is whatever this bug's fix decides and a test says which - 16 of the corpus's Fixed bugs carry a standing rejection, so leaving it undecided is how this ships a surprise

## Impact

The gate is enforced by accident of ordering. A unit rejected before it starts is held to it; a unit rejected after it starts is not, and nothing reports the difference. That makes the recorded verdict decorative for most of the corpus, and it means the cheapest possible finding - a plan review that catches a defect before code - has no effect at all on the units most likely to receive one, which are the ones already being worked.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Filed |
