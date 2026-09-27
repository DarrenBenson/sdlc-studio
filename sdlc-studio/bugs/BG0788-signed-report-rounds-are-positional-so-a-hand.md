# BG0788: Signed-report rounds are positional, so a hand-deleted verdict row goes unseen when a same-day later run re-reviewed the unit, and verdict rows carry no run id

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py, changelog.d/BG0788.md
> **Parent:** CR0599
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

- [ ] **AC1** Given a signed fixture report, when a later run on the same UTC day reviews a batch unit and the signed run's own REJECT row for that unit is deleted, then `sprint_report.py check` exits 1 naming that unit's rounds. Fails on: HEAD's positional bound, which slides the later run's row into the slice and reads VALID
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py::SignedReportStableTests::test_a_deleted_row_is_seen_past_a_same_day_later_run
- [ ] **AC2** Given a signed fixture report, when one of the run's own counted rows is superseded after the signature, then `check` exits 0 and the unit's rounds read as signed. Fails on: counting only rows live at check time, so a later correction by addition moves a signed figure (BG0787 QA round 2)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py::SignedReportStableTests::test_a_supersession_after_the_signature_does_not_move_rounds
- [ ] **AC3** Given a close, when PREPARE files the report, then the run record carries each batch unit's counted verdict rows as identities digested from the row's eight parsed cells, and the ledger file is byte-identical before and after. Fails on: adding a Run column (a ninth cell under an eight-column header, and 1,286 rows that could never carry it), or digesting the raw line, which a table re-pad changes
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py::SignedReportStableTests::test_the_close_freezes_row_identities_without_touching_the_ledger
- [ ] **AC4** Given a signed fixture whose run record froze its rows, when a later run that reviewed a batch unit the same day has no record in this clone, then `check` exits 0. Fails on: re-deriving rounds through `_later_review_bases`, which needs every later run's gitignored record
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py::SignedReportStableTests::test_frozen_rounds_need_no_later_run_record

## Notes

- Sprint 6 engineering design: identity = a digest of the row's eight parsed cells (unit, verdict, reviewer, author, date, brief, tier, issues; `-` and empty read the same), so every historic row already has one and none is rewritten. The ledger holds 37 exact duplicate row pairs, so the run's list is a multiset. Frozen in `sprint._file_the_report` just before `build_report`, by the BG0787 rule (which is right at close, when no later run exists); rounds are the count of frozen identities present in the ledger. `_later_review_bases` stays only for a record migrate could not freeze, and is retired once none remains. Land after BG0795 (same freeze point). Ratchet: no check added; retires the positional slice for every frozen record. Measured: RPT0006-RPT0010 all check VALID with only their own run record present, so AC5 of US0941 does not need this unit; it closes the same-day tamper hole.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Filed |
| 2026-09-26 | sdlc | BG0787 QA round 2: superseding an in-window verdict row after signing also moves a signed rounds figure; row identity covers it too. AC1 needs grooming into a testable criterion before build |
| 2026-09-27 | sdlc-studio v6 planning | Groomed for Sprint 6: row identity is a digest of the parsed cells frozen on the run at PREPARE; criteria and Verify selectors written |
