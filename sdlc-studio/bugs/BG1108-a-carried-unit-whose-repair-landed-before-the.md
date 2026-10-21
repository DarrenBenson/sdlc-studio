# BG1108: A carried unit whose repair landed before the new run's base has an empty review diff, so its redelivery review cannot block

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_carried_review_base.py, changelog.d/BG1108.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Evidence:** Goal review for run three, 2026-10-21. The engineering seat: 'BG0962's code and BG1078's predate the base (922b9d6c, 940cdda5), so the brief's git diff (critic.py:2786-2790) is empty and every finding reads as pre-existing: neither review can block.' The QA seat found the same. For this run, BG1078's grooming note names `git diff c6f2239c -- <Affects>` by hand.
> **Created:** 2026-10-21
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-21T07:02:04Z

## Summary

`critic.py brief` scopes a unit's diff to `git diff <run base> -- <Affects>` (critic.py:2786-2790), using the base of the run that holds the unit. When a unit is carried at the review cap but its repair commit has already landed on main, which is how US1076's round-2 repair 940cdda5 landed before BG1078 was carried, the next run's base is after the repair. The diff the brief names is then empty. Under the review rule, only a regression or a newly introduced defect blocks, so every finding on that repair reads as pre-existing and the redelivery review cannot block. BG0962 has the same shape for its 2026-10-07 fix, 922b9d6c.

## Steps to Reproduce

Carry a unit at the review cap after its repair commit is on main, plan it into a new run, then run `critic.py brief --unit <carried bug> --seat qa`: the diff line names the new run's base, and `git diff <base> -- <Affects>` is empty.

## Proposed Fix

Record, when a unit is carried, the commit its capping REJECT judged, and have the brief of the carried bug's redelivery scope its diff from that commit. Alternatively, let the run record a per-unit review base that the brief reads before the run's own.

## Acceptance Criteria

- [ ] **AC1** The brief for a carried unit's redelivery names a diff from the commit its capping REJECT judged, and that diff holds the repair landed before the new run
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_carried_review_base.py

## Impact

A carried unit's redelivery can be approved over a diff no reviewer was shown, or its findings dismissed as pre-existing.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-21 | Claude Opus 5.5 | Filed |
