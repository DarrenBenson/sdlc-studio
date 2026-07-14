# CR-0252: Refresh PRD/TRD/TSD to the v4 feature set (specs are self-declared v2.0.0 against a v4.1.0 product)

> **Status:** Proposed
> **Priority:** P1
> **Type:** Improvement
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Document review 2026-07-14 found all three project spec docs self-declare Version 2.0.0 (PRD, TRD, TSD), last touched 2026-06-20 to 2026-07-06, while the product is v4.1.0. The v4 flagship capabilities are absent under any wording: the engagement floor / mandatory planning pass (PRD=0 TRD=0), ULID collision-free identity (0/0), the generated team / working seats / Cooper personas (0/0), and the RFC0032 learning loop / retro / disposition (0/0). The TSD does not know the mutation gate (0). The PRD still uses the retired 'autosprint' name (renamed to 'sprint' at v4.0). The TRD's ADR log stops at ADR-003, with no ADRs for four architecturally-significant v4 decisions (engagement floor, ULID identity, generated team, learning loop). A repo that preaches spec-code alignment (reconcile, `verify_ac)` has its own PRD two majors behind - a dogfooding-integrity gap.

## Impact

Anyone reading the PRD/TRD/TSD to understand the product learns a pre-v4 skill. The specs cannot be trusted as the source of truth they claim to be, and the dogfooding story ('we keep docs aligned to code') is undercut by the flagship repo's own drift. Fixing it is a prd/trd/tsd generate refresh - substantial, not a freeze-time quick fix.

**Effort:** L

## Acceptance Criteria

- [ ] PRD/TRD/TSD declare v4.x and cover the engagement floor, ULID identity, generated team, and learning loop; PRD uses 'sprint' not 'autosprint'; TRD has ADRs for the four v4 decisions; TSD covers the mutation gate. Verify: rg -qi 'engagement floor|learning loop' sdlc-studio/trd.md && rg -qi '4\.' sdlc-studio/prd.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
