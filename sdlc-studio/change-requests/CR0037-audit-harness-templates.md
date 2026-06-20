# CR-0037: portable audit prompt-harness templates (RFC0002 WS2)

> **Status:** Complete
> **Priority:** Medium
> **Type:** Feature
> **Requester:** Autosprint (RFC0002)
> **RFC:** RFC-0002
> **Date:** 2026-06-20
> **Affects:** templates/automation/audit-finder.md (new), audit-refute.md (new), audit-classify.md (new)
> **Depends on:** CR0036 (WS1)
> **GitHub Issue:** --

## Summary

Spawned from RFC0002 WS2. The portable, tool-neutral prompt harness for the audit
pipeline: a per-lens loop-until-dry finder, an independent refute-panel skeptic, and a
merge/classify step that emits the exact fields `file_finding.py` needs. Any
AGENTS.md-capable harness can drive them (Option A, D2 portable-first).

## Acceptance Criteria

- [x] `audit-finder.md` is a per-lens finder prompt with structured JSON output and an empty-round (loop-until-dry) terminator.
- [x] `audit-refute.md` is a single-skeptic refute prompt defaulting to refuted-on-uncertainty, parameterised by vote count + survive threshold + refute lens.
- [x] `audit-classify.md` merges + classifies survivors and emits the per-type fields the filer requires (so artifacts are rich, not hollow).
- [x] All three use `{{placeholder}}` syntax and pass lint.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (RFC0002) | Complete - finder/refute/classify harness templates |
