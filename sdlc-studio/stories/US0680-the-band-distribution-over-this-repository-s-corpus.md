# US0680: The band distribution over this repository's corpus is RE-MEASURED after the change and recorded, so the claim that the gate discriminates rests on a number

> **Status:** Draft
> **Delivers:** CR0549
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/scripts/tests/test_route.py, sdlc-studio/change-requests/CR0549-route-estimate-scores-whole-declared-files-so-the.md
> **Epic:** EP0217
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The band distribution over this repository's corpus is RE-MEASURED after the change and recorded, so the claim that the gate discriminates rests on a number
**So that** CR0549 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given the changed estimator, when the band distribution over this repository's whole bug corpus is re-measured, then the measurement is RECORDED in CR0549 beside the pre-change figures - 87% full, 48% with `code` and `risk` both saturated, and a p25-median-p75 of 48-50-54
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::BandDistributionTests::test_the_recorded_distribution_matches_a_fresh_measurement
- [ ] **AC2** Given the re-measured distribution, when the spread is computed, then it is WIDER than the six-point interquartile band the current estimator produces - stated as a number the test asserts, because 'the gate now discriminates' is exactly the kind of claim this project has shipped false before
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::BandDistributionTests::test_the_interquartile_spread_is_wider_than_six_points

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
