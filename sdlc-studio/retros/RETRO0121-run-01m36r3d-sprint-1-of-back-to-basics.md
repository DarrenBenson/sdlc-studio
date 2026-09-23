# RETRO-0121: RUN-01M36R3D: Sprint 1 of back to basics, the lean loop

> **Date:** 2026-09-23
> **Batch:** US0868, US0869, US0870, US0871, US0872, US0873, US0874, US0875, US0876, US0877, US0878

## Keep

- Parallel file-disjoint lanes, each unit reviewed once by a fresh reviewer with a two-round cap: 11 units, every REJECT was a real defect, and no unit needed a third round.

## Stop

- Running four suites at once behind per-commit gates built for one: a timing claim deadlocked every fresh worktree, and a gate D0255 had switched off still forced 31 mutant re-registrations.

## Try

- Sprint 2 deletes the gate lanes that cost the most and caught nothing here: the spec-claims timing claim, evidence-drift with the mutation ledger, and module-alone at push (560 of 668 seconds).
- Hand lane agents their shared contracts as code stubs, not prose: the one integration break and the orchestrator's token-sum error both came from prose contracts.
- Open a unit when its lane starts, not at plan time, so per-unit time and tokens measure the work.
