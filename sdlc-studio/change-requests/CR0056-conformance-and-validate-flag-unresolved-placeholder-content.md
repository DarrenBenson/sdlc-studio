# CR-0056: conformance and validate flag unresolved placeholder content

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-21

## Summary

Self-audit: a freshly-scaffolded Draft story from artifact.new passes conformance (specified+verifiable) with pure {{placeholder}} AC and a {{placeholder}} Verify line - the placeholder counts as a real AC/verifier. A hidden conformance hole. Validate reports 0 errors on the scaffold.

## Acceptance Criteria

- [ ] validate flags unresolved {{...}} placeholders in AC/Verify/required sections as an error
- [ ] conformance treats a placeholder-only AC/Verify as not-yet-specified (a scaffold cannot reach Done with placeholders)
- [ ] tested; critic APPROVE

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | audit | Raised |
