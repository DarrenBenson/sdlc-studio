# US1267: The Phase 5 re-measure publishes cost per point by harness and states plainly whether the 40 per cent bar was met

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0715
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/rfcs/RFC0062-token-efficient-delivery-a-sprint-costs-at-most.md, tools/bench/results/runs.jsonl, tools/tests/test_rfc0062_remeasure.py
> **Epic:** EP0354
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The Phase 5 re-measure publishes cost per point by harness and states plainly whether the 40 per cent bar was met
**So that** CR0715 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: RFC0062 publishes the re-measure by harness

- **Given** the Phase 2 baseline page from US1266 and RFC0062
- **When** the RFC's `## Phase 5 Result` section is read
- **Then** it holds one row per harness the baseline measured: the baseline cost per fixture, the re-measured cost per fixture, the change as a percentage, the held-back pass rate of each, and the cost per point of the one sprint of this repository the RFC's fifth phase names. A harness with no baseline reads not judged. Fails on: a single pooled figure across harnesses, or a harness the baseline measured missing from the table
- **Verify:** pytest tools/tests/test_rfc0062_remeasure.py::Rfc0062RemeasureTests::test_the_phase_5_result_reports_cost_per_point_by_harness

### AC2: The verdict on the 40 per cent bar follows from the figures

- **Given** the same section
- **When** each harness's verdict is read beside its row
- **Then** it says met only where the re-measured cost is at least 40 per cent below the baseline at an equal or better held-back pass rate, and not met otherwise, and the section ends with one sentence stating whether the bar was met overall. Fails on: a 31 per cent saving described as meeting the bar, a verdict left out for a harness that missed it, or a saving claimed at a worse held-back score
- **Verify:** pytest tools/tests/test_rfc0062_remeasure.py::Rfc0062RemeasureTests::test_each_verdict_matches_the_arithmetic_and_the_bar_is_stated_plainly

### AC3: The re-measured figures are recomputed from the committed rows

- **Given** the section and `tools/bench/results/runs.jsonl`
- **When** `runner.py summary` is computed over the measured rows at the skill commit the section names for the re-measure
- **Then** each re-measured cost in the table equals the summary's figure for that fixture, arm and harness, and the baseline column equals the baseline page's. Fails on: a figure typed by hand or a baseline restated to flatter the saving
- **Verify:** pytest tools/tests/test_rfc0062_remeasure.py::Rfc0062RemeasureTests::test_the_remeasured_figures_equal_the_summary_of_the_committed_rows

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
