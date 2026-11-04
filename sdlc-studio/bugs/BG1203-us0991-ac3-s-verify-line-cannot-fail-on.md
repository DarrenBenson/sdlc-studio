# BG1203: US0991 AC3's Verify line cannot fail on the close's main-thread prose, which only a sibling test pins

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/stories/US0991-the-close-and-the-report-state-each-reading-s.md, changelog.d/BG1203.md
> **Evidence:** US0991 round-1 verdict, scratchpad run5/US0991-verdict-r1.txt.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T12:39:19Z

## Summary

2026-11-04, US0991's review (qa-seat-US0991-r1, APPROVE, non-blocking). AC3's Verify, `test_sprint_report.py`::HarnessBasisReportTests::`test_cost_section_states_the_readings_basis`, builds the report and never reaches `retro.run_attributed_tokens.` Two mutants restoring main-thread wording there (retro.py:2153, 2157) pass it, and only `test_retro.py`::HarnessBasisTests::`test_the_basis_says_main_thread_only_where_the_reader_does` kills them, so `verify_ac` reads AC3 PASS with the defect in place.

## Steps to Reproduce

1. Apply the retro.py:2157 mutant.
2. `verify_ac.py run --id US0991 --dry-run`: AC3 passes.

## Proposed Fix

Add the retro test as a second Verify line on US0991 AC3.

## Acceptance Criteria

- [ ] **AC1** US0991 AC3 carries a Verify line naming the retro test, and `verify_ac` runs it.
  - **Verify:** shell grep -q 'test_the_basis_says_main_thread_only_where_the_reader_does' sdlc-studio/stories/US0991-the-close-and-the-report-state-each-reading-s.md

## Impact

The transition gate can pass a regression the push suite would catch later.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
