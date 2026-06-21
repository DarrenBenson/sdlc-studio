# CR-0061: Stakes-scaled autosprint review depth token trim

> **Status:** Complete
> **Created:** 2026-06-21
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement

## Summary

From the RV0004 token review: the autosprint loop spawned a full adversarial critic sub-agent per
unit regardless of stakes (a trivial doc change cost the same as a parser). Scale review depth to
stakes - full adversarial critic for code/risky units, a lighter recorded review for pure-doc/
mechanical units - keeping the recorded-verdict honesty (the `critiqued` gate still requires a
committed APPROVE; only the depth scales). Policy/doc change, no new machinery.

## Acceptance Criteria

- [x] `reference-autosprint.md` defines stakes-scaled review depth: full independent adversarial
  critic for code/logic/parser/security/data-loss units; a lighter recorded review for pure-doc/
  template/mechanical units; "when unsure, use the full critic"
- [x] the verdict tier is recorded in `critic.py record` (reviewer/issues), so the `critiqued`
  conformance gate still requires a committed APPROVE - no honesty regression, no conformance.py change
- [x] no new "risk engine" script (kept a judgement policy); lint green

## Implementation

Reworded the Independent-critic step in `reference-autosprint.md` to tier the review by risk band,
recorded via the existing critic.py. No code change (the conformance `critiqued` gate is unchanged -
it still requires a recorded APPROVE).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (RFC0016) | Created via `new` (deterministic) |
