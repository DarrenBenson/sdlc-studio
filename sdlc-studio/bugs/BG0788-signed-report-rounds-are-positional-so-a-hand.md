# BG0788: Signed-report rounds are positional, so a hand-deleted verdict row goes unseen when a same-day later run re-reviewed the unit, and verdict rows carry no run id

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Created:** 2026-09-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-26T15:18:42Z

## Summary

After BG0787, a signed report's unit rounds are the run's rows between its own review base and the fewest rows a later run found. The bound is positional: when a later run on the same UTC day re-reviewed the unit, deleting one of the signed run's own rows slides the later row into the slice and check reads VALID. The bound also lives in the later run's gitignored, unsigned record. Verdict rows carry only a date, so a same-day review outside any run, or a later run reviewing a unit outside its batch, still invalidates. Found by BG0787's QA review; ruled out of BG0787's AC2 under D0277 as the same trust-root class as CR0599.

## Steps to Reproduce

Sign a report; open a later run the same day that reviews a batch unit; delete the signed run's own REJECT row for that unit; check reads VALID.

## Proposed Fix

Record a run id (or a digest of the unit's rows) on each verdict row or at the review base, so the report counts rows by identity, not position; lands with CR0599's tracked signature record.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: After BG0787, a signed report's unit rounds are the run's rows between its own review base and the fewest rows a later run found.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Sign a report; open a later run the same day that reviews a batch unit; delete the signed run's own REJECT row for that unit; check reads VALID.
- [ ] **AC3** The proposed fix lands, pinned by a test: Record a run id (or a digest of the unit's rows) on each verdict row or at the review base, so the report counts rows by identity, not position; lands with...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Filed |
