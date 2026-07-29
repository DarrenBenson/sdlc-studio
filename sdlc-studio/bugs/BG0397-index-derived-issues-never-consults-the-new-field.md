# BG0397: index_derived_issues never consults the new field drift, so the gate lane asserting the index is derived is green over it

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
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

### AC1: a stale index cell fails the index-derived lane

- **Given** a bug whose file says Severity High and whose index row says Low
- **When** `index_derived_issues` runs
- **Then** it reports the type as not derived-consistent, and names WHICH way it is underived
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::IndexDerivedSeesFieldDriftTests::test_a_stale_index_cell_fails_the_index_derived_lane
- **Verified:** yes (2026-07-29)

### AC2: a derived index still passes

- **Given** an index whose cells match their files
- **When** the lane runs
- **Then** it reports nothing, so the lane discriminates rather than always failing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::IndexDerivedSeesFieldDriftTests::test_a_derived_index_still_passes
- **Verified:** yes (2026-07-29)

### AC3: the lane's inputs are derived, not a second list

- **Given** `apply_type`'s own write condition, which defines what "not a fixed point of apply" means
- **When** a key is added to that condition
- **Then** a guard reading the condition from source fails unless `ROW_MUTATING_KEYS` covers it, so the omission that produced this bug cannot recur silently
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::IndexDerivedSeesFieldDriftTests::test_the_lane_checks_every_key_that_makes_apply_write
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
