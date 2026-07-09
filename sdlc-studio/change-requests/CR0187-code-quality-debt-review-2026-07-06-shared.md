# CR-0187: Code-quality debt (review 2026-07-06): shared-layer bypasses, duplication, complexity, diagnostics

> **Status:** Complete
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic (v4 breakdown):** [EP0018](../epics/EP0018-tooling-hardening-and-review-debt.md)
> **Priority:** Low
> **Type:** Improvement
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** M

## Summary

Themed consolidation of the Low-severity maintainability findings from review RV0006. None
changes behaviour today; together they are the debt that lets the Medium-severity defects
recur.

## Motivation

The review found the codebase disciplined (uniform exit-code convention, annotated broad
excepts confined to advisory lanes, self-diagnosing findings). These Low items are the
loose threads: stale docstrings, duplicated primitives that can drift, uneven JSON support,
and silent advisory lanes with no debug channel.

## Proposed Changes (each with evidence)

1. **Fix stale/incorrect docstrings.** `reconcile.py:2-14` still calls itself "read-only ...
   Subcommand: detect" while shipping `apply`/`fields`/`archive` write subcommands (a
   read-only allowlist trusting it under-scopes the mutation surface, cf.
   `tests/test_confinement.py`).
2. **De-duplicate shared primitives into `lib/sdlc_md.py`.** `audit.find_artifact`
   (audit.py:43-51) duplicates `transition._find` (transition.py:127-135) - already drifted in
   return shape; `verify_ac` repeats its epic-membership scan (verify_ac.py:719-724, 766-770).
   Move `find_by_id` and `linked_to_epic` into the shared layer and delegate.
3. **Even out `--format json`.** `reconcile apply` (reconcile.py:1242-1246),
   `artifact revision` (artifact.py:474-480), and `file_finding rebuild` (file_finding.py:226-229)
   emit prose only, where every sibling verb offers JSON; the result dicts already exist.
4. **Tame complexity hotspots.** `reconcile.detect_type` (113 lines),
   `conformance.detect_conformance` (106 lines, depth 6), `transition.transition` (85 lines,
   four interleaved gates), `lessons.render_global_lesson` (depth 7). Extract named helpers.
5. **Fix latent test-suite issues.** Invalid escape `["x \| y", ...]` at
   `tests/test_table_parsers.py:85` (future SyntaxError - use a raw string); capture stdout in
   the verify tests that leak `[APL]`/`wrote ...` lines into suite output.
6. **Small cleanups.** Redundant `except (OSError, Exception)` at gate.py:135;
   `meta_new` dry-run reports `indexed: False` unconditionally (artifact.py:227-229) where the
   real path and `new()`'s dry-run predict honestly; hardcoded `.claude/...` skill path in the
   tool-neutral sprint planner (sprint.py:64-69) - resolve against `Path(__file__).parent.parent`.
7. **Bound append-only `.local` logs and add an opt-in debug channel.** `telemetry.jsonl` and
   `verify-history.jsonl` grow without cap; advisory lanes swallow errors with no trace. Add a
   size/age roll (or `telemetry compact`) and an `SDLC_DEBUG=1` -> one-stderr-line channel for
   the swallowed advisory exceptions.

## Acceptance Criteria

- [ ] `reconcile.py` docstring lists all four subcommands and scopes read-only to `detect`.
- [ ] `find_by_id`/`linked_to_epic` live in `lib/sdlc_md.py`; the duplicate copies delegate.
- [ ] `apply`, `revision`, `rebuild` accept `--format json` printing their existing result
      structures.
- [ ] The four named hotspots are decomposed into helpers with no behaviour change (tests
      unchanged and green).
- [ ] `test_table_parsers.py:85` uses a raw string; the verify tests no longer leak stdout.
- [ ] The six small cleanups are applied; `.local` logs roll; `SDLC_DEBUG=1` emits one line
      from each named swallowed-advisory site.

## Dependencies

| Artefact | Relationship |
| --- | --- |
| CR0181 | The larger github_sync/verify_ac shared-layer bypass is pulled out there; item 2 here is the smaller find/epic-scan duplication |
| CR0182 | The archive duplication is pulled out there; not repeated in item 2 |

## Risk

Low. Refactor-and-cleanup; the complexity extractions must be behaviour-preserving - rely on
the existing green suite plus CR0185's new invariants.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Consolidated the Low code-quality/observability findings from RV0006 |
