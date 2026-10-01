# BG0851: The sprint report says the operator ruled nothing and no gate stood down when both happened

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_operator_interventions.py, changelog.d/BG0851.md
> **Depends on:** BG0848
> **Created:** 2026-09-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-29T15:25:43Z

## Summary

Found in a consuming web project's signed run (RUN-01M3PMW3, RPT0003): the operator resolved a deferred decision with `sprint decision resolve` (force a unit to Fixed), the unit was moved with `transition --force` (a Forced-override written on the artefact), and the operator ruled a one-verdict raise of the review cap. The signed report's Rulings section reads 'the operator ruled 0 time(s)' and Waivers in force reads 'no gate stood down for this seal', because it counts only decisions-log rows and accepted waivers - not resolved sprint decisions nor Forced-override fields inside the run window. The page the operator signs understates the operator's own interventions.

## Steps to Reproduce

Re-run at HEAD 46cb9acf on 2026-09-30 in a throwaway git tree built from the lean close fixture, batch US0101 and US0102, run opened an hour earlier:

1. `sprint.py decision defer --unit US0101 ...` then `sprint.py decision resolve --index 1 --choice force`: `decision for US0101 resolved: force (0 pending)`. The run state gains a `resolved_decisions` entry and no `rulings` entry.
2. `transition.py set --id US0101 --status Done --force`: `override: --force waived 1 gate(s), recorded (artefact field)`; the story carries `> **Forced-override:** 2026-09-30: --force waived 1 gate(s) on Done - ...`.
3. `sprint.py batch drop US0102`, then `transition.py set --id US0102 --status Done --force`: a second Forced-override, on a unit no longer in the batch.
4. `sprint_report.py build --run RUN-LEAN0001 --id RETRO0001` prints under Rulings "NOT MEASURED - the run records no rulings" and under Waivers in force "no gate stood down for this seal - the log was read and carries no accepted waiver dated inside this report's window".

Control: `decisions.py add --by operator` in the same run appends `{'id': 'D0001', 'by': 'operator', ...}` to the run's `rulings`, so that path is counted.

The signed RPT0012 (RUN-01M3RPSK) splits the same way. Rulings reads "the operator ruled 1 time(s)", which is D0288, recorded with `decisions.py add --by operator`, so the Rulings half does not reproduce on that path. Waivers in force reads "no gate stood down for this seal", although BG0852 carries a Forced-override dated 2026-09-30 inside the run's window (08:17:59Z to 13:56:11Z) and was dropped from the batch (carried at the review cap) before it was forced. The filed fix, which lists batch units only, would have missed it.

## Proposed Fix

`sprint decision resolve` records an operator ruling in the open run (`run_state.record_ruling`, by `operator`), as `decisions.py add --by operator` does. The Waivers in force section also lists every unit the run's batch held at any point, dropped units included, whose Forced-override is dated inside the run's window, naming the unit and the gate it waived; a filed page's own reading decides which rows it lists on re-derivation, as it already does for decision-log waivers, so a later override cannot move a signed page.

## Acceptance Criteria

- [ ] **AC1** Given an open run in which the operator resolves a deferred decision with `sprint.py decision resolve`, when `sprint_report.py build` derives the report, then Rulings reads "the operator ruled 1 time(s)", and 2 once a `decisions.py add --by operator` follows in the same run. Fails on: HEAD, where the resolve writes no ruling and the section reads 0 (NOT MEASURED on a run state with no `rulings` list)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_operator_interventions.py::OperatorInterventionTests::test_a_resolved_decision_counts_as_an_operator_ruling
  - **Verified:** yes (2026-10-01)
- [ ] **AC2** Given an open run in which a batch unit and a unit dropped from the batch are each moved with `transition.py set --force`, and a third batch unit carries a Forced-override dated before the run's start day, when `sprint_report.py build` derives the report, then Waivers in force lists the two in-window units with the gate each waived, omits the third, and does not read "no gate stood down". Fails on: HEAD, which reads "no gate stood down"; on the filed fix (batch units only), which omits the dropped unit, the RPT0012 shape; and on listing every Forced-override field whatever its date, which lists the third
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_operator_interventions.py::OperatorInterventionTests::test_every_forced_override_in_the_window_is_listed
  - **Verified:** yes (2026-10-01)
- [ ] **AC3** Given a run closed with `sprint.py close` and sealed with `sprint.py sign`, when a unit the run dropped from its batch, still at Review with unverified ACs, is then moved to Done with `transition.py set --force` on the same day, then `sprint_report.py check --report` still prints VALID. Fails on: a re-derivation that places the date-only Forced-override against the window without replaying the filed page's reading, which lists the late override and prints INVALIDATED
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_operator_interventions.py::OperatorInterventionTests::test_an_override_after_the_seal_does_not_move_the_signed_page
  - **Verified:** yes (2026-10-01)

- [ ] **AC4** Given this repository's signed RPT0012, whose run (RUN-01M3RPSK) carried D0288 in its rulings and BG0852's Forced-override dated 2026-09-30 inside its window on a unit dropped from its batch, when `sprint_report.py check --report RPT0012` runs after the change, then it still prints VALID, as it does at HEAD. Fails on: a new counting rule applied to a page signed before it, which lists BG0852's override on the re-derivation, a row the signed page does not hold, and prints INVALIDATED
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_report_operator_interventions.py::OperatorInterventionTests::test_a_page_signed_before_the_rule_still_checks_valid
  - **Verified:** yes (2026-10-01)

## Impact

The signed page misreports how much the human steered the run - the one thing a lights-out report must state plainly.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-29 | sdlc-studio | Filed |
| 2026-09-30 | sprint planning | Groomed: premise re-run at HEAD - `sprint decision resolve` records no ruling and in-window Forced-overrides are not listed (holds); `decisions.py add --by operator` is counted (RPT0012 reads 'the operator ruled 1 time(s)', D0288) while its Waivers section omits BG0852's Forced-override on a dropped unit; fix widened from batch units to every unit the batch held; three executable criteria (resolve counted, in-window overrides listed including dropped units, a later override does not move a signed page); Points 2 to 3; Affects gains sprint.py and a lean test, drops the two test_sprint_report.py paths. |
| 2026-09-30 | sprint planning | Regroomed after goal review round 1: AC4 added - the signed RPT0012 (D0288 in its rulings, BG0852's in-window Forced-override on a dropped unit) still checks VALID after the change, as it does at HEAD (`VALID: RPT0012 re-derives to the fingerprint it records (023473f5406ef653)`); Depends on BG0848, since AC3 signs a run and would read INVALIDATED on BG0848's defect; Points 3 to 5 (four criteria across sprint.py and sprint_report.py). |
