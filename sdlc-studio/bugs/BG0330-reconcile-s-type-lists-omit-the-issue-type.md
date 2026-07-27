# BG0330: reconcile's type lists omit the issue type, so the issues index is never reconciled by any path

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

reconcile.py hardcodes 8 of the 9 `sdlc_md.ARTIFACT_TYPES`, omitting 'issue', and no --scope names it either, so detect/apply/index-derived can never census sdlc-studio/issues/ - status-mismatch, missing-row, orphan-row and count drift in the issues index are exempt from every automated check even though artifact.py, triage.py, status.py and the shipped index template fully support the type. archive.py derives its type list from `ARTIFACT_TYPES`, the convention reconcile violates.

## Steps to Reproduce

Evidence (`SCOPE_TYPES` (lines 35-46) and `DEFAULT_TYPES` (line 47); inherited by `cmd_detect`, `cmd_apply`, `index_derived_issues`, and gate.py:_reconcile): reconcile.py:47 and :44 omit issue; `sdlc_md.py`:825-835 has nine types including issue; only transition.py:800's `apply_type` call syncs an issue row, and only at transition time; gate.py:49 sums over the same incomplete `DEFAULT_TYPES.`

## Proposed Fix

Derive `DEFAULT_TYPES` and the `SCOPE_TYPES` indexes list from `sdlc_md.ARTIFACT_TYPES` (as archive.py does) so issue - and any future type - is censused by detect, apply, and the gate lane.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
