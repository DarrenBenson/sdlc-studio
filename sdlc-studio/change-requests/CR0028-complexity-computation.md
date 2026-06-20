# CR-0028: complexity computation (RFC0009 WS1)

> **Status:** Complete
> **Priority:** High
> **Type:** Feature
> **Requester:** Autosprint (RFC0009)
> **RFC:** RFC-0009
> **Date:** 2026-06-20
> **Affects:** scripts/complexity.py (new), scripts/repo_map.py
> **Depends on:** RFC0009 (D1, D2, D4)
> **GitHub Issue:** --

## Summary

Spawned from RFC0009 WS1. A `scripts/complexity.py` that computes **cognitive**
(SonarSource) and **cyclomatic** complexity per function from Python's `ast` (pure
stdlib), with a `lizard` soft dependency for non-Python files (degrading to unscored
when absent). `repo_map.py` emits per-function cognitive/cyclomatic into the map.
The metric is advisory (RFC0009 D3).

## Proposed Changes

### Item 1: stdlib cognitive + cyclomatic scorer + scan CLI

**Priority:** High **Effort:** Medium

`cognitive_complexity` / `cyclomatic_complexity` per function; `analyse_source` /
`analyse_file` (lizard soft-dep for non-`.py`); `scan` CLI with a configurable
`complexity.cognitive_high` threshold (default 15). Nested defs scored separately.

### Item 2: repo_map emit

**Priority:** Medium **Effort:** Low

`parse_python` attaches `cognitive`/`cyclomatic` to each function symbol.

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| scripts/complexity.py | cognitive + cyclomatic scorers, scan CLI | New |
| scripts/repo_map.py | per-function complexity in the map JSON | Modified |

### Breaking Changes

None. New script; repo_map function symbols gain additive keys.

## Acceptance Criteria

- [x] Cognitive complexity matches the SonarSource spec on nesting, elif chains (vs else-nested-if, distinguished by col_offset), boolean alternation, ternary nesting, comprehension filters, match guards, and try/finally.
- [x] Cyclomatic = 1 + decision points; nested defs excluded; consistent with cognitive on comprehension filters.
- [x] Non-Python degrades via lizard, or to unscored ([]) when lizard is absent; never raises.
- [x] repo_map emits per-function cognitive/cyclomatic. Unit-tested; independent critic APPROVE (after fixing 4 cognitive spec deviations).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (RFC0009) | Complete - US0026; critic REJECT->fixed 4 cognitive spec deviations, +5 spec-edge tests |
| 2026-06-20 | Autosprint (RFC0009) | Spawned from RFC0009 WS1 |
