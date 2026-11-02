# BG1184: BG1176's re-pointed criteria leave three sub-claims unpinned, and two manual Verify lines still send a reviewer to a folded fragment

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/stories/US0201-prd-sections-3-10-11-to-the-shipped.md, sdlc-studio/stories/US0206-tsd-record-the-blocking-80-coverage-gate-and.md, sdlc-studio/bugs/BG1176-eight-done-criteria-went-stale-in-the-6.md, sdlc-studio/bugs/BG1053-us1004-did-not-converge-in-review-round-3.md, sdlc-studio/bugs/BG1056-bg1053-did-not-converge-in-review-round-2.md
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-02T21:07:27Z

## Summary

Found by BG1176's review and US1101's round-2 review (2026-11-02). (1) US0201 AC2's Then cites BG0133 and BG0136 in the PRD's US1104 Changelog row (prd.md:745), but its grep reads only the section 10 sentence (mutant S1 survives). (2) US0206 AC1's Then says both coverage sections call the floor the hard gate (tsd.md:174, :501), but its grep reads neither (S3 survives). (3) BG1176 AC2 refuses only the old v6.1.0 literal, not a fresh literal (E2 survives), and never reads BG0945 AC1 (F1 survives). (4) BG1053 AC5 and BG1056 AC7 are manual Verify lines pointing at changelog.d/US1004.md, which the 6.2.0 cut folded.

## Steps to Reproduce

Apply mutants S1, S3, E2 and F1 (scratchpad `qa_bg1176_mutants.py)` and run each criterion's Verify: green.

## Proposed Fix

Add a grep for each unpinned sub-claim, make BG1176 AC2 refuse any version literal in those criteria, and re-point the two manual lines at the released CHANGELOG section.

## Acceptance Criteria

- [ ] **AC1** Mutants S1, S3, E2 and F1 each turn their criterion's Verify red, and no manual Verify line names a folded fragment.
  - **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/verify_ac.py run --ids US0201,US0206,BG1176 --dry-run

## Impact

Each criterion can lose part of its claim with its Verify still green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | claude | Filed |
