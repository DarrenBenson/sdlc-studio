# BG1102: The corpus-verify timing step's ceiling is pinned only as an integer, so one as long as the job's own cap passes

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_corpus_verify_env.py, changelog.d/BG1102.md
> **Evidence:** BG1054 QA review, round 2 (APPROVE), qa-seat-BG1054-r1, 2026-10-20, at e161e6ba: mutant R5 survived alone.
> **Created:** 2026-10-20
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-20T08:23:08Z

## Summary

`test_the_timing_step_never_stops_the_job` checks only that the timing step's timeout-minutes is an int. A ceiling of 150, equal to the corpus-verify job's cap, passes the test, though a hung verifier would then end the whole job before the verification step runs. The current 15 is sound.

## Steps to Reproduce

Set the timing step's timeout-minutes to 150 in .github/workflows/lint.yml and run tools/tests/`test_corpus_verify_env.py`: green.

## Proposed Fix

Require the step's ceiling to leave the job's cap less the lane's measured time free for the verification step.

## Acceptance Criteria

- [ ] **AC1** A timing-step ceiling that leaves the verification step less than its measured time turns the test red
  - **Verify:** pytest tools/tests/test_corpus_verify_step_ceiling.py::CorpusVerifyStepCeilingTests

## Impact

A later edit can raise the step's ceiling to one that lets a hang consume the job.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-20 | Claude Opus 5.5 | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): Won't Fix, not beneficial (LL0056): it pins a hypothetical edit to a timeout ceiling on a step that is already bounded and cannot stop the job |
