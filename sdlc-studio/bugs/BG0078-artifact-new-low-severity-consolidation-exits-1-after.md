# BG0078: artifact new Low-severity consolidation exits 1 after creating the CR, and its dry-run crashes

> **Status:** Fixed
> **Severity:** Medium
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio file
> **Verification depth:** functional (CLI tests: dry-run, first-create and append paths all exit 0 with shape-correct output; suite 1463 green)

## Summary

rc-verdict: BLOCKS v4.0 tag (borderline: one-line fix, flagship EP0014 triage lane on the v3-default era). On a schema-v3 project a Low-severity finding folds into a consolidation CR (triage_noise.py:218-244) whose result dict lacks epic_linked (and indexed/id semantics in dry-run); cmd_new's text path prints r['indexed']/r['epic_linked'] unconditionally (artifact.py:472-474; the setdefault at :333 patches only 'indexed'). Reproduced (RV0007): --dry-run -> error: 'indexed', exit 1; real run -> the CR IS created/appended, then error: 'epic_linked', exit 1. A false non-zero exit after a landed side effect invites an orchestrator retry and duplicate consolidated findings; --format json is unaffected (text path only).

## Steps to Reproduce

schema_version: 3 fixture; artifact.py new --type bug --severity Low --title x -> CR file created, then exit 1 'epic_linked'; same with --dry-run -> exit 1 'indexed', nothing written.

## Proposed Fix

Print consolidation results by their own shape (r.get with defaults) in cmd_new's text path; cover both create and append paths with a test.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Filed |
