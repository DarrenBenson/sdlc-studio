# BG0397: index_derived_issues never consults the new field drift, so the gate lane asserting the index is derived is green over it

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Evidence:** adversarial review of RUN-01KYMJEM, reproduced by the reviewer
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

`apply_type` now returns `result['fields']` and `detect_all` emits `index-field` drift, but `index_derived_issues` still tests only changes/appended/`counts_updated`/stamped. It is the sole backing of gate.py's `index-derived` lane and `schema_check`'s rule, so the commit gate keeps asserting the index is derived over an index that is not.

## Steps to Reproduce

Change a bug's Severity in a copy; detect reports index-field drift; `index_derived_issues` returns [].

## Proposed Fix

Add a branch on res.get('fields').

## Acceptance Criteria

- [ ] A stale index cell makes the index-derived gate lane fail.
- [ ] The lane's inputs are derived from detect's own drift kinds rather than a second list.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
