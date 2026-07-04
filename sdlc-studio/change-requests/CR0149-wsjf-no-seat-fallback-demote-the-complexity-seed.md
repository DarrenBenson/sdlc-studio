# CR-0149: WSJF no-seat fallback - demote the complexity seed from size stand-in to tiebreak

> **Status:** Approved
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-07-04
> **Created-by:** sdlc-studio file

## Summary

> **Re-scoped (2026-07-04) after the operator's adversarial review.** First filed claiming "the
> WSJF denominator is still complexity"; the review checked sprint.py and refuted it - with a
> seat size present the denominator IS the seat size already (the BG0047 fix), and the
> original headline AC was implemented before this CR was written.

The remaining, narrower delta is the **no-seat fallback**: when the Engineering seat has not
scored a unit, the complexity seed still stands in as the WSJF size (`size = seed` when
`seed > 0`). Blast-radius complexity measures the cognitive complexity of the EXISTING files a
unit touches - a risk signal, not effort: a one-line fix in reconcile.py reads as a 42-point
job. In the fallback, dividing by it distorts exactly the units nobody scored.

## Design (settled at the sprint design rung)

- In `_order_batch`, the no-seat-size branch divides by `DEFAULT_UNKNOWN_SIZE`
  (never the seed); the seed stays in `it["complexity"]` (tiebreak via `_rank_key`)
  and the token budget. One pinning test: a small CR touching a high-complexity
  file, seat numerators but no seat size, must not sink below a same-priority
  unit touching a simple file.

## Acceptance Criteria

- [ ] in the no-seat-size fallback, the WSJF denominator is the declared neutral default (not
      the complexity seed); the seed remains the within-priority tiebreak (smaller blast
      radius first) and the token-budget input
- [ ] reference-sprint.md documents the complexity signal as blast-radius RISK (tiebreak +
      budget), never job size
- [ ] a unit test pins the small-fix-in-complex-file fallback case no longer sinking on the
      file's complexity; `CHANGELOG.md` [Unreleased]

## Out of Scope

- The seat-size denominator (already implemented - BG0047).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | audit | Raised |
| 2026-07-04 | claude | Re-scoped per the operator's adversarial review: headline AC was already implemented; scope narrowed to the no-seat fallback; Medium -> Low |
| 2026-07-04 | claude | Design settled: fallback divides by the neutral default; seed remains tiebreak + budget input |
