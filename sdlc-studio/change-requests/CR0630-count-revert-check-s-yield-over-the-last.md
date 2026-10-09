# CR-0630: Count revert-check's yield over the last several signed runs before doctrine rule 21 is ruled on

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** sdlc-studio/reviews/revert-check-yield.md
> **Evidence:** Raised by the G7 breakdown of CR0624 and CR0616 and its panel review (D0355). A measurement, no code; after BG1009.
> **Date:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T10:05:25Z

## Summary

Doctrine rule 21 (US0935) says no gate enforces 'fails without the fix', on mutation's yield: 1,033 of 1,043 mutants killed. CR0624 would reverse it for the revert. The revert's own yield figures do not support that ruling. One figure is unaudited: 18 would-refuse in 730 examinations, from an instrument that, as BG1009 shows, refuses a revert that changes nothing. Another is relayed rather than counted: a consuming project's '11 of 18 units rejected at least once', for any reason. The third is zero: 0 of 19 refused on RUN-01M40TSJ (panel). Run the shipped `verify_ac.py revert-check` over every unit of the last several signed runs (at least five), in a scratch clone. Use each run record's `base_ref` and `verified_sha` (sdlc-studio/reports/runs/). Record per unit: passed, refused (with the criteria), or not judged (with the cause). Record per run: the seconds spent, and the number of criteria the transition-naming story would print. Where a consuming project shares its run records, count its runs the same way. Do this after BG1009 lands, so empty reverts and timeouts are not counted as findings.

## Impact

Doctrine rule 21 would be ruled on figures that are unaudited, relayed or measured with a defective instrument.

## Acceptance Criteria

- [ ] A committed review page lists each run counted, with its base and verified refs, and per unit the verdict and cause, as the shipped CLI printed them
- [ ] The page states the totals (refused, passed, not judged, per-pass seconds), and a decision row cites them when rule 21 is ruled on

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | Claude Opus 5.5 | Raised |
