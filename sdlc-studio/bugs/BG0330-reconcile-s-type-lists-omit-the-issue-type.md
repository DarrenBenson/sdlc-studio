# BG0330: reconcile's type lists omit the issue type, so the issues index is never reconciled by any path

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

reconcile.py hardcodes 8 of the 9 `sdlc_md.ARTIFACT_TYPES`, omitting 'issue', and no --scope names it either, so detect/apply/index-derived can never census sdlc-studio/issues/ - status-mismatch, missing-row, orphan-row and count drift in the issues index are exempt from every automated check even though artifact.py, triage.py, status.py and the shipped index template fully support the type. archive.py derives its type list from `ARTIFACT_TYPES`, the convention reconcile violates.

## Steps to Reproduce

Evidence (`SCOPE_TYPES` (lines 35-46) and `DEFAULT_TYPES` (line 47); inherited by `cmd_detect`, `cmd_apply`, `index_derived_issues`, and gate.py:_reconcile): reconcile.py:47 and :44 omit issue; `sdlc_md.py`:825-835 has nine types including issue; only transition.py:800's `apply_type` call syncs an issue row, and only at transition time; gate.py:49 sums over the same incomplete `DEFAULT_TYPES.`

## Proposed Fix

Derive `DEFAULT_TYPES` and the `SCOPE_TYPES` indexes list from `sdlc_md.ARTIFACT_TYPES` (as archive.py does) so issue - and any future type - is censused by detect, apply, and the gate lane.

## Acceptance Criteria

### AC1: the default sweep is derived, so no artefact type can be omitted from it

- **Given** `sdlc_md.ARTIFACT_TYPES`, the single source of truth for the nine types
- **When** `reconcile.DEFAULT_TYPES` is read
- **Then** it holds every one of them, because it is derived rather than hand-listed - re-hardcoding
  the list, or adding a tenth type, reddens this guard instead of quietly exempting an index
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::EveryArtifactTypeIsCensusedTests::test_default_sweep_covers_every_artifact_type

### AC2: every type is reachable by a `--scope`

- **Given** the `SCOPE_TYPES` map that `--scope` derives its choices from
- **When** the union of its values is compared with `ARTIFACT_TYPES`
- **Then** every type is covered and `--scope indexes` is the full set, so a type can never be
  addressable by the machinery yet unaddressable from the command line
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::EveryArtifactTypeIsCensusedTests::test_every_artifact_type_is_reachable_by_a_scope

### AC3: a drifted issues index is reported by a default `detect`

- **Given** `sdlc-studio/issues/` holding IS0001 at Triaging and an index row saying Open
- **When** `reconcile detect` runs with no `--scope`
- **Then** it exits 1 naming IS0001 - the index that was censused by no path is now censused by the
  default one, which is the path the commit gate and `sprint` take
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::EveryArtifactTypeIsCensusedTests::test_default_detect_reports_issue_index_drift

### AC4: a default `apply` repairs it, and the index-derived check sees it

- **Given** that same drifted issues index
- **When** `reconcile apply` runs with no `--scope`
- **Then** the row is rewritten to Triaging and a following `detect` is clean, and
  `index_derived_issues` reports the index under the `issue:` key
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::EveryArtifactTypeIsCensusedTests::test_default_apply_reconciles_the_issue_index

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-28 | delivery lane (RUN-01KYJZGZ) | Acceptance criteria authored; type lists derived from `ARTIFACT_TYPES`, `issues` scope added |
