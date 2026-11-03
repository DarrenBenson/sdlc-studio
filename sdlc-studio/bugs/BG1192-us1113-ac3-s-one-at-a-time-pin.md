# BG1192: US1113 AC3's one-at-a-time pin lets a concurrent serial pool through under load, because its three 0.5 s probes must start within 0.5 s of each other

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_workers.py, changelog.d/BG1192.md
> **Evidence:** US1113 round-2 verdict, scratchpad run5/US1113-verdict-r2.txt.
> **Created:** 2026-11-03
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-03T11:24:42Z

## Summary

2026-11-03, US1113's round-2 review (qa-seat-US1113-r1, APPROVE, non-blocking). `test_serial_only_verifiers_run_after_the_pool` (`test_verify_lane_workers.py`:233) proves the `serial_only` stories run one at a time by watching three 0.5 s probes (`test_verify_lane_workers.py`:56) for overlap. The mutant that runs them on their own pool of `workers` threads passed the AC3 node once at a 15-minute load average of 9.78 on 8 cores, and was killed 3 of 3 when run alone. The real code never reads falsely red, so this is a pin that can miss the defect on a slow machine, not a flaky failure.

## Steps to Reproduce

1. Load the machine (the reviewer ran parallel probes at load about 10 on 8 cores).
2. Apply the mutant that sends the `serial_only` stories to a ThreadPoolExecutor of `workers` threads.
3. Run the AC3 node: it can pass.

## Proposed Fix

Have each probe hold a shared marker (a lock file or a counter file) for its whole run and record the most it ever saw held at once, so overlap is detected whatever the start skew, instead of relying on 0.5 s sleeps overlapping.

## Acceptance Criteria

- [ ] **AC1** AC3's test fails on the serial-pool mutant however late each probe starts, shown by a run that delays each probe's start by more than its sleep.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_workers.py

## Impact

A later edit that runs `serial_only` verifiers concurrently can pass the push gate on a loaded host.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-03 | claude | Filed |
