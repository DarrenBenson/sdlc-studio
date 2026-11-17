# US1266: The Phase 2 baseline runs the benchmark at the pinned skill commit in each installed harness and commits the result

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0715
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** docs/benchmarks/protocol-v2.md, docs/benchmarks/rfc0062-phase2-baseline.md, tools/bench/results/runs.jsonl, tools/tests/test_benchmark_protocol.py
> **Epic:** EP0354
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The Phase 2 baseline runs the benchmark at the pinned skill commit in each installed harness and commits the result
**So that** CR0715 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The baseline page reports every harness the runner supports

- **Given** `docs/benchmarks/rfc0062-phase2-baseline.md`
- **When** it is read against the harnesses `tools/bench/runner.py` holds a headless command for
- **Then** it names the skill commit 5057f7ef by its full id, and for each of those harnesses either a measured row per fixture and arm (runs, mean tokens, mean US dollar cost, held-back pass rate) or a line saying the harness was not installed or could not be metered, with the reason. Claude Code has three runs per fixture and arm and each other measured harness one or two, as RFC0062's Phase 2 states. Fails on: a harness left off the page without a word, or a run count the plan did not ask for passed off as the plan's
- **Verify:** pytest tools/tests/test_benchmark_protocol.py::Rfc0062Phase2Baseline::test_the_baseline_page_reports_every_supported_harness_at_the_pinned_commit

### AC2: Every figure on the page is recomputed from the committed rows

- **Given** the page and `tools/bench/results/runs.jsonl`
- **When** `runner.py summary` is computed over the log's measured rows whose `skill_ref` is 5057f7ef
- **Then** each mean on the page equals the summary's figure for that fixture, arm and harness, and every such row reads `metrics_source` measured. Fails on: a figure typed by hand, a calibration row pooled in, or a row measured at another commit counted in the baseline
- **Verify:** pytest tools/tests/test_benchmark_protocol.py::Rfc0062Phase2Baseline::test_the_pages_figures_equal_the_summary_of_the_committed_rows

### AC3: The protocol records the baseline without being reshaped

- **Given** `docs/benchmarks/protocol-v2.md`
- **When** its Status section is read
- **Then** it gains a line that links the baseline page, the sections the existing protocol tests pin are all still present, and where the baseline's run counts differ from the protocol's sample size the baseline page says so under a heading that names it a deviation. Fails on: a sample size quietly edited to fit the runs that were made
- **Verify:** pytest tools/tests/test_benchmark_protocol.py::Rfc0062Phase2Baseline::test_the_protocol_links_the_baseline_and_states_any_deviation

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
