# BG1698: A unit approved in a ruled round past the cap stays dropped from the batch, so the close and the report do not credit it

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/scripts/tests/test_carry_discharge_rejoins_batch.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_run_end_to_end.py, changelog.d/BG1698.md
> **Evidence:** sdlc-studio/.local/run-state.json batch_changes: 14 'carried at the review cap' drops; 13 re-added by sprint.py batch add after their D0565-D0578 approvals; reference-review.md:509-516 (carry and discharge) names no re-add. Recurred in run twenty-four: RUN-01M84Z8Z's batch_changes drop BG1548 and BG1574 as carried, both were approved in round three and moved to Fixed, and its batch holds neither. Reproduced at cecc9dfe through `critic.py record` in a throwaway run, 2026-11-24.
> **Created:** 2026-11-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-22T02:02:17Z

## Summary

A REJECT at the review cap carries the unit: critic.py record files a carry bug and drops the unit from the open run's batch. reference-review.md says the carried unit may reach Done on an APPROVE from the reviewer who rejected, in the carrying run, and critic.py record --ruling DNNNN admits that round. But nothing returns the approved unit to the batch, and no page tells the operator to: the close, the retro scaffold and the sprint report then omit a unit that was delivered and Fixed in the run, so delivered points are understated and cost per point overstated. In run twenty-one 13 such units had to be re-added by hand with sprint.py batch add. The carry bug the cap filed also stays Open until closed by hand.

At HEAD `round_refusal` admits the discharging APPROVE (the carry's own exit, or a round a `--ruling` authorises) and `_record` writes it, and nothing in that path calls `run_state.add_to_batch`; the only callers are `sprint.py batch add`, `batch add-epic` and `batch swap`.

## Steps to Reproduce

1. Open a run holding US0101 and US0102. Record two REJECTs of US0101 by one reviewer: the second carries it, files BG0001 and drops it, and the batch reads `[US0102]`.
2. Record that reviewer's APPROVE of US0101 through `critic.py record` (it is admitted past the cap as the carry's exit; `--ruling DNNNN` admits the same round by decision).
3. The batch still reads `[US0102]`, `batch_changes` holds only the drop, and BG0001 is still Open. As filed, `sprint.py close` then scaffolds a retro whose Batch line omits US0101.

## Proposed Fix

When `critic.py record` writes a carried unit's discharging APPROVE inside the open run whose `batch_changes` dropped it as carried at the review cap, return the unit to that run's batch with `run_state.add_to_batch`, its reason naming the carry bug and any ruling; print that it rejoined the batch and that the carry bug is still Open, with the command that closes it; and say so in reference-review.md's carry and discharge paragraph. Closing the carry bug itself stays with `transition.py`, which runs its criteria.

## Acceptance Criteria

- [ ] **AC1** Given an open run whose batch dropped US0101 as carried at the review cap (carry bug BG0001), when the rejecting reviewer's APPROVE is recorded through `critic.py record`, then the run's batch holds US0101 again and `batch_changes` ends with an add for US0101 whose reason names BG0001. Fails on: the batch stays without US0101 and `batch_changes` holds only the drop.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_carry_discharge_rejoins_batch.py::CarryDischargeRejoinsBatchTests::test_the_discharging_approve_returns_the_unit_to_the_batch
- [ ] **AC2** Given the same carried unit and an accepted decision naming it, when the APPROVE is recorded with `--ruling DNNNN`, then the unit rejoins the batch as in AC1 and the add's reason names the ruling too. Fails on: the batch stays without the unit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_carry_discharge_rejoins_batch.py::CarryDischargeRejoinsBatchTests::test_a_ruled_approve_returns_the_unit_to_the_batch
- [ ] **AC3** Given a carried unit discharged in a later run whose batch already holds it, or an APPROVE recorded with no open run, when `critic.py record` writes it, then the batch is unchanged and no add is recorded. Fails on: a fix that adds on every APPROVE of a once-carried unit, writing a duplicate entry or a run state where none was open (this guard holds today).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_carry_discharge_rejoins_batch.py::CarryDischargeRejoinsBatchTests::test_no_add_outside_the_carrying_run
- [ ] **AC4** Given the discharge in AC1, when the operator reads the record's output and reference-review.md's carry and discharge paragraph, then both say the unit rejoins the carrying run's batch, and the output names BG0001 as still Open with the command that closes it. Fails on: the output says only that the APPROVE was recorded, and the page names no rejoin.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_carry_discharge_rejoins_batch.py::CarryDischargeRejoinsBatchTests::test_the_output_and_the_review_reference_name_the_rejoin

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-22 | sdlc-studio | Filed |
| 2026-11-22 | Claude Opus 5.5 (run twenty-one orchestrator) | Related to BG1277 but distinct: BG1277 is the closing-review row crediting a carried unit whose carry bug was delivered; this is the approved carried unit itself never returning to the batch |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced at cecc9dfe through `critic.py record` in a throwaway run, and seen again in run twenty-four (BG1548, BG1574); generated criteria replaced by four executable ones (plain and ruled discharge, a guard outside the carrying run, and the output and page); closing the carry bug left to `transition.py`, the output naming it; Affects drops sprint.py, test_critic.py and test_sprint.py; Points stay 2 |
| 2026-11-24 | orchestrator | Affects gains tests/test_lean_signed_run_end_to_end.py: line 313 pins a discharged unit as carried, which AC1 changes to delivered; the carry bug keeps its Known issues row (the CR builder's full-suite run) |
