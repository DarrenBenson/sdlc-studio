# BG1698: A unit approved in a ruled round past the cap stays dropped from the batch, so the close and the report do not credit it

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/scripts/tests/test_carry_discharge_rejoins_batch.py, changelog.d/BG1698.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** sdlc-studio/.local/run-state.json batch_changes: 14 'carried at the review cap' drops; 13 re-added by sprint.py batch add after their D0565-D0578 approvals; reference-review.md:509-516 (carry and discharge) names no re-add.
> **Created:** 2026-11-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-22T02:02:17Z

## Summary

A REJECT at the review cap carries the unit: critic.py record files a carry bug and drops the unit from the open run's batch. reference-review.md says the carried unit may reach Done on an APPROVE from the reviewer who rejected, in the carrying run, and critic.py record --ruling DNNNN admits that round. But nothing returns the approved unit to the batch, and no page tells the operator to: the close, the retro scaffold and the sprint report then omit a unit that was delivered and Fixed in the run, so delivered points are understated and cost per point overstated. In run twenty-one 13 such units had to be re-added by hand with sprint.py batch add. The carry bug the cap filed also stays Open until closed by hand.

## Steps to Reproduce

1. Run a unit to a round-2 REJECT at the cap (it is dropped, carry bug filed). 2. Record an authorised round-3 APPROVE with critic.py record --ruling DNNNN and move the unit to Fixed. 3. sprint.py close scaffolds a retro whose Batch line omits the unit, and run-state.json's batch does not hold it.

## Proposed Fix

When critic.py record admits a carried unit's discharging APPROVE inside the run that carried it, return the unit to that run's batch (recording the add with the ruling), and move the carry bug it filed to Fixed; or, at minimum, say in reference-review.md and the record's output that the operator should batch add it.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: A REJECT at the review cap carries the unit: critic.py record files a carry bug and drops the unit from the open run's batch.
- [ ] **AC2** The proposed fix lands, pinned by a test: When critic.py record admits a carried unit's discharging APPROVE inside the run that carried it, return the unit to that run's batch (recording the add with...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-22 | sdlc-studio | Filed |
| 2026-11-22 | Claude Opus 5.5 (run twenty-one orchestrator) | Related to BG1277 but distinct: BG1277 is the closing-review row crediting a carried unit whose carry bug was delivered; this is the approved carried unit itself never returning to the batch |
