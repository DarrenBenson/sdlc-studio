# BG0582: the design rung can be planned and groomed but not closed: sprint plan reads the rung and the close chain does not, so it demands Done for units the rung says correctly end at Ready

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Verification depth:** functional (all twelve criteria drive the real close chain over temp git repos at four rungs and across both unit types. Mutation: 14 mutants, each anchor asserted to occur exactly once, `__pycache__` purged and `python3 -B`, all 14 KILLED, restore byte-exact. EIGHT of the fourteen came from TWO adversarial rounds that both REJECTED. Round 1: a story-only fixture let a `type_ != "story"` skip survive all 895 tests, a single-shape fixture let `story_is_ungroomed` substitute for `unit_is_ungroomed`, and the scope was `!= "done"` rather than `== "design"`, moving the defect onto the plan and triage rungs. Round 2: that same scope error was STILL PRESENT in the sibling `_signoff_preflight`, dropping a hard done-gate blocker for those two rungs with no substitute bar; and the round-1 repair to `_report_preflight` had no test at all, both of its halves surviving all 898 tests. Six criteria exist only to catch over-correction, because the author of this repair was the session it unblocked)
> **Evidence:** RUN-01M05A5M close, 2026-08-16. Predicted by the adversarial goal review before the run opened - it flagged that the brief promised Review while the design rung ends at Ready - and confirmed at the close. BG0581 is the brief half of the same asymmetry; this is the closer half.
> **Created:** 2026-08-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`sprint plan --goal design` is rung-aware. It accepts an ungroomed batch, says so - 'this rung exists to groom them. The close reports what it actually produced' - and `anchor_status_block` (sprint.py:5474) states the terminal in terms: design-rung units 'correctly end at Ready with RED acceptance criteria'. The CLOSE chain reads none of that. `undelivered_blockers` contains no reference to the rung at all, and on a 12-unit design rung whose every story reached Ready exactly as intended, `sprint close --dry-run` raised 12 `status` stops ('its code landed and its status is still Ready'), 12 `done-gate` stops demanding Done, and 12 `sign-off` stops. The rung is offered by the planner and is unreachable through the closer.

## Steps to Reproduce

1. `sprint.py plan --worklist <ungroomed units> --goal design --write --sprint-goal '<goal>'` - accepted, rung recorded as design in run-state.json. 2. Groom every unit and transition the stories to Ready, which is the rung's stated terminal. 3. `sprint.py close --dry-run --retro RETROxxxx` - every unit raises a status stop for being at Ready, a done-gate stop demanding Done, and a sign-off stop. Measured 2026-08-16 on RUN-01M05A5M: 12 of 12 units, 45 stops in total. 4. `grep -c rung` over `undelivered_blockers` returns 0. 5. The `sign-off` stop cannot be cleared even by hand, which is what makes this a wall rather than an inconvenience: `critic.py signoff --unit US0625 ...` reports `sign-off SKIPPED for US0625: its status is 'Ready', which is neither terminal nor awaiting sign-off - the work has not been delivered` and writes `0 unit(s)`. So the verb that exists to satisfy the gate refuses the rung's own terminal, on the same delivery assumption. Three lanes, one premise.

## Proposed Fix

The close chain must read the rung the run recorded, exactly as the planner does. `undelivered_blockers`, the done-gate fan-out and the sign-off lane should each derive their expected terminal from the run's rung rather than assuming the delivery one - the run state already carries it. `critic.py signoff` needs the same, and it is the one to fix first: while it refuses, no amount of correct work clears the gate, because the operator cannot sign off a unit the tool declines to write. The narrower alternative, if the rung is to stay delivery-only at the close, is for `sprint plan` to REFUSE `--goal design` rather than accept a run nothing can close; a rung that can be entered and not exited is worse than one that does not exist, because the work is done before the wall is met.

## Acceptance Criteria

- [ ] **AC1** Given a run whose recorded rung is `design` and whose batch unit is groomed and at Ready, when `undelivered_blockers` reads it, then it reports NO status blocker - Ready is that rung's terminal.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ADesignRungIsJudgedAgainstItsOwnProductTests::test_a_groomed_unit_at_ready_does_not_block_a_design_rung
  - **Verified:** yes (2026-08-16)
