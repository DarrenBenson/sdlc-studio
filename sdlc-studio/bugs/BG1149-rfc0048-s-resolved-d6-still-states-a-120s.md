# BG1149: RFC0048's resolved D6 still states a 120s per-commit gate budget against a 99s baseline, while the config has declared 480s against 400s since 2026-09-20

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/rfcs/RFC0048-make-the-test-suite-cost-effective-without-lowering.md, changelog.d/BG1149.md
> **Evidence:** US1106 round-1 repair report (2026-11-01), L-0175's new Revalidated reason; RFC0048:131; .config.yaml:207-218.
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T03:05:00Z

## Summary

Found while re-judging L-0175 in US1106 (2026-11-01). sdlc-studio/rfcs/RFC0048-make-the-test-suite-cost-effective-without-lowering.md:131 (D6, Resolved) gives the per-commit gate budget as 120 seconds. sdlc-studio/.config.yaml:207-218 re-declared `gate_budget` on 2026-09-20 as 480s against a 400s baseline, with the reasoning written beside it. The resolved decision of record still names the old figure, and nothing compares a resolved RFC decision with the config value it names. L-0175 records exactly this propagation failure.

## Steps to Reproduce

1. Read RFC0048 D6 (line 131): 120s.
2. Read sdlc-studio/.config.yaml:207-218: 480s against a 400s baseline.
3. Expected: the decision of record carries a revision naming the re-declaration, or points at the config.

## Proposed Fix

Give RFC0048 a revision row and point D6 at the config block, so the decision of record names the current figure and where it lives.

## Acceptance Criteria

- [ ] **AC1** RFC0048's D6 names the gate budget the config declares, or points at the config block, and carries a revision row dated with the re-declaration.
  - **Verify:** shell grep -q 'gate_budget' sdlc-studio/rfcs/RFC0048-make-the-test-suite-cost-effective-without-lowering.md

## Impact

A reader of the RFC acts on a budget four times too tight.

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it is what is left of a fix already shipped. RFC0048 is this repository's resolved decision record; the config holds the current figure and nothing user-facing reads the RFC. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
