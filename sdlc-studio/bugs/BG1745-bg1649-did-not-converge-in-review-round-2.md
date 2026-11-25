# BG1745: BG1649 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG1649.md
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M87B5M - raised during the run, 2026-11-25T01:45:27Z

## Summary

BG1649 was rejected at round 2, the review cap, by agent-a5ff50ac77d8044c9 (engineering), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] the close hint's id spelling is unpinned (sprint.py:10535, test\_sprint.py:11819 and 11827): `_lane_return_hint` prints `sdlc_md.display_id(root, uid)` because `lanes_in_flight` holds each unit by its `norm_id` (run\_state.record\_lane\_start), which drops a v3 id's dash, but LaneInFlightCloseTests runs only US0101, whose two spellings agree, so the mutant `shown = uid` passes both its tests. Re-tested in isolation on a v3 fixture (US-01M6XQJF in flight and Done): HEAD names `sprint.py lane return --units US-01M6XQJF`, the mutant names `sprint.py lane return --units US01M6XQJF`, a key no artefact file carries, which is the defect `display_id` exists to prevent (the command itself still runs, as `lane return` reads either spelling). The call is this unit's own, absent at the base and added by 45045c034, and the line it is appended to already prints the norm id, so dropping it is the edit a later change makes with the suite green. A v3-id case in LaneInFlightCloseTests closes it. No open bug covers it; RULINGS: Round one's "the finishing step the refusal names is not the return `lane accept` would have run": CLOSED. The hint and the return come from one `_return_argv`, and my probe of a bug's refused move (BG0001 on the LaneAcceptTests fixture, an open run with its lane started, `lane accept --tokens 77 --gap` holding an apostrophe) printed `transition.py set --id BG0001 --status Fixed`, then `sprint.py lane return --units BG0001 --claimed 'Fixed on an independent APPROVE (round 1)' --timeout 300 --tokens 77 --gap ...`. After the hand move to Fixed, the shlex-split hint exited 0, recorded the 77 delegated tokens and emptied `lanes_in_flight`. `verify_ac.py run --id BG1649 --dry-run` ac=3 pass=3 in my detached worktree, where the declared suites pass. My mutant hard-coding the hint's status as Done also survives the AC1 test, which exercises only a story, but the bug path prints Fixed by the probe above and a constant in place of the type's status is not a plausible edit, so it is a remark, not a finding. Claim inventory: the fragment, the `_return_argv` and `_lane_return_hint` docstrings, the LaneInFlightCloseTests docstring, the refusal's "The verdict is recorded and the criteria are green" (the record and `verify_ac.py run` precede the move) and the commit body's BG1649 paragraph are TRUE against the probes and tests above.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1649 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1649 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] the close hint's id spelling is unpinned (sprint.py:10535, test\_sprint.py:11819 and 11827): `_lane_return_hint` prints `sdlc_md.display_id(root, uid)` because `lanes_in_flight` holds each unit by its `norm_id` (run\_state.record\_lane\_start), which drops a v3 id's dash, but LaneInFlightCloseTests runs only US0101, whose two spellings agree, so the mutant `shown = uid` passes both its tests. Re-tested in isolation on a v3 fixture (US-01M6XQJF in flight and Done): HEAD names `sprint.py lane return --units US-01M6XQJF`, the mutant names `sprint.py lane return --units US01M6XQJF`, a key no artefact file carries, which is the defect `display_id` exists to prevent (the command itself still runs, as `lane return` reads either spelling). The call is this unit's own, absent at the base and added by 45045c034, and the line it is appended to already prints the norm id, so dropping it is the edit a later change makes with the suite green. A v3-id case in LaneInFlightCloseTests closes it. No open bug covers it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1649 AC1 still passes: Given an APPROVE whose `transition.py set` refuses, when `lane accept` prints its refusal, then it names the finishing step (`transition.py set ...` then `sprint.py lane return --units <ID>`). Fails on: the `transition.py set` branch of `_accept` names no next step.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_a_refused_transition_names_the_lane_return_that_finishes_the_unit
- [ ] **AC3** BG1649 AC2 still passes: Given a unit finished by hand after that refusal and still in `lanes_in_flight`, when `sprint.py close` runs, then its in-flight note names `sprint.py lane return --units <ID>` as the command that clears a lane whose unit is already terminal. Fails on: the note says only that the span reads NOT MEASURED.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneInFlightCloseTests::test_a_terminal_unit_in_flight_names_the_lane_return_that_clears_it
- [ ] **AC4** BG1649 AC3 still passes: Given the same unit, when `sprint.py lane return --units <ID>` is run after the hand transition, then the unit leaves `lanes_in_flight` and its span closes (positive control for the named command). Fails on: a named command that does not clear the lane.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_lane_return_after_a_hand_transition_clears_the_lane

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
