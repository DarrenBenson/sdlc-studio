# BG0331: gate.py's reconcile lane enumerates two drift sources and exempts the five sweep-level detectors, re-creating the bug it

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_804ef18d

## Summary

The blocking reconcile lane counts only `detect_type` drift plus `derivable_request_drift`; its own comment records that sweep-assembled kinds were invisible here and then fixes only one - `meta_index_drift`, `epic_breakdown_drift` (including ticked-early, 'the direction that masks unfinished work'), `epic_points_drift`, `link_asymmetry_drift`, linked-epics and `undecomposed_drift` (a hard two-backlog rule) remain invisible, so a tree on which reconcile detect exits 1 passes the pre-commit hook and CI, and AGENTS.md's documented gate disagrees with the executed one.

## Steps to Reproduce

Evidence (_reconcile, lines 45-73 (summing line 49, derivable-only addition lines 66-69)): gate.py:49-69 vs reconcile.py `cmd_detect`:1518-1537, which extends `all_drift` with seven additional detectors on the default sweep; both the hook (line 275) and lint.yml (line 60) run gate.py, not reconcile detect; reconcile.py:1625 exits 1 on any drift.

## Proposed Fix

Factor `cmd_detect`'s default sweep into a `detect_all()` returning the full `all_drift` list and have `gate._reconcile` count that, so the gate and reconcile detect can never disagree on the same tree.

## Acceptance Criteria

### AC1: the reconcile lane covers every drift source the detector produces

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReconcileLaneTests
- **Verified:** yes (2026-07-28, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-28 | Claude Fable 5 | Acceptance criterion authored at review - the unit reached Fixed without one, which CR0459 exists to refuse |
