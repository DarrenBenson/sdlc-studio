# BG0763: Two file_finding tests write stub packs into the shipped audit-profiles folder, so parallel runs race

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`test_file_finding.py`'s AuditAttributionUnheldInvariantsTests write zz-review-stub.md and zz-review-dupe.md into the real templates/audit-profiles/ directory. Under pytest-xdist a sibling test's duplicate pack makes `LIVE_LENS` ambiguous, so `test_a_stub_pack_elsewhere_does_not_break_an_unrelated_filing` fails at random. It refused BG0762's commit on 2026-09-25 and passes alone every time.

## Steps to Reproduce

Run the commit hook's selected suites under load with `test_file_finding.py` selected; about one run in several fails `test_a_stub_pack_elsewhere_does_not_break_an_unrelated_filing` on an ambiguous lens. Alone it passes.

## Proposed Fix

Point `file_finding`'s pack lookup at a per-test temporary copy of the packs folder (a parameter or environment override the tests set), so no test writes into the shipped templates; delete nothing the tests prove.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `test_file_finding.py`'s AuditAttributionUnheldInvariantsTests write zz-review-stub.md and zz-review-dupe.md into the real templates/audit-profiles/ directory.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run the commit hook's selected suites under load with `test_file_finding.py` selected; about one run in several fails...
- [ ] **AC3** The proposed fix lands, pinned by a test: Point `file_finding`'s pack lookup at a per-test temporary copy of the packs folder (a parameter or environment override the tests set), so no test writes into...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
