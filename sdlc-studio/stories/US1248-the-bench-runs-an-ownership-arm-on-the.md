# US1248: The bench runs an ownership arm on the brownfield fixtures, reporting priced tokens, score and duplication

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0701
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/bench/runner.py, tools/bench/transcript_metrics.py, tools/tests/test_bench_runner.py, tools/bench/arms/pipeline_ownership_CLAUDE.md, changelog.d/US1248.md
> **Epic:** EP0343
> **Points:** 3
> **Persona:** Rowan Achterberg

## User Story

**As a** Rowan Achterberg
**I want** The bench runs an ownership arm on the brownfield fixtures, reporting priced tokens, score and duplication
**So that** CR0701 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The ownership arm differs from the pipeline arm by the ownership line alone

- **Given** the two brownfield fixtures
- **When** `runner.py prepare` lays out the ownership arm and the pipeline arm of each
- **Then** the ownership arm's workspace holds the skill and the same visible files, and its instructions are the pipeline arm's plus the ownership line, nothing else. Fails on: an arm with no skill, or one that differs in more than the line, so the comparison measures something else
- **Verify:** pytest tools/tests/test_bench_runner.py::OwnershipArmTests::test_the_ownership_arm_is_the_pipeline_arm_plus_the_line

### AC2: Duplicated lines are counted before and after by one named tool

- **Given** a workspace whose visible files hold a known duplicated block, and a finished copy with the block merged
- **When** the run is scored and recorded
- **Then** the entry records the duplicated lines before and after, both from the same counter, and names that counter; the known block is counted exactly, and the merged copy counts fewer. Fails on: a count taken only after the run, two counters for the two figures, or a figure with no tool named
- **Verify:** pytest tools/tests/test_bench_runner.py::OwnershipArmTests::test_duplicated_lines_are_counted_before_and_after_by_one_tool

### AC3: The summary sets the ownership arm beside the pipeline arm

- **Given** recorded runs of both arms on a brownfield fixture, one run carrying no duplication count
- **When** `runner.py summary` aggregates them
- **Then** each arm's row for the fixture states priced tokens with the dollar cost, the held-back suite score and duplicated lines before and after, and the run with no count is left out of that mean, never read as zero. Fails on: the ownership arm folded into the pipeline arm's row, or a missing count averaged in as zero
- **Verify:** pytest tools/tests/test_bench_runner.py::OwnershipArmTests::test_the_summary_reports_tokens_score_and_duplication_per_arm

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
