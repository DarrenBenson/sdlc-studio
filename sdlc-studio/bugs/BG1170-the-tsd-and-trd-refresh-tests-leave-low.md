# BG1170: The TSD and TRD refresh tests leave low residual gaps their round-2 and BG1166 reviews named

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_lean_tsd_refresh.py, tools/tests/test_lean_trd_refresh.py, changelog.d/BG1170.md
> **Evidence:** sdlc-studio/reviews/critic-verdicts.md: US1102 round-2 APPROVE and BG1166 APPROVE, 2026-11-01.
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T09:17:58Z

## Summary

Low findings left by the APPROVEs of US1102 at round 2 (qa-seat-US1102-r1, brief 2d7eb9aed8af) and of BG1166 (qa-seat-BG1166-r1, brief 017f7af94efd), 2026-11-01. In tools/tests/`test_lean_tsd_refresh.py`: (1) the percentage pattern misses '82-percent', '82-per-cent' and '82pc'. (2) `mode_mentions` reads only a ticked mode or a ticked `review.line_coverage: <value>`, and only in Coverage Measurement, so '`line_coverage: block`', '`review.line_coverage=block`', an unticked 'runs at block' and a Unit Testing cell pass. (3) `MIN_QUOTE_WORDS` 3 to 2, dropping the `review.line_coverage` condition from the ours selector, and dropping `hundred` each survive. (4) A three-word fragment of a clause still maps it from an unrelated row. (5) `_COUNT_RE` flags 'the two test trees', the module docstring's own phrase, and misses a count with no noun after it ('330 in all'). In tools/tests/`test_lean_trd_refresh.py`: (6) nothing pins the scratch repository's `--template=` guard, so with `GIT_TEMPLATE_DIR` set its removal fails 4 subtests but the suite as run stays green.

## Steps to Reproduce

Apply each reviewer mutant in a throwaway worktree and run the module: each named one stays green.

## Proposed Fix

Widen the percentage and count patterns. Read every `line_coverage` key form across the whole TSD. Require a quote's words to be distinctive to its clause. Add a two-word short-quote mutant and a `GIT_TEMPLATE_DIR` fixture.

## Acceptance Criteria

- [ ] **AC1** Each of the US1102 round-2 reviewer's surviving mutants fails `test_lean_tsd_refresh.py`, and the module's own docstring phrase does not.
  - **Verify:** pytest tools/tests/test_lean_tsd_refresh.py
- [ ] **AC2** Dropping `--template=` from `_ignored` fails `test_lean_trd_refresh.py` under a `GIT_TEMPLATE_DIR` whose info/exclude ignores `*.json`.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py

## Impact

A future stale figure, mode or count in the TSD, or a dropped template guard, could pass these tests.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
