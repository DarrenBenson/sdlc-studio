# US1112: The release verify lane's pytest batch runs on every core under its own ceiling and states how many criteria it resolved

> **Status:** Ready
> **Delivers:** CR0660
> **Created:** 2026-11-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_batch.py, changelog.d/US1112.md
> **Epic:** EP0296
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** solo founder-engineer cutting a release (Maya)
**I want** `gate.py --release` to resolve its pytest criteria from one parallel batch that one verifier's ceiling does not cut off
**So that** a release gate costs about one full-suite run rather than 100 minutes, and a batch that resolved nothing says so

## Acceptance Criteria

- **AC1:** Given pytest-xdist is installed and a fixture workspace whose criteria name tests in two files, one carrying `serial_only` tests, when `pytest_batch_cache` runs, then the other tests run on xdist workers, the `serial_only` tests run afterwards in a process with no worker, and every node lands in the one returned cache
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_batch.py::VerifyLaneBatchTests::test_the_batch_runs_on_xdist_with_serial_only_tests_after
- **AC2:** Given a batch that runs longer than the per-verifier ceiling and shorter than the batch ceiling, when the release verify lane runs, then every batched criterion resolves from the batch and no per-criterion pytest process is spawned for it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_batch.py::VerifyLaneBatchTests::test_the_batch_is_not_cut_off_at_one_verifiers_ceiling
- **AC3:** Given a batch that times out or resolves nothing, when the lane renders, then its cost clause reads `batch resolved 0 of <n> pytest verifier(s)` with the reason, never the bare `(batched)`, and every criterion still runs on its own and keeps its verdict
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_batch.py::VerifyLaneBatchTests::test_an_empty_batch_is_named_and_falls_back
- **AC4:** Given a batched node whose recorded duration exceeds the per-verifier ceiling, when the lane resolves it from the batch, then it reads red as a timeout, exactly as its own spawn would, and the batch ceiling's default is named in the lane's detail and in `gate.py --help`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_batch.py::VerifyLaneBatchTests::test_a_batched_node_over_the_per_verifier_ceiling_reads_red

## Notes

- Serves: Maya Okafor, End goal 5 (every check earns its keep). CR0660; D0399.
- Diagnosis, read from the code (2026-11-02), not yet measured: `verify_ac.pytest_batch_cache` runs the 350 verifier test files as one serial `pytest -q` process under the per-verifier ceiling (300 s by default, 450 and 900 at 6.2.0), while the serial skill suite alone takes about 597 s. The batch times out and returns `{}` with only a debug log, and about 2,095 bare-node pytest verifiers fall back to cold per-criterion spawns, roughly 4,200 s against the measured 4,447 s lane. AC3 makes the lane state it.
- Design: run the batch the way `gate.run_tests_plan` runs a selection (`-n auto --maxschedchunk=1 -m "not serial_only"`, then the `serial_only` files), with one junit file per phase merged, under its own ceiling (`SDLC_VERIFY_BATCH_TIMEOUT`).
- AC1 must fail on: `-n auto` dropped from the batch argv, or the `serial_only` tests run in the parallel phase. The fixture tests record `PYTEST_XDIST_WORKER` to a file.
- AC2 must fail on: the per-verifier `timeout` passed to the batch subprocess, as today. Each fixture test appends its name to a log when it runs, so ran-once against ran-twice is observed, not patched (LL0014).
- AC4 must fail on: a batch result trusted whatever its junit duration, which reverses the one-ceiling invariant at gate.py:1664 and would let US0940's 535 s criterion resolve green from the batch (engineering seat, goal review). Name `SDLC_VERIFY_BATCH_TIMEOUT`'s default.
- AC3 must fail on: `' (batched)' if batch` restored, or an empty cache resolving a node as passed.
- Must not change: a verifier past its ceiling reads red; nothing writes Verified back; `--release --skip verify` stays refused; the cache lives for one lane run only, and an empty, timed-out or crashed batch or an absent node never resolves green.
- Risks: a verifier test green serially and red under xdist now reads red, which is a finding, not a lane regression. Merging the phases must not let one phase's missing node shadow the other's result. Keep `SDLC_STUDIO_BOUNDARY_SUITE` as it is. Re-derive `VERIFY_LANE_BUDGET_S` from the first measured run. Correct the stale collection comment in `pytest_batch_cache` (pytest.ini pins `--import-mode=importlib`).
- Overlaps: US1113 edits the same function (`gate._verify_acs`), so deliver US1112 first. BG1100, BG1183, BG1028.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-02 | Claude Opus 5.5 (grooming) | Groomed under D0399 from the run-five planning pass: user story, criteria with Verify lines, mutants and risks |
| 2026-11-02 | Claude Opus 5.5 (grooming) | Goal review (engineering seat): AC4 added, so a batched node over the per-verifier ceiling still reads red |
