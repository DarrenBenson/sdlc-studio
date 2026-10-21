# BG1090: test_output_prints_in_declared_order_whatever_finishes_first failed one subtest under heavy load, and passes alone; not yet diagnosed

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** tools/tests/test_lean_precommit_parallel.py, changelog.d/BG1090.md
> **Evidence:** 2026-10-19 19:00, studypc2, tools suite at 0d892e52's parent tree plus its fix: `SUBFAILED(run='3') tools/tests/test_lean_precommit_parallel.py::ParallelLaneTests::test_output_prints_in_declared_order_whatever_finishes_first`, 1 failed, 975 passed in 735.65s; three solo re-runs passed (about 12 s each).
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T18:15:09Z

## Summary

In a full tools suite run at -n 4 on studypc2, beside two review agents' test runs (load average 6-9, the run taking 735 s against a usual 380 s), subtest run=3 of tools/tests/`test_lean_precommit_parallel.py`::ParallelLaneTests::`test_output_prints_in_declared_order_whatever_finishes_first` failed. Run alone straight after, it passed three times out of three. Nothing in the change under test touched the pre-commit hook it exercises. The cause is NOT established: BG1077 was first filed as a load flake and turned out to be a real regression, so this is recorded as an undiagnosed failure, not as a flake.

## Steps to Reproduce

Run `python3 -m pytest -q -n 4 tools/tests` while other test runs load the machine; on 2026-10-19 one run in one failed subtest run=3.

## Proposed Fix

Read the failing subtest's assertion under load (capture its output), and either make its synchronisation event-driven or find the real defect.

## Acceptance Criteria

- [ ] **AC1** Given each lane started later than the 0.25 s step between the declared sleeps (a start delay the fixture injects, as load does), when the declared-order test's commit runs, then the verdicts still print in declared order, and the test's own Given does not depend on sleep ordering
  - **Verify:** pytest tools/tests/test_lean_precommit_parallel.py::ParallelLaneTests::test_declared_order_holds_when_lanes_start_late

## Impact

A push or a local suite run can be refused by a failure that may or may not be a defect.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
