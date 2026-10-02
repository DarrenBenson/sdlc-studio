# BG0902: A late lane return --tokens writes into a sealed run and invalidates its signed page

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_sealed_run_late_total.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Evidence:** US0980 QA review round 1 (RUN-01M3Y7DP)
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T12:59:03Z

## Summary

`run_state.record_delegated_tokens` checks only the run id (`run_state.py`:1533), so a lane return made after sprint sign records into the sealed run and the signed page re-derives INVALIDATED (`tokens_delegated`, `est_actual`, `eu_tokens`, `eu_minutes` move). BG0830 (Won't Fix, D0291) ruled the general case below cost because its fix was a refusal; US0980 makes a late lane return a more likely route in.

## Steps to Reproduce

1. Close and sign a run with a lane in flight. 2. lane return --units X --tokens 7000. 3. `sprint_report.py` check -> INVALIDATED.

## Proposed Fix

Record nothing into a run whose outcome is no longer running and print one line saying the run is sealed (a warning, not a refusal).

## Acceptance Criteria

- [ ] **AC1** Given a sealed run whose signed page checks VALID, when lane return --units X --tokens 7000 runs, then nothing is recorded, a line says the run is sealed, and the page still checks VALID. Fails on: the current code records into the sealed run and the page reads INVALIDATED
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_sealed_run_late_total.py::SealedRunLateTotalTests::test_a_late_total_leaves_the_sealed_page_valid

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
