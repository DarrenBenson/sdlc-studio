# BG0850: A carried unit's discharge approval is refused by the review cap that another reviewer's rounds filled

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_no_plan_phase.py, .claude/skills/sdlc-studio/reference-review.md, changelog.d/BG0850.md
> **Created:** 2026-09-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-29T14:04:42Z

## Summary

Found in a consuming web project's run: a unit carried at the review cap is refused Fixed/Done until the reviewer who rejected it records an APPROVE (transition.py: 'reaches Done on an APPROVE from the reviewer who rejected it (the same reviewer id)'). When the re-delivery run's rounds were recorded under a different reviewer id (REJECT then APPROVE, two rounds), `critic.py record` then refuses the rejecting reviewer's APPROVE at the cap ('2 review round(s) recorded, at the cap of 2'), so no path discharges the old REJECT short of --force. Separately, `critic.py record` accepted both rounds from the different reviewer silently, although neither could ever discharge the carry - the operator learnt it only at transition time.

## Steps to Reproduce

Reproduced at HEAD 46cb9acf on 2026-09-30 through `critic.py record` and `transition.py set` in a throwaway git tree holding BG0001 (In Progress), in an open run whose batch is BG0001 and BG0002. The summary understates the scope: the rejecting reviewer's own discharge is refused, not only a discharge after another reviewer's rounds (RUN-01M3RPSK, BG0852, D0288).

1. `critic.py record --unit BG0001 --verdict REJECT --reviewer rev-a` twice: round 2 prints `BG0001 carried at the review cap: BG0002 holds the findings, and the unit leaves the open run's batch`.
2. `critic.py record --unit BG0001 --verdict APPROVE --reviewer rev-a` exits 2: record refused for BG0001: "BG0001 has 2 review round(s) recorded, at the cap of 2 (`review.max_rounds`). A unit still rejected at the cap is carried as a known issue, not reviewed again".
3. `transition.py set --id BG0001 --status Fixed` exits 1: `BG0001 carries an unanswered delivery REJECT (rev-a's REJECT of 2026-09-30; rev-a's REJECT of 2026-09-30)`.

The later-run shape refuses the same way: close that run, open one whose batch holds BG0001, record rev-b REJECT then rev-b APPROVE (both written, rounds 1 and 2), and `transition.py set --id BG0001 --status Fixed` still names rev-a's REJECT while rev-a's APPROVE is refused `at the cap of 2`. Controls: in a later run where rev-a gives round 1, the APPROVE is written and the transition to Fixed exits 0; and a discharge row written with `round_refusal` bypassed lets `transition.py set --id BG0001 --status Fixed --dry-run` exit 0 in both shapes, so the fix is confined to the cap check in critic.py.

## Proposed Fix

In `round_refusal`, admit past the cap one APPROVE on a CARRIED unit (its delivery REJECT at the cap was carried: a batch drop reasoned `carried at the review cap: <bug>`) when the reviewer is the one whose carried REJECT is outstanding; it answers that REJECT and opens no new round. Every other verdict past the cap is refused as today, including rev-b's and a REJECT from rev-a. A unit at the cap that was never carried is out of scope here (BG0841). The record-time warning floated in the summary is not needed once the rejecting reviewer can discharge.

## Acceptance Criteria

- [ ] **AC1** Given a unit carried at the cap in an open run by rev-a's two REJECTs, when `critic.py record --verdict APPROVE --reviewer rev-a` runs, then it exits 0, writes the row, and `transition.py set --status Fixed` then exits 0 with no `--force` and no Forced-override field. Fails on: HEAD, which refuses the APPROVE `at the cap of 2` and the transition on rev-a's unanswered REJECT
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py::CarriedDischargeTests::test_the_rejecting_reviewer_discharges_a_carried_unit
  - **Verified:** yes (2026-09-30)
- [ ] **AC2** Given that carried unit delivered again in a later run where rev-b recorded REJECT then APPROVE, when `critic.py record --verdict APPROVE --reviewer rev-a` runs, then it exits 0 and `transition.py set --status Fixed` exits 0. Fails on: a fix that admits the discharge only outside a run holding the unit, where the cap is counted from the unit's review base and rev-b's two rounds still fill it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py::CarriedDischargeTests::test_the_discharge_passes_after_another_reviewers_rounds
  - **Verified:** yes (2026-09-30)
- [ ] **AC3** Given the carried unit, when rev-b records an APPROVE past the cap, or rev-a records a REJECT past it, then `critic.py record` exits 2 and writes nothing, the refusal naming rev-a; and given a unit with two REJECTs from rev-a recorded while no run was open (nothing carried, no bug filed), rev-a's APPROVE is refused at the cap as today. Fails on: a fix that lifts the cap for any APPROVE on a unit whose last round is a REJECT, which writes rev-b's row and the never-carried unit's row
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_review_cap.py::CarriedDischargeTests::test_only_the_rejecting_reviewers_approve_on_a_carried_unit_passes
  - **Verified:** yes (2026-09-30)

## Impact

An approved, merged unit cannot reach Fixed without a forced override, and the briefing error that caused it is invisible until the transition.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-29 | sdlc-studio | Filed |
| 2026-09-30 | sprint planning | Groomed: premise re-run at HEAD and wider than filed (the rejecting reviewer's own discharge is refused at the cap, BG0852/D0288); three criteria (discharge in the carrying run, discharge after another reviewer's rounds, only the rejecting reviewer's APPROVE on a carried unit passes); the record-time warning dropped as unneeded; Affects narrowed to critic.py (a bypassed discharge row already clears transition), test_lean_review_cap.py, reference-review.md and the fragment; Points 3 kept. |
