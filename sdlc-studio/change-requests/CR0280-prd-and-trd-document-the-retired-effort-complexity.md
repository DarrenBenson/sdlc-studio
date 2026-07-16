# CR-0280: PRD and TRD document the retired Effort/complexity estimator as current, keep its answered questions open, and gate recalibration on two already-fixed defects

> **Status:** Proposed
> **Priority:** High
> **Type:** docs
> **Size:** M
> **Affects:** sdlc-studio/prd.md, sdlc-studio/trd.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

Both spec documents present the falsified pre-RFC0038 cost model as live. prd.md:211 says Effort (S/M/L) feeds WSJF and the token forecast and that 'the constants have deliberately not been re-fitted'; prd.md:535-541 declares two loop defects 'open and must land before any recalibration decision' (accuracy re-derives estimates from live constants; the filer cannot record Affects:) - both are BG0133/BG0136, Fixed 2026-07-14; prd.md Section 11 keeps 'is there a plan-time predictor at all?' open. trd.md §10 presents the complexity-based predictor as the live design, §12 Q4 calls the loop 'unfalsifiable' for lack of recorded forecasts, and §13's Won't-Have forbids the rate recomputation the shipped estimator now performs. Committed main (RFC0038 finale, 8fdddc6) ships Fibonacci Points x a measured tokens-per-point rate (r=+0.68), records plan-time forecasts stamped with estimator constants, and retired Effort. Anyone rebuilding from these self-described migration blueprints would rebuild the falsified estimator. Verified 3x + 3x + 3x by refute panels; no existing CR covers the refresh (CR0252 predates the finale).

## Impact

Both spec documents present the falsified pre-RFC0038 cost model as live.

## Acceptance Criteria

- [ ] prd.md Section 3's sizing row describes the shipped model: Fibonacci Points on stories/bugs, T-shirt Size on CR/RFC/epic, forecast = sum(Points) x the measured tokens-per-point rate; Effort S/M/L named only as retired
- [ ] prd.md Section 10 no longer claims the two loop defects are open; it cites BG0133/BG0136 as fixed with the shipped behaviour (accuracy reads only the recorded forecast; `file_finding` accepts --affects)
- [ ] prd.md Section 11's plan-time-predictor open question is closed citing RFC0038's points model (r=+0.68)
- [ ] trd.md §10 describes the points x measured-rate forecast with plan-time forecasts recorded to telemetry.forecasts stamped with estimator constants; §12 Q4 closed; §13's auto-recalibration Won't-Have restated to match the shipped per-plan rate recomputation

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
