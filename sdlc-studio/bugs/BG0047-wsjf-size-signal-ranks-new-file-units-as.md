# BG0047: WSJF size signal ranks new-file units as trivially small, inverting the sprint order

> **Status:** Open
> **Severity:** medium
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio file

## Summary

sprint.py plan --order wsjf sizes each unit as the max cognitive complexity of the EXISTING files its Affects names (_complexity_size). A unit whose Affects points at not-yet-existing files (greenfield work - exactly the biggest jobs) resolves no paths, gets size 0, and wsjf_score's max(size,1) makes it the cheapest possible denominator: in the 2026-07 sprint plan the epic-sized CR0134 (seat-estimated 13 points) ranked joint-first at WSJF 21.0 while the 5-point CR0132 sank to 0.524 behind a size-42 denominator (reconcile.py's complexity, not the job's). Compounding it, wsjf-inputs.json has no size/effort slot, so the Engineering seat that owns effort (reference-sprint.md: 'Engineering for effort, seeded by the complexity signal') has no way to correct the seed - 'seeded' is in practice 'hard-coded'.

## Steps to Reproduce

1. Author a CR whose Affects lists only files that do not exist yet. 2. Score it in .local/wsjf-inputs.json with any values. 3. Run sprint.py plan --crs Proposed --order wsjf. 4. Observe complexity=0 and the unit ranked as if effort were minimal; compare a small CR touching one large existing file, which sinks.

## Proposed Fix

Let wsjf-inputs.json optionally carry a seat-scored size/effort per unit and prefer it over the complexity seed when present; when no Affects path resolves, treat size as unknown (fall back to priority order or a declared default), never as minimal. Pin both behaviours with unit tests on wsjf_score/select_batch.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | audit | Filed |
