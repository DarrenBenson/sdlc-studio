# CR-0035: deterministic Bug/CR/RFC finding filer (RFC0002 WS3)

> **Status:** Complete
> **Priority:** High
> **Type:** Feature
> **Requester:** Autosprint (RFC0002)
> **RFC:** RFC-0002
> **Date:** 2026-06-20
> **Affects:** scripts/file_finding.py (new), reference-scripts.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

Spawned from RFC0002 WS3. A `scripts/file_finding.py` that files an audit finding as a
Bug/CR/RFC deterministically: allocate a collision-free ID (reusing next_id), render a
**structured** artifact (required sections enforced so it cannot emit a hollow stub -
the 2nd proving run's lesson, RFC0010), write it, append the type-correct index row, and
recompute the index counts (reusing reconcile's tested pass).

## Acceptance Criteria

- [x] `file --type bug|cr|rfc` allocates the next ID without collision and writes a structured artifact (all required sections populated).
- [x] The richness guard refuses a hollow artifact (missing summary / acs / steps+fix / options raises before any file is written).
- [x] The index row is appended to the data table (never inside the summary block) and the counts recomputed; `reconcile detect` then shows 0 drift, including for a title containing a pipe.
- [x] Unit-tested (allocation, structure, pipe-in-title 0-drift, summary-only-index safety); independent critic APPROVE (HIGH latent-corruption path fixed).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (RFC0002) | Complete - file_finding.py; critic APPROVE after fixing the data-table targeting |
