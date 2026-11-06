# US1128: The benchmark runs a fixture headless in any supported CLI against a pinned skill version and records the usage it prints

> **Status:** Done
> **Delivers:** CR0669
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/bench/runner.py, tools/tests/test_bench_headless.py, changelog.d/US1128.md
> **Epic:** EP0299
> **Points:** 5
> **Depends on:** US1125, US1122
> **Persona:** Rowan Achterberg

## User Story

**As a** Rowan Achterberg
**I want** The benchmark runs a fixture headless in any supported CLI against a pinned skill version and records the usage it prints
**So that** the consuming-project cost is measured the same way in every harness

## Acceptance Criteria

- **AC1:** Given `runner.py prepare --harness <h> --skill-ref <commit>`, then the workspace holds that commit's skill in the harness's local skill directory as `install.sh --list-targets` names it, and a harness with no skill directory is refused by name. Fails on: the working tree's skill installed instead of the pinned commit's
  - **Verify:** pytest tools/tests/test_bench_headless.py::BenchHeadlessTests::test_prepare_installs_the_pinned_skill_for_the_harness
  - **Verified:** yes (2026-11-06)
- **AC2:** Given `runner.py run`, then the arm's prompt runs headless in that CLI (a fake CLI in the test), and the result row records tokens normalised by `lib/harness_usage.py`, the wall time and the held-back suite score, with `metrics_source` measured. Fails on: tokens recorded by hand, or a row written when the CLI printed no usage
  - **Verify:** pytest tools/tests/test_bench_headless.py::BenchHeadlessTests::test_run_records_measured_usage_and_score
  - **Verified:** yes (2026-11-06)
- **AC3:** Given `runner.py summary`, then it reports each fixture, arm and harness, with the estimated US dollar cost where the model is priced. Fails on: two harnesses' rows pooled into one
  - **Verify:** pytest tools/tests/test_bench_headless.py::BenchHeadlessTests::test_summary_by_fixture_arm_and_harness_with_dollars
  - **Verified:** yes (2026-11-06)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-06 | Claude Opus 5.5 | Groomed: criteria and Verify checks authored for run seven (RFC0062 Phase 1) |
