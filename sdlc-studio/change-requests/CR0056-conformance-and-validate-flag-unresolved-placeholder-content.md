# CR-0056: conformance and validate flag unresolved placeholder content

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-21

## Summary

Self-audit: a freshly-scaffolded Draft story from artifact.new passes conformance (specified+verifiable) with pure {{placeholder}} AC and a {{placeholder}} Verify line - the placeholder counts as a real AC/verifier. A hidden conformance hole. Validate reports 0 errors on the scaffold.

## Acceptance Criteria

- [x] validate flags unresolved {{...}} placeholders in AC/Verify/required sections as an error
- [x] conformance treats a placeholder-only AC/Verify as not-yet-specified (a scaffold cannot reach Done with placeholders)
- [x] tested; critic APPROVE

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | audit | Raised |
| 2026-06-21 | Autosprint (CR0056) | Built: validate + conformance placeholder-only detection (value-based, gates agree); critic APPROVE + dogfood fixed 2 false-positive checkbox matches |
