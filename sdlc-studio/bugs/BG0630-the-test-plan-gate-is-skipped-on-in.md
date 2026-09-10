# BG0630: the test-plan gate is skipped on In Progress to Done, so a unit that entered before its rejection was recorded reaches terminal without it ever being checked

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Verification depth:** functional (authored at plan time as the tier this unit is driven to; the derived half is written by `verify_ac.py depth --write` at delivery, never by hand)
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

> **Re-measured 2026-09-08 after plan review.** The earlier figures came from
> `critic-verdicts.md`, the DELIVERY ledger, which this gate never reads. On the plan-review
> ledger at kind `test-plan`: 77 units ever rejected and 63 of them terminal. The walled
> population is the one the GATE would compute, standing rejection AND no repair clearing it,
> which is **16 bugs at Fixed**: BG0516, BG0521, BG0524, BG0530, BG0533, BG0541, BG0560,
> BG0568, BG0593, BG0594, BG0595, BG0596, BG0597, BG0598, BG0614, BG0653. A first count of 12
> read the standing verdict alone and was wrong in both directions - five of its twelve have
> answered their rejections and cannot reach the refusal, and nine others it never named are
> walled. AC5's fixture is built on one of the sixteen.

- [ ] **AC1** Given a unit that entered In Progress before its plan-review REJECT was recorded, when it is transitioned to a TERMINAL status - `Done` for a story, `Fixed` for a bug - then it is REFUSED. The verdict is consulted at the transition that makes the work permanent, not only at the one that starts it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::TestPlanGateEntryTests::test_the_gate_applies_on_the_in_progress_to_terminal_route
  - **Verified:** no
- [ ] **AC2** Given the same unit taken DIRECTLY to a terminal status without passing through In Progress, then it is refused too. Measured on a fixture with a standing rejection on record: `Open -> In Progress` is refused today while BOTH `In Progress -> Fixed` and a direct `Open -> Fixed` exit 0, so a fix that adds only the first route leaves the second wide open and every unit this bug is about is a bug
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::TestPlanGateEntryTests::test_a_direct_route_to_a_terminal_status_is_refused_too
  - **Verified:** no
- [ ] **AC3** Given a unit whose plan review carries an independent APPROVE, when it moves to a terminal status by either route, then it passes - the positive control, because a gate that now fires on the ordinary route must still let a properly reviewed unit through, and both routes are green at HEAD so each discriminates only through its mutant
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::TestPlanGateEntryTests::test_an_approved_plan_review_passes_on_both_routes
  - **Verified:** no
- [ ] **AC4** Given a workspace where `review.test_plan_after` is unset, when any unit reaches a terminal status, then the gate does not fire at all. The new firing sits INSIDE the dated adoption cutoff, per RETRO0098, because a gate that refuses a whole backlog is switched off rather than satisfied
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::TestPlanGateEntryTests::test_the_new_firing_sits_inside_the_dated_cutoff
  - **Verified:** no
- [ ] **AC5** Given one of the 16 bugs already at Fixed the gate would refuse, when nothing is done to it, then this change does not reopen it - the gate fires on a transition, never retrospectively; and when such a bug IS reopened and re-fixed, that transition is REFUSED until the rejection is answered. The behaviour is decided here rather than deferred to whatever the implementation happens to do
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::TestPlanGateEntryTests::test_a_reopened_and_refixed_bug_must_answer_its_rejection_first
  - **Verified:** no

## Impact

The gate is enforced by accident of ordering. A unit rejected before it starts is held to it; a unit rejected after it starts is not, and nothing reports the difference. That makes the recorded verdict decorative for most of the corpus, and it means the cheapest possible finding - a plan review that catches a defect before code - has no effect at all on the units most likely to receive one, which are the ones already being worked.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/transition.py, reinstate the `from_canon not in _IMPL_TARGETS` early return at the gate's second call site | Given a unit that entered In Progress before its plan-review REJECT was recorded, when it is transitioned to a TERMINAL status - `Done` for a story, `Fixed` for a bug - then it is REFUSED. The verdict is consulted at the transition that makes the work permanent, not only at the one that starts it |
| AC2 | in .claude/skills/sdlc-studio/scripts/transition.py, narrow the new firing to transitions whose source status is In Progress | Given the same unit taken DIRECTLY to a terminal status without passing through In Progress, then it is refused too. Measured on a fixture with a standing rejection on record: `Open -> In Progress` is refused today while BOTH `In Progress -> Fixed` and a direct `Open -> Fixed` exit 0, so a fix that adds only the first route leaves the second wide open and every unit this bug is about is a bug |
| AC3 | in .claude/skills/sdlc-studio/scripts/transition.py, delete the `critic.is_independent` branch at the terminal-route site | Given a unit whose plan review carries an independent APPROVE, when it moves to a terminal status by either route, then it passes - the positive control, because a gate that now fires on the ordinary route must still let a properly reviewed unit through, and both routes are green at HEAD so each discriminates only through its mutant |
| AC4 | in .claude/skills/sdlc-studio/scripts/transition.py, delete the `_plan_gate_active` call at the terminal-route site, leaving the gate unconditional | Given a workspace where `review.test_plan_after` is unset, when any unit reaches a terminal status, then the gate does not fire at all. The new firing sits INSIDE the dated adoption cutoff, per RETRO0098, because a gate that refuses a whole backlog is switched off rather than satisfied |
| AC5 | in .claude/skills/sdlc-studio/scripts/transition.py, skip the gate for any unit whose artefact already records a terminal status in its revision history | Given one of the 16 bugs already at Fixed the gate would refuse, when nothing is done to it, then this change does not reopen it - the gate fires on a transition, never retrospectively; and when such a bug IS reopened and re-fixed, that transition is REFUSED until the rejection is answered. The behaviour is decided here rather than deferred to whatever the implementation happens to do |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Filed |
| 2026-09-08 | Claude Fable 5.1 | Blast radius re-measured at the goal review, where the engineering seat found the figure stale by half. On this ledger today: 167 units have ever carried a REJECT and 155 of them are terminal, against the 44 and 41 recorded when this was filed on 2026-08-27 - the ledger has roughly quadrupled since. The repair's migration cost scales with that number, which is why this unit is ordered LAST in its batch: its fix changes when the test-plan gate fires and would otherwise wall its own batch-mates while they are In Progress carrying a standing rejection |
| 2026-09-10 | Claude Opus 5 | Delivered. The gate fires again at the terminal transition - `Done` for a story, `Fixed` for a bug - by whatever route reached it, inside the `review.test_plan_after` cutoff and deduplicated against the entry firing. Measured through the shipped command at the base of this change on a fixture carrying a standing REJECT: `Open -> In Progress` refused, while `In Progress -> Fixed` and a direct `Open -> Fixed` both exit 0; after it both are refused, and an independent APPROVE still passes on both routes. The walled population re-measured through the gate's own reading over this repository's bugs: 48 carry a standing test-plan REJECT, 34 of those sit at Fixed, and 16 of those have no repair clearing it - BG0516, BG0521, BG0524, BG0530, BG0533, BG0541, BG0560, BG0568, BG0593, BG0594, BG0595, BG0596, BG0597, BG0598, BG0614, BG0653 - confirming the figure the criteria note records. One existing fixture needed a test plan and an independent approval to reach the guard it tests: a machine-filed survivor bug carries neither. All five declared mutants applied and killed |
