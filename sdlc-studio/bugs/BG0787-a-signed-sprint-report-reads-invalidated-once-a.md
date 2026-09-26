# BG0787: A signed sprint report reads INVALIDATED once a later run reviews one of its units, because unit rounds are re-derived from the whole live verdict ledger

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py, changelog.d/BG0787.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_report.py
> **Created:** 2026-09-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-26T14:48:24Z

## Summary

RPT0009 (RUN-01M3BK9Y, signed 2026-09-25) now fails `sprint_report.py` check: '`unit_rounds[28]`: signed 0, now 2'. The report's per-unit review rounds are re-read from the live verdict ledger without the run's window, so a unit the run cut or carried (US0914, cut under D0269) and a later run reviewed moves the signed figure. It recurs for every signed report whose units are reviewed after its close. BG0751 windowed the findings figures to the run; the rounds figure was left unwindowed. Found by US0940's QA review; RPT0006-RPT0008 still read VALID.

## Steps to Reproduce

1. python3 .claude/skills/sdlc-studio/scripts/`sprint_report.py` check --report RPT0009: exit 1, INVALIDATED, `unit_rounds[28]` signed 0 now 2. 2. The unit at index 28 was reviewed in RUN-01M3CK1K.

## Proposed Fix

Window `unit_rounds` to verdict rows recorded within the signed run (as BG0751 windows findings), so a later run's reviews cannot move a signed figure; RPT0006-RPT0009 check VALID afterwards; a test signs a report, records a later-run verdict on a batch unit, and asserts VALID.

## Acceptance Criteria

- [ ] **AC1** Given a signed sprint report whose batch holds a unit that a later run reviews (a verdict row recorded after the signature), when `sprint_report.py check` runs on it, then it reads VALID and `unit_rounds` for that unit reads as signed. Fails on: re-deriving unit rounds from every verdict row in the live ledger, with no run window
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py::SignedReportStableTests::test_a_later_run_reviewing_a_batch_unit_does_not_invalidate
- [ ] **AC2** Given the same report, when a verdict row inside the run's own window is edited by hand for a unit no later run re-reviewed on the same UTC day (that case is BG0788, D0277), then `check` still reads INVALID naming the unit's rounds. Fails on: a window so wide or a rounds figure so frozen that the check stops reading the run's own rows
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_signed_report_stable.py::SignedReportStableTests::test_a_hand_edited_in_window_round_is_still_invalid
- [ ] **AC3** Given this repository, when `sprint_report.py check` runs on RPT0006, RPT0007, RPT0008 and RPT0009 with the signing clone's run record present, then each exits 0. Fails on: a fix that only helps reports signed after it lands
  - **Verify:** shell sh -c 'for r in RPT0006 RPT0007 RPT0008 RPT0009; do python3 .claude/skills/sdlc-studio/scripts/sprint_report.py check --report $r >/dev/null || exit 1; done'

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Filed |
| 2026-09-26 | sdlc | Groomed for Sprint 5: criteria and Verify selectors written; High, blocks rc.1 under the zero-open-High bar |
| 2026-09-26 | sdlc | AC2 scoped under D0277: the same-day later re-review case is BG0788 (row identity, with CR0599) |
