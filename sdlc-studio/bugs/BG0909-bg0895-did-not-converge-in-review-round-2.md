# BG0909: BG0895 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_seal_finding_in_batch.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T14:31:55Z

## Summary

BG0895 was rejected at round 2, the review cap, by qa-seat reviewer (subagent a1d97d0c), so it was carried as a known issue rather than reviewed again. The findings still open: [new] on a re-close the checklist reads the previous attempt's frozen gate: report\_gate\_clear has one writer (PREPARE, sprint.py:9075) and nothing clears it when a new attempt starts, so delivered\_batch (sprint\_report.py:2159) judges attempt 2's checklist with attempt 1's verdict while the page derives from attempt 2's fresh freeze - executed both directions through two real closes: red then green gives a page with 1 open finding beside a 2 unruled gap, green then red gives a page listing BG0101 open beside a 1 unruled gap - round 1's first finding is MOVED to the re-close path; [new] the frozen branch of delivered\_batch (:2159-2160) is unpinned: deleting it survives all 5 tests

## Steps to Reproduce

1. Read the round 2 REJECT of BG0895 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG0895 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: [new] on a re-close the checklist reads the previous attempt's frozen gate: report\_gate\_clear has one writer (PREPARE, sprint.py:9075) and nothing clears it when a new attempt starts, so delivered\_batch (sprint\_report.py:2159) judges attempt 2's checklist with attempt 1's verdict while the page derives from attempt 2's fresh freeze - executed both directions through two real closes: red then green gives a page with 1 open finding beside a 2 unruled gap, green then red gives a page listing BG0101 open beside a 1 unruled gap - round 1's first finding is MOVED to the re-close path
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [new] the frozen branch of delivered\_batch (:2159-2160) is unpinned: deleting it survives all 5 tests
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** BG0895 AC1 still passes: Given a run whose batch holds a bug filed during the run, approved and verified but not yet terminal, when the run is closed, signed and checked, then the check reads VALID. Fails on: the current code reads INVALIDATED
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_seal_finding_in_batch.py::SealFindingInBatchTests::test_a_batch_finding_does_not_move_the_signed_page
- [ ] **AC4** BG0895 AC2 still passes: Given a bug filed during the run and NOT in the batch, when the run is closed, signed and checked, then it is still listed among the known issues and the check reads VALID. Fails on: a fix that drops every finding raised in the run
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_seal_finding_in_batch.py::SealFindingInBatchTests::test_a_mid_run_finding_outside_the_batch_stays_listed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
