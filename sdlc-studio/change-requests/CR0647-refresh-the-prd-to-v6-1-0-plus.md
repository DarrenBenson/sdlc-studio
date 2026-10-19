# CR-0647: Refresh the PRD to v6.1.0 plus 6.2: release markers, the features shipped since July, the business rules and NFRs that moved, and counts as bands

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/prd.md, tools/tests/test_lean_prd_refresh.py
> **Evidence:** RV0028 findings PRD-1, PRD-3 to PRD-25 (PRD-2's dead key is BG1063); prd.md:202 'all features Complete at v4.1.0'; `retro.py velocity` -> 'MEASURED RATE: 146,283 tokens per point'.
> **Date:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T07:48:08Z

## Summary

RV0028's PRD leg verified 62 of 64 features Complete, 1 Partial (the engagement floor, BG0959) and 1 retired under its own name, but found the 16 [Unreleased] flags all wrong (each shipped by v6.0.0), no row for anything shipped since July (the charter queue, rolling runs, the boundary gates, risk-banded review, the line-coverage gate, changelog fragments and release cut, the constitution, the sprint report and sign), and business rules, NFRs and the cost model that no longer match the code: bugs execute Verify lines too, the groomed definition checks criteria and the split ceiling, the network and read-only claims are understated, and plans price from a measured 146,283 tokens per point rather than the 25,000 seed.

## Impact

The PRD reads as frozen at v4.1 and states requirements the product has moved past, so the Product Owner sign-off cannot be given against it.

## Acceptance Criteria

- [ ] The PRD's baseline reads v6.1.0 plus 6.2 on main and no shipped feature row carries [Unreleased]
- [ ] The feature inventory carries a row for each capability shipped since July 2026 that RV0028 PRD-10 names
- [ ] The business rules, NFRs and cost model match the code: the delivery units that execute Verify lines, the groomed definition, the network paths, the read-only set and the measured tokens-per-point rate
- [ ] Derived counts are stated as bands, per prd.md:85, and per-ship history moves from feature blocks to the changelog table
- [ ] The verified detail criteria are ticked, and the engagement floor reads Partial until BG0959 is Fixed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Raised |
