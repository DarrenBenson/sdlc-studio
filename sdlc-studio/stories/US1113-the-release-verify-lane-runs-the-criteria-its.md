# US1113: The release verify lane runs the criteria its batch cannot resolve on a bounded worker pool, serial_only ones after it

> **Status:** Done
> **Delivers:** CR0660
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_workers.py, changelog.d/US1113.md
> **Epic:** EP0296
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** solo founder-engineer cutting a release (Maya)
**I want** the verifiers the batch cannot resolve (shell, grep, flagged pytest, cache misses) to run on a bounded worker pool
**So that** about 620 serial subprocesses stop setting the release gate's wall-clock time

## Acceptance Criteria

- **AC1:** Given `SDLC_VERIFY_WORKERS=3` and six fixture stories whose verifiers record their start and end, when the release verify lane runs, then no more than three verifiers ever overlap and some do, the detail names `3 worker(s)`, and with `SDLC_VERIFY_WORKERS=1` none overlap
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_workers.py::VerifyLaneWorkersTests::test_the_pool_is_bounded_by_the_worker_setting
  - **Verified:** yes (2026-11-03)
- **AC2:** Given one verifier that outlives the per-verifier ceiling while others run beside it, when the lane reports, then that criterion is red and named in `[ids: ...]`, it is not re-run, and the red count equals the serial run's
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_workers.py::VerifyLaneWorkersTests::test_a_timeout_on_the_pool_still_reads_red
  - **Verified:** yes (2026-11-03)
- **AC3:** Given stories whose verifiers name a test module carrying `serial_only`, when the lane runs, then those stories run after the pool has drained, never beside another verifier
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_workers.py::VerifyLaneWorkersTests::test_serial_only_verifiers_run_after_the_pool
  - **Verified:** yes (2026-11-03)
- **AC4:** Given the pool, when the lane renders, then every clause lists its criteria in the serial run's order and no story file's bytes change
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_workers.py::VerifyLaneWorkersTests::test_the_pool_reports_in_story_order_and_writes_nothing
  - **Verified:** yes (2026-11-03)

## Notes

- Serves: Maya Okafor, End goal 5. CR0660; D0399.
- Design: a `ThreadPoolExecutor` over stories, `SDLC_VERIFY_WORKERS` (default min(cpu_count, 8)), `serial_only`-naming stories after the pool, results reassembled in path order. Use the same `serial_only` text test as `run_tests_plan`.
- AC1 must fail on: a pool with no `max_workers` (one thread per story), or the setting read while the loop stays serial.
- AC2 must fail on: the worker catching the timeout and dropping the story's report, or re-running it alone and keeping the second verdict.
- AC3 must fail on: every story sent to the pool.
- AC4 must fail on: results collected with `as_completed`, or `verify_story(dry_run=False)`.
- Risks: shell verifiers that share state (`.local` files, the git index, a `gate.py` run) can interfere; `SDLC_VERIFY_WORKERS=1` restores serial. Load can push a near-ceiling criterion over its ceiling, which then reads red, as it should (BG1183's two criteria are the likely cases). verify_ac's module globals must stay thread-safe, and the lane opens no corpus cache.
- Overlaps: US1112 (same function, delivered first), BG1183, BG1028.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-02 | Claude Opus 5.5 (grooming) | Groomed under D0399 from the run-five planning pass: user story, criteria with Verify lines, mutants and risks |
