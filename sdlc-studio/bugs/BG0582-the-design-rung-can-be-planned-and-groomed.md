# BG0582: the design rung can be planned and groomed but not closed: sprint plan reads the rung and the close chain does not, so it demands Done for units the rung says correctly end at Ready

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01M05A5M close, 2026-08-16. Predicted by the adversarial goal review before the run opened - it flagged that the brief promised Review while the design rung ends at Ready - and confirmed at the close. BG0581 is the brief half of the same asymmetry; this is the closer half.
> **Created:** 2026-08-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`sprint plan --goal design` is rung-aware. It accepts an ungroomed batch, says so - 'this rung exists to groom them. The close reports what it actually produced' - and `anchor_status_block` (sprint.py:5474) states the terminal in terms: design-rung units 'correctly end at Ready with RED acceptance criteria'. The CLOSE chain reads none of that. `undelivered_blockers` contains no reference to the rung at all, and on a 12-unit design rung whose every story reached Ready exactly as intended, `sprint close --dry-run` raised 12 `status` stops ('its code landed and its status is still Ready'), 12 `done-gate` stops demanding Done, and 12 `sign-off` stops. The rung is offered by the planner and is unreachable through the closer.

## Steps to Reproduce

1. `sprint.py plan --worklist <ungroomed units> --goal design --write --sprint-goal '<goal>'` - accepted, rung recorded as design in run-state.json. 2. Groom every unit and transition the stories to Ready, which is the rung's stated terminal. 3. `sprint.py close --dry-run --retro RETROxxxx` - every unit raises a status stop for being at Ready, a done-gate stop demanding Done, and a sign-off stop. Measured 2026-08-16 on RUN-01M05A5M: 12 of 12 units, 45 stops in total. 4. `grep -c rung` over `undelivered_blockers` returns 0.

## Proposed Fix

The close chain must read the rung the run recorded, exactly as the planner does. `undelivered_blockers`, the done-gate fan-out and the sign-off lane should each derive their expected terminal from the run's rung rather than assuming the delivery one - the run state already carries it. The narrower alternative, if the rung is to stay delivery-only at the close, is for `sprint plan` to REFUSE `--goal design` rather than accept a run nothing can close; a rung that can be entered and not exited is worse than one that does not exist, because the work is done before the wall is met.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `sprint plan --goal design` is rung-aware.
- [ ] **AC2** The proposed fix lands, pinned by a test: The close chain must read the rung the run recorded, exactly as the planner does.

## Impact

Every grooming run. The design rung is the shipped answer to an ungroomed backlog - `sprint plan` refuses a batch at the delivery rung and names design as the route - so this is not an exotic path. A run that cannot close leaves its units terminal-but-unaccounted, which is precisely the state BG0580 was filed for, and the only exits are `--file-and-close` or `--force`. It also contradicts the repository's own record: the close stamp knows the rung and the gates that block do not, so the run's own paperwork disagrees with itself.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-16 | sdlc-studio | Filed |
