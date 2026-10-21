# BG1021: A CR declared Size L is not flagged for decomposition

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_breakdown_size_l_decompose.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, changelog.d/BG1021.md
> **Evidence:** Field report, 2026-10-09, planning Sprint 1 in a consuming project. sprint.py breakdown --crs Proposed reported 10 units, 0 ungroomed, and one decompose candidate: CR-01M46BZJ because it touches 5 files. CR-01M46BKF and CR-01M46B9P are Size L, with fewer than 5 declared paths and no Points, and neither was listed. The plan of those requests then said the batch was within the unit budget and priced no tokens. After they were refined into stories of 8, 5 and 8 points, the same run re-planned at the done rung said the token forecast was over budget (about 525000 against 500000).
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Grok 4.7; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T16:38:18Z

## Summary

reference-sprint.md says the plan flags a CR that is declared Large, or that touches five or more files. The size the grooming gate actually demands of a CR is a T-shirt Size, and Size L is the top of that scale. The decompose list only looks at Points at or above the split ceiling, or at five declared files. A T-shirt size is never read as a number, so Size L matches neither test. The CR is certified groomed, the plan opens, and the first time the work has a point total is after refine, when the token budget can already have been exceeded. The existing test pins the Points-at-8 path, which a CR filed under the current size rule does not use.

## Steps to Reproduce

1. Write a Proposed CR with Size L, Affects naming one file that exists, no Points, and no story that cites it. 2. Run sprint.py breakdown --crs Proposed. 3. The CR is groomed and is absent from the decompose list. 4. A CR with Points 8 and the same shape is listed.

## Proposed Fix

Treat Size L and Size XL as the decompose signal the reference already names, alongside the points ceiling and the five-file threshold. Keep Size S and Size M off that list. Do not invent a point total from the T-shirt.

## Acceptance Criteria

- [ ] **AC1** A Proposed CR declared Size L or XL, with one resolvable Affects path, no Points and no citing story, is listed by `sprint.py breakdown` for decomposition, while Size S and M are not
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_breakdown_size_l_decompose.py::SizeLDecomposeTests::test_a_size_l_cr_is_flagged_for_decomposition

## Triage

- Confirmed at 0c7e4d90 by the code path: the breakdown flags a CR for decomposition only when `points >= ceiling` or it declares `DECOMPOSE_FILE_THRESHOLD` (five) or more files (sprint.py ~2157-2161); a T-shirt Size is never read, though reference-sprint.md:374 promises the plan flags a CR "declared Large". Pre-existing.
- Severity Medium stands: a Size L request passes as groomed and its token budget is first priced after refine. Fragment renamed to the unit id.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | Grok 4.7 | Filed |
| 2026-10-12 | Claude Opus 5.5 (triage) | Triaged: confirmed on current code; changelog fragment named for the unit; Verify on a new test module (BG0980) |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
