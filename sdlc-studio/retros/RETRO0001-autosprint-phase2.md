<!--
Sprint retro for the CR0020 autosprint (RFC0001 Phase 2). Written at the close;
read at the start of the next sprint. Promote durable lessons with lessons add --global.
Related: reference-autosprint.md, RFC0001, CR0018
-->
# RETRO-0001: Autosprint Phase 2 - guardrails, ledger, autonomous wiring

> **Date:** 2026-06-20
> **Batch:** CR0020 (RFC0001 Phase 2)
> **Goal:** done
> **Delivered:** 3 / 3   **Blocked:** 0

## Delivered

- **US0009** - `ledger.py`: committed append-only per-tranche decisions ledger
  (`sdlc-studio/decisions/<tranche>.md`); survives compaction. Dogfooded - CR0020's
  own rulings recorded by the script as it was built.
- **US0010** - `loop_guard.py`: deterministic iteration cap, repetition-breaker and
  completion oracle; quarantine = Blocked-and-continue, exit 3.
- **US0011** - `--autonomous` mode documented across reference-autosprint.md,
  reference-project.md, help/autosprint.md, tying ledger + guardrails + critic +
  closing gate.

## Blocked / deferred

- None. Every unit reached Done green.

## What went well

- **The loop self-hosted.** autosprint's own conformance gate (11/11) and batch
  selector drove the delivery of autosprint's remaining guardrails - the bootstrap
  closed.
- **TDD caught a real bug:** the cross-invocation accumulation test failed first
  because two identical signatures trip the repetition-breaker (correct behaviour);
  the test was wrong, not the code. RED-first earned its keep.
- **The independent critic earned its keep too:** both scripts were APPROVED but
  each critic found a mutation-survivable gap (untested `_clean` pipe-handling; the
  cap-1 boundary + cross-process accumulation), all closed before commit.

## What was hard / what stalled

- Index status lag: stories committed Done while the index still read Ready - caught
  by `reconcile detect` at the closing gate, not before. The closing reconcile is
  load-bearing, not ceremony.
- `next_id allocate --type` (not positional) and the `--root` containing-dir
  convention still trip first use; worth a one-line reminder in the loop prompt.

## Lessons

- A doc-only unit's "critic" is the mandatory closing review, not a mutation pass -
  don't spend a sub-agent where `rg`-verified AC + review suffice.
- Append-only is only safe if the sanitiser that prevents row-splitting is itself
  tested - an untested `_clean` is a silent data-loss path. <!-- promotable -->
- Drive status flips by reading the file into a variable before writing (the US0006
  truncation footgun); the per-story Python edits held to it.

## Metrics

- Tokens: not separately metered (one continuous session) · Critic rejects: 0 hard
  (2 critic-driven test additions) · Commits: 5 green (decompose + 3 units + close)
