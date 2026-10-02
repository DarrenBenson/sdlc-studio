# BG0895: A finding filed during the run and then added to the batch invalidates the signed page when sign moves it terminal

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_seal_finding_in_batch.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** RUN-01M3VF2J rehearsal: findings_scan signed 13, re-derived 11
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T07:27:57Z

## Summary

BG0876 and BG0877 were filed mid-run and added to RUN-01M3VF2J's batch. The close listed them as open findings raised in the run; sign moved them to Fixed, so the re-derivation dropped them from known issues and RPT0014 read INVALIDATED in the rehearsal. Worked around by moving them terminal before the close, BG0848's old workaround.

## Steps to Reproduce

1. File a bug inside an open run. 2. sprint batch add it, deliver and approve it. 3. sprint close, sprint sign, `sprint_report` check -> INVALIDATED (`findings_scan` and issue rows shift).

## Proposed Fix

Exclude batch units from the open-findings-raised-in-the-run scan (they are on the page as delivered), or settle them at the close as BG0848 did for spans.

## Acceptance Criteria

- [ ] **AC1** Given a run whose batch holds a bug filed during the run, approved and verified but not yet terminal, when the run is closed, signed and checked, then the check reads VALID. Fails on: the current code reads INVALIDATED
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_seal_finding_in_batch.py::SealFindingInBatchTests::test_a_batch_finding_does_not_move_the_signed_page
- [ ] **AC2** Given a bug filed during the run and NOT in the batch, when the run is closed, signed and checked, then it is still listed among the known issues and the check reads VALID. Fails on: a fix that drops every finding raised in the run
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_seal_finding_in_batch.py::SealFindingInBatchTests::test_a_mid_run_finding_outside_the_batch_stays_listed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
| 2026-10-02 | qa seat (goal review) | AC2 added: the control beside AC1, so the goal cannot go green on a fixture |
