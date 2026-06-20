# CR-0029: code plan complexity estimation + refactor-first (RFC0009 WS2)

> **Status:** Complete
> **Priority:** High
> **Type:** Feature
> **Requester:** Autosprint (RFC0009)
> **RFC:** RFC-0009
> **Date:** 2026-06-20
> **Affects:** scripts/complexity.py (assess), reference-code.md
> **Depends on:** CR0028 (WS1), RFC0009 (D3, D6)
> **GitHub Issue:** --

## Summary

Spawned from RFC0009 WS2. `complexity.py assess` scores a change's blast radius (the
files a story will touch, from the repo-map neighbourhood - D4) into a difficulty band
and a **refactor-first recommendation** per hotspot. `code plan` folds both into the
estimate. Advisory, never a gate (D3); the refactor is scoped to the change (D6).

## Proposed Changes

### Item 1: `assess` (blast-radius difficulty + refactor-first)

**Priority:** High **Effort:** Low

`assess(repo_root, files, threshold)` returns `difficulty` (low/medium/high by max
cognitive vs threshold), `hotspots`, and a `refactor_first` line per hotspot. `assess`
CLI subcommand; always exits 0 (advisory).

### Item 2: `code plan` workflow guidance

**Priority:** High **Effort:** Low

`reference-code.md` step 6b: after repo-map ranking, run `assess`; weight the estimate
by the difficulty band; add a scoped refactor-first plan step per hotspot.

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| scripts/complexity.py | `assess` + `assess` CLI | New |
| reference-code.md | code-plan step 6b (assess + refactor-first) | Modified |

### Breaking Changes

None.

## Acceptance Criteria

- [x] `assess` returns a difficulty band and a refactor-first line per hotspot; a high-complexity touched file yields `high` + a recommendation; a simple change yields `low` and none.
- [x] Missing files are skipped; lizard-unscored functions do not crash; the CLI always exits 0 (advisory, D3).
- [x] `reference-code.md` documents the assess + refactor-first step in the code-plan workflow (scoped to the change, D6).
- [x] Unit-tested; independent critic APPROVE.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (RFC0009) | Complete - US0027; assess + reference-code.md step 6b; critic APPROVE |
| 2026-06-20 | Autosprint (RFC0009) | Spawned from RFC0009 WS2 |
