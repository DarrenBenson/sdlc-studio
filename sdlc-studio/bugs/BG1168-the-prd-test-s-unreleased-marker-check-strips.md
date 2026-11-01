# BG1168: The PRD test's unreleased-marker check strips code spans from the whole row, and PRD edits land with no Revision History row

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_lean_prd_refresh.py, sdlc-studio/prd.md, changelog.d/BG1168.md
> **Evidence:** critic-verdicts.md: the full-tier APPROVEs of US1082 by qa-seat-US1082-r1 (brief 4667a10df171) and of US1103 by qa-seat-US1103-r1 (brief 0694a83d48e7).
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T08:44:27Z

## Summary

Two low findings from the full-tier re-reviews of US1082 and US1103 (2026-11-01). (1) `unreleased_marks` in tools/tests/`test_lean_prd_refresh.py` strips code spans from the whole row line, and from the whole details block. So a shipped Status cell, or a details Status line, that reads Complete followed by the marker in backticks passes AC1 (reviewer probes Q21 and Q22). The exemption exists only for the release-cut row's Description. (2) 75c53a6d (US1082) and 14746a94 (US1079) changed sdlc-studio/prd.md without a Revision History row, and nothing asks for one.

## Steps to Reproduce

1. Append the marker in backticks to a shipped row's Status cell in a throwaway worktree, then run `test_lean_prd_refresh.py`: green.
2. `git show 75c53a6d -- sdlc-studio/prd.md`: no Revision History row.

## Proposed Fix

Exempt a code span only inside the Description cell. Add a check, or a `doc_freshness` rule, that a PRD content change carries a Revision History row dated on or after it.

## Acceptance Criteria

- [ ] **AC1** A Status cell or details Status line that carries the unreleased marker inside a code span fails `test_lean_prd_refresh.py`, and the release-cut row's Description still passes.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py
- [ ] **AC2** The PRD's Revision History holds a row for every commit since 6.1.0 that changed its content.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py

## Impact

A shipped row can carry the unreleased marker unseen, and the PRD's history under-reports its edits.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
