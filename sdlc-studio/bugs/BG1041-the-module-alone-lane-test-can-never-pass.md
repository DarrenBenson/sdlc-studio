# BG1041: The module-alone lane test can never pass on a host with fewer than four cores, and blames the pool for it

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_gate.py, changelog.d/BG1041.md
> **Created:** 2026-10-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (triage); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-13T14:07:51Z

## Summary

Found by BG1031's QA review on 2026-10-13 (pre-existing since ea8a99a0, BG0649). `test_gate.py`'s ModuleAloneLaneTests floors its sleeper count at four (`min(16, max(4, os.cpu_count() or 1))`), gate.py sizes the lane's pool at `os.cpu_count()`, and the test requires every sleeper asleep at once (`overlap >= n_sleepers`), which a pool of k caps at k. With `PYTHON_CPU_COUNT`=2 the test fails with 'only 2 of 4 sleepers were asleep at once - the pool is smaller than the cores', a false accusation. CI (4 vCPU) and the 8-core gate host never hit it.

## Steps to Reproduce

Run the test with `PYTHON_CPU_COUNT`=2: it fails, blaming the pool.

## Proposed Fix

Require the overlap to reach min(`n_sleepers`, the pool's size as the lane reports it), or drop the floor of four to the core count.

## Acceptance Criteria

- [ ] **AC1** Given a host with two cores, when the module-alone lane test runs, then it passes, and a serial lane still fails it
  - **Verify:** manual: run the test with PYTHON_CPU_COUNT=2 and see it pass, then with the lane serialised and see it fail

## Impact

Low: a contributor on a two-core machine sees the push gate red for a reason that is not true.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | Claude Opus 5.5 (triage) | Filed |
