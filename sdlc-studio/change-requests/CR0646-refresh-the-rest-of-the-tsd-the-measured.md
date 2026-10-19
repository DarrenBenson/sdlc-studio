# CR-0646: Refresh the rest of the TSD: the measured coverage, per-unit line coverage, the test-tree conventions, NFR rows and the header

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** sdlc-studio/tsd.md
> **Evidence:** RV0028 findings TSD-3, TSD-9, TSD-10, TSD-11, TSD-13, TSD-15, TSD-16, TSD-18, TSD-20, TSD-21, TSD-22, TSD-24; CI run 38886029272 coverage `TOTAL 39514 4200 89%`; tsd.md:182 'roughly 82%'.
> **Date:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T07:48:08Z

## Summary

Outside the gate sections (CR0644), RV0028's TSD leg found the coverage stated as roughly 82% against a CI-measured 89%, no mention of per-unit added-line coverage (`verify_ac --coverage`, `review.line_coverage`, off in this repo), a test tree that names one module convention while 196 of 332 skill modules are per-unit lean modules, PRD NFRs with no TSD row (the four network paths, the appetite breaker, ULID identity), and a header still at the 6.0 baseline with an unlisted status value.

## Impact

The TSD under-reports its own coverage and misdescribes where tests live, so a reader cannot map a PRD NFR to the gate that holds it.

## Acceptance Criteria

- [ ] The TSD states coverage as the CI-measured figure or points at the CI coverage step, and describes per-unit added-line coverage with this repo's setting
- [ ] The test tree names both module conventions (per-script and per-unit lean), the shared helpers, the pytest markers and the hooks, without a module count
- [ ] Every PRD non-functional requirement maps to a TSD row, including the network paths, the appetite breaker and ULID identity
- [ ] The header names the 6.2 baseline, uses one of the document's own status values, and the revision history is in date order

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Raised |