- [ ] **AC2** Given a `design` rung whose batch carries an UNGROOMED unit, when `undelivered_blockers` reads it, then it BLOCKS naming that unit - the rung is exempt from the build rung's bar, never from its own.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ADesignRungIsJudgedAgainstItsOwnProductTests::test_an_ungroomed_unit_still_blocks_a_design_rung
  - **Verified:** yes (2026-08-16)
- [ ] **AC3** Given a `done` rung whose unit was delivered and left at Ready, when `undelivered_blockers` reads it, then it still reports the status blocker unchanged - the repair must not loosen the build rung it was scoped away from.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ADesignRungIsJudgedAgainstItsOwnProductTests::test_a_done_rung_is_exactly_as_strict_as_before
  - **Verified:** yes (2026-08-16)
- [ ] **AC4** Given a run state carrying no `goal` key, an empty one or whitespace, when `run_rung` reads it, then it answers `done` - most run states predate the rung, and defaulting anywhere else relaxes the delivery gates for every historical run.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ADesignRungIsJudgedAgainstItsOwnProductTests::test_an_absent_goal_is_treated_as_the_build_rung
  - **Verified:** yes (2026-08-16)
- [ ] **AC5** Given a `design` rung, when `_signoff_preflight` runs, then it emits exactly one NON-BLOCKING `sign-off` row naming the rung and no `done-gate` row - a skipped gate that says nothing reads identically to one that passed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ADesignRungIsJudgedAgainstItsOwnProductTests::test_the_skipped_delivery_gates_are_reported_not_silent
  - **Verified:** yes (2026-08-16)
- [ ] **AC6** Given a `done` rung, when `_signoff_preflight` runs, then it still emits a BLOCKING sign-off row - the two-role gate must keep being previewed for every build run.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ADesignRungIsJudgedAgainstItsOwnProductTests::test_a_done_rung_still_gets_its_blocking_signoff_row
  - **Verified:** yes (2026-08-16)

- [ ] **AC7** Given a `design` rung whose batch carries an ungroomed BUG, when `undelivered_blockers` reads it, then it BLOCKS naming that bug - a mixed batch is the normal case and a story-only bar exempts real work.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ADesignRungIsJudgedAgainstItsOwnProductTests::test_an_ungroomed_BUG_blocks_a_design_rung_too
  - **Verified:** yes (2026-08-16)
- [ ] **AC8** Given each ungroomed SHAPE `unit_is_ungroomed` reports - no-criteria, placeholder and derived-only - when `undelivered_blockers` reads a design batch carrying it, then it BLOCKS; the bar must not be pinned for the placeholder alone.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ADesignRungIsJudgedAgainstItsOwnProductTests::test_every_ungroomed_SHAPE_blocks_not_just_the_placeholder
  - **Verified:** yes (2026-08-16)
- [ ] **AC9** Given a `plan` or `triage` rung, when `undelivered_blockers` reads it, then it does NOT judge it against the design rung's product - those rungs select and sequence rather than groom, and judging them by grooming moves this defect one rung over instead of closing it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ADesignRungIsJudgedAgainstItsOwnProductTests::test_a_plan_rung_is_not_judged_against_the_design_rungs_product
  - **Verified:** yes (2026-08-16)

- [ ] **AC10** Given a `plan` or `triage` rung, when `_signoff_preflight` runs, then it still produces its blocking delivery preview and does NOT take the design rung's skip row - the sibling function must be scoped the same way, or the defect is relocated rather than removed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ADesignRungIsJudgedAgainstItsOwnProductTests::test_plan_and_triage_keep_the_signoff_and_done_gate_preview
  - **Verified:** yes (2026-08-16)
- [ ] **AC11** Given a close pre-flight that is READY but carries a non-blocking row, when `_report_preflight` renders it, then the row is printed - a skipped gate that prints nothing reads exactly like one that passed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheReadyCloseStillSaysWhatItSkippedTests::test_a_ready_close_still_prints_what_it_did_not_check
  - **Verified:** yes (2026-08-16)
- [ ] **AC12** Given a pre-flight page carrying both a blocking and a non-blocking row, when it renders, then the non-blocking one is labelled `reported not blocking` - an operator must not count eight refusals where three refuse.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TheReadyCloseStillSaysWhatItSkippedTests::test_a_non_blocking_row_is_labelled_as_one
  - **Verified:** yes (2026-08-16)

## Impact

