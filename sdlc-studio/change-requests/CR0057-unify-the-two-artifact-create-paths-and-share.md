# CR-0057: unify the two artifact create paths and share index helpers

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-21

## Summary

Self-audit: artifact.new and file_finding.file are two create paths for cr/rfc/bug that diverge - file_finding writes NO provenance stamp (so provenance check false-flags audit-filed artifacts, incl. the CRs just filed), uses a different index-row convention (Updated=-- vs the header-driven builder), and duplicates the data-header-finder loop, the reconcile._join_row private call, and a divergent _slug. Unify: file_finding stamps too; one shared header-driven row builder + find_data_header + _join_row moved to lib; one slug. Add --dry-run parity to new/close/file/pvd sync.

## Acceptance Criteria

- [ ] file_finding-created artifacts carry a provenance stamp (provenance check no longer false-flags them)
- [ ] one shared index-row builder + data-header finder + _join_row (in lib) used by both paths
- [ ] --dry-run added to artifact new/close, file_finding file, pvd sync (parity with reconcile apply / provenance remake)
- [ ] tested; critic APPROVE

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | audit | Raised |
