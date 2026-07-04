# RETRO-0008: Sprint 2026-07-C - the re-scoped seven, delivered through their own new machinery

> **Date:** 2026-07-04
> **Batch:** CR0143, CR0144, CR0145, CR0146, CR0147, CR0148, CR0149 (operator-re-scoped dogfood write-ups)
> **Goal:** done
> **Delivered:** 7 / 7   **Blocked:** 0

## Delivered

- **CR0147** - the freshness finding names its static counting method (claim and checker agree).
- **CR0148** - the adversarial full-diff critic pass is a named, exact close step (this very
  retro ran under it).
- **CR0145** - Verify runners missing from PATH draw an advisory that owns the author-vs-CI
  ambiguity; live-verified on this machine's absent pytest.
- **CR0146** - mutation gate v2: content-hash staleness (leads), round-robin budget with files
  as the fast axis, tokenizer docstring exclusion with a noted degrade.
- **CR0144** - `sdlc_md.iter_tables()` + four parsers ported one at a time, existing tests
  unmodified and green between ports; the BG0046/BG0049 defect class retired structurally.
- **CR0149** - the WSJF no-seat fallback divides by the neutral default; the complexity seed is
  blast-radius risk (tiebreak + budget), never size.
- **CR0143** - `transition --ids` batches with per-id gating; retro/review are tool-created
  meta-artifacts - **this retro was created by that code at this sprint's own close**.

## Critic loop, observed

Approve across all seven on the first pass, with five low findings - four fixed in the close
(json stdout kept pure in batch mode, meta-index insertion bounded to the data table, gate
hash paths resolved against --root, a contradictory comment corrected), each seen RED first.
The fifth (a header-less-block scavenge heuristic drift in the iterator port, no real-file
trigger, differential-probed old-vs-new) is logged here as accepted drift. The critic's
differential probing of CR0144 - old parsers vs new over adversarial fixtures - confirmed the
two other behaviour changes are the documented intent (dup scoping, matrix-only ts_check).

## What went well

- The operator's adversarial review of the CR batch (pre-sprint) meant every unit's scope was
  already load-tested; zero mid-flight re-scoping.
- Seat-sized WSJF planned the order with no hand-merge (BG0047's slot, second production use).
- The close dogfooded its own deliverables: this retro via CR0143's meta path, the critic pass
  under CR0148's newly named discipline, staleness checked by CR0146's own hash lane.

## What was hard / near-miss

- A regression test passed VACUOUSLY by anchoring on a display id that legitimately recurred
  (lesson L-0003: anchor on slugs/paths, never display ids). Caught only because the critic's
  repro was re-run by hand after the test went green suspiciously fast.
- Noted for the backlog: next_id can re-allocate a meta id whose file is gone but whose index
  row remains (surfaced by the same near-miss fixture).

## Actions

- [ ] Operator: CR0150 (concurrent-session advisory) and CR0151 (seat-score provenance) remain
      Proposed for review - the only open backlog items.
- [ ] Watch: iterator scavenge heuristic (accepted drift), meta-id re-allocation edge.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | claude | Sprint close retro (created via `artifact new --type retro` - CR0143 dogfood) |