Every grooming run. The design rung is the shipped answer to an ungroomed backlog - `sprint plan` refuses a batch at the delivery rung and names design as the route - so this is not an exotic path. A run that cannot close leaves its units terminal-but-unaccounted, which is precisely the state BG0580 was filed for, and the only exits are `--file-and-close` or `--force`. It also contradicts the repository's own record: the close stamp knows the rung and the gates that block do not, so the run's own paperwork disagrees with itself.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | delete the `if rung == "design"` early-return branch from `undelivered_blockers` in sprint.py, so it falls through to the delivery-status test | Given a run whose recorded rung is `design` and whose batch unit is groomed and at Ready, when `undelivered_blockers` reads it, then it reports NO status blocker - Ready is that rung's terminal. |
| AC2 | change that branch in sprint.py to `return []`, skipping the delivery gates and checking nothing in their place | Given a `design` rung whose batch carries an UNGROOMED unit, when `undelivered_blockers` reads it, then it BLOCKS naming that unit - the rung is exempt from the build rung's bar, never from its own. |
| AC3 | replace the branch guard in sprint.py with `if True:`, so a build run stops reporting units delivered and left at Ready | Given a `done` rung whose unit was delivered and left at Ready, when `undelivered_blockers` reads it, then it still reports the status blocker unchanged - the repair must not loosen the build rung it was scoped away from. |
| AC4 | change `run_rung`'s default in sprint.py from `done` to `design`, so every run state predating the rung is read as a grooming run | Given a run state carrying no `goal` key, an empty one or whitespace, when `run_rung` reads it, then it answers `done` - most run states predate the rung, and defaulting anywhere else relaxes the delivery gates for every historical run. |
| AC5 | change `_signoff_preflight` in sprint.py to return a bare `[]` for a non-done rung, skipping the gates silently instead of recording the skip | Given a `design` rung, when `_signoff_preflight` runs, then it emits exactly one NON-BLOCKING `sign-off` row naming the rung and no `done-gate` row - a skipped gate that says nothing reads identically to one that passed. |
| AC6 | delete the `rung != "done"` guard on `_signoff_preflight`'s early return in sprint.py, so a build run loses its sign-off preview entirely | Given a `done` rung, when `_signoff_preflight` runs, then it still emits a BLOCKING sign-off row - the two-role gate must keep being previewed for every build run. |
| AC7 | insert `if type_ != "story": continue` into `_rung_product_blockers` in sprint.py - the skip survived all 895 tests in test_sprint.py before this criterion existed | Given a `design` rung whose batch carries an ungroomed BUG, when `undelivered_blockers` reads it, then it BLOCKS naming that bug - a mixed batch is the normal case and a story-only bar exempts real work. |
| AC8 | change `_rung_product_blockers` in sprint.py to call `conformance.story_is_ungroomed`, which agrees on the placeholder shape and misses the other two | Given each ungroomed SHAPE `unit_is_ungroomed` reports - no-criteria, placeholder and derived-only - when `undelivered_blockers` reads a design batch carrying it, then it BLOCKS; the bar must not be pinned for the placeholder alone. |
| AC9 | widen the branch guard in sprint.py from `rung == "design"` back to `rung != "done"`, so a plan rung is told it produced no acceptance criteria | Given a `plan` or `triage` rung, when `undelivered_blockers` reads it, then it does NOT judge it against the design rung's product - those rungs select and sequence rather than groom, and judging them by grooming moves this defect one rung over instead of closing it. |
| AC10 | widen `_signoff_preflight`'s early return in sprint.py from `rung == "design"` back to `rung != "done"`, so plan and triage skip the done-gate preview with nothing in its place | Given a `plan` or `triage` rung, when `_signoff_preflight` runs, then it still produces its blocking delivery preview and does NOT take the design rung's skip row - the sibling function must be scoped the same way, or the defect is relocated rather than removed. |
| AC11 | delete the ready-path `elif` branch from `_report_preflight` in sprint.py, so a clean close prints nothing about the gates it did not run | Given a close pre-flight that is READY but carries a non-blocking row, when `_report_preflight` renders it, then the row is printed - a skipped gate that prints nothing reads exactly like one that passed. |
| AC12 | revert `_blocker_label(b)` to `_stage_label(b['stage'])` in sprint.py's pre-flight printer, so an advisory row renders identically to a refusal | Given a pre-flight page carrying both a blocking and a non-blocking row, when it renders, then the non-blocking one is labelled `reported not blocking` - an operator must not count eight refusals where three refuse. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-16 | sdlc-studio | Filed |
