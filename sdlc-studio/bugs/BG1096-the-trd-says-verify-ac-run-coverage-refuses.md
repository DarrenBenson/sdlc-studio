# BG1096: The TRD says verify_ac run --coverage refuses under block and reports under report when coverage is absent; the split is the Done gate's

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/trd.md, tools/tests/test_trd_coverage_soft_dependency.py, changelog.d/BG1096.md
> **Evidence:** US1085 QA review, round 2 (APPROVE), qa-seat-US1085-r1, 2026-10-19, at 7916edc3: [new] item 2 [LC-018].
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T20:48:59Z

## Summary

trd.md's Script language row says that without `coverage` 'the run refuses under `block` and reports under `report`'. With coverage hidden, `verify_ac run --coverage` exits 2 ('the coverage module is absent') under both settings. The block/report split belongs to the Done transition's gate (transition.py:813-818, pinned by `test_transition.py` CoverageGateTests::`test_a_missing_coverage_module_never_reads_as_covered).` AGENTS.md credits it to the run and the gate together.

## Steps to Reproduce

Hide coverage and run `verify_ac.py run --coverage --id <story>` under `review.line_coverage` report and block: exit 2 both times.

## Proposed Fix

Say the run reports the module absent, and the Done gate refuses under block and reports under report.

## Acceptance Criteria

- [ ] **AC1** The TRD's coverage clause names the Done gate as the block/report split, and the run's own exit without coverage
  - **Verify:** pytest tools/tests/test_trd_coverage_soft_dependency.py::TrdCoverageSoftDependencyTests

## Impact

A reader expects the run itself to honour `review.line_coverage.`

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
