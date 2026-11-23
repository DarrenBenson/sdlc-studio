# BG1694: test_kill_grace_interrupt reads the deaf child's pid file before the child has written it, so it fails under load

> **Status:** Fixed
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_kill_grace_interrupt.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land_commit_timeout_group.py, tools/tests/test_test_census.py, changelog.d/BG1694.md
> **Evidence:** .local/run21/land-RBG1470b.log: FAILED test_kill_grace_interrupt.py::KillGraceInterruptTests::test_an_interrupted_grace_sigkills_the_group_and_propagates, ValueError at line 66; test_kill_grace_interrupt.py:29-31 (DEAF writes with open().write), :64-66 (_child reads at once). Introduced by 09cf0766.
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T20:14:11Z

## Summary

`KillGraceInterruptTests._child` reads child.pid with int(`read_text())` as soon as the fake CLI has marked its SIGTERM. The deaf child writes that file with open(path, 'w').write(pid), which creates it empty first, and under load the child may not have started or written by then: the read gets '' and the case fails with ValueError: invalid literal for int() with base 10: ''. It refused a run twenty-one landing (BG1470, prose only) in the commit hook at load 7.7, where the same tree passed the full suite on the gate host.

## Steps to Reproduce

1. Load the workstation (load above the core count). 2. Commit any change that selects `test_kill_grace_interrupt.py`, or run it in a loop. 3. `test_an_interrupted_grace_sigkills_the_group_and_propagates` fails now and then at `test_kill_grace_interrupt.py`:66 with ValueError on an empty pid file.

## Proposed Fix

In `_child`, wait (with `_wait_for` and a bound) until child.pid holds an integer before reading it, and have the deaf child write it atomically (write a temporary name, then os.replace).

## Acceptance Criteria

- [ ] **AC1** Given the machine under load, when `test_kill_grace_interrupt.py` runs, then `KillGraceInterruptTests._child` waits under a bound (`_wait_for`) until child.pid holds an integer before reading it. Fails on: `ValueError: invalid literal for int() with base 10: ''` at `_child`, which refused run twenty-three's push of e2a109be on the gate host.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_kill_grace_interrupt.py
  - **Verified:** yes (2026-11-23)
- [ ] **AC2** Given the deaf child in `test_kill_grace_interrupt.py`, when it records its pid, then it writes a temporary name and moves it into place with `os.replace`, so a reader never sees an empty child.pid. Fails on: `open(path, 'w').write(pid)`, which creates the file empty before writing.
  - **Verify:** shell grep -q 'os.replace' .claude/skills/sdlc-studio/scripts/tests/test_kill_grace_interrupt.py && python3 -m pytest -q .claude/skills/sdlc-studio/scripts/tests/test_kill_grace_interrupt.py
  - **Verified:** yes (2026-11-23)
- [ ] **AC3** Given the machine under load, when `test_lane_land_commit_timeout_group.py` runs, then `LandCommitTimeoutKillsHooksTests._pid` waits under a bound until the hook's pid file holds an integer before reading it, and the hook writes it atomically. Fails on: `ValueError: invalid literal for int() with base 10: ''` from `_pid`, as a run twenty-three commit hit at load 13.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land_commit_timeout_group.py
  - **Verified:** yes (2026-11-23)
- [ ] **AC4** Given the wall-clock census, when `tools/tests/test_test_census.py` runs, then neither new bound test (`test_child_gives_up_at_its_bound`, `test_pid_gives_up_at_its_bound`) is named as a commit-run test bounding a duration its own process measures: each is marked `serial_only` (or `boundary_only`) or bounds nothing by wall clock. Fails on: the two `assertLess(time.monotonic() - started, 10, ...)` lines landed in e14e7052, which refused REF2's commit.
  - **Verify:** pytest tools/tests/test_test_census.py::WallClockCensusTests
  - **Verified:** yes (2026-11-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three orchestrator) | AC3 added and Affects widened: test_lane_land_commit_timeout_group's `_pid` reads the hook's pid file before the hook writes it, the same race, which blocked the EFCI commit at load 13 in run twenty-three |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three orchestrator) | Groomed AC1 and AC2 into executable criteria and pointed at 2 for AC3's second test, after the race refused a push of e2a109be on the gate host; pulled into run twenty-three |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three orchestrator) | Reopened with AC4: the landed fix's two bound tests assert a wall-clock duration in commit-run tests, which the wall-clock census refuses; found when REF2's commit selected the census |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three orchestrator) | Affects widened to tools/tests/test_test_census.py, the test AC4's Verify runs: the repair's two wall-clock mutants are killed by the census, and the land refuses a mutant checked against a test the unit does not declare |
