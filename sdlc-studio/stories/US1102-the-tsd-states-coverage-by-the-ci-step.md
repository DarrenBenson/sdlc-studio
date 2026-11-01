# US1102: The TSD states coverage by the CI step, describes per-unit line coverage, names both test-module conventions, maps every PRD NFR to a row and carries a 6.2 header

> **Status:** Ready
> **Delivers:** CR0646
> **Created:** 2026-10-31
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/tsd.md, tools/tests/test_lean_tsd_refresh.py, changelog.d/US1102.md
> **Epic:** EP0293
> **Points:** 3
> **Depends on:** US1098, US1104
> **Persona:** Rowan Achterberg

## User Story

**As** the skill maintainer releasing 6.2
**I want** the TSD to state coverage by the CI step, describe per-unit line coverage, name both test-module conventions, map every PRD NFR to a row and carry a 6.2 header
**So that** a reader can map each PRD NFR to the gate that holds it, and the TSD no longer under-reports its own coverage (CR0646)

## Acceptance Criteria

- **AC1:** Given the CI coverage step and `review.line_coverage` in this repo's config, when the TSD is read, then coverage is stated by pointing at that step rather than as a pinned figure, and per-unit added-line coverage is described with this repo's setting
  - **Verify:** pytest tools/tests/test_lean_tsd_refresh.py::TsdRefreshTests::test_coverage_points_at_ci_and_names_line_coverage
- **AC2:** Given the test tree, when the TSD is read, then it names both module conventions (per-script and per-unit lean), the shared helpers, the pytest markers and the hooks, with no module count
  - **Verify:** pytest tools/tests/test_lean_tsd_refresh.py::TsdRefreshTests::test_the_test_tree_names_both_conventions
- **AC3:** Given every non-functional requirement in the PRD, when the TSD is read, then each maps to a TSD row, including the network paths, the appetite breaker and ULID identity
  - **Verify:** pytest tools/tests/test_lean_tsd_refresh.py::TsdRefreshTests::test_every_prd_nfr_has_a_tsd_row
- **AC4:** Given the TSD's header and revision history, when they are read, then the header names the 6.2 baseline and one of the document's own status values, and the history is in date order
  - **Verify:** pytest tools/tests/test_lean_tsd_refresh.py::TsdRefreshTests::test_the_header_and_history

## Notes

- From BG1065 (2026-11-01): tsd.md:354 still says 'Every run in this repository now exceeds it (BG1065)'. Since BG1065, the budget is recorded beside a measured standard run (gate.py GATE_BUDGET_MEASURED) and a push judges only the standard lanes against it. Correct that sentence in this unit, which owns tsd.md.
- Serves: Rowan Achterberg, End goal 3.
- Source: sdlc-studio/reviews/RV0028-unified-review-before-the-second-6-2-run.md, the TSD leg, and CR0646.
- AC1 must fail on: a pinned coverage percentage, or the line-coverage setting stated as anything but the config's value (read from .config.yaml).
- AC3 must fail on: an NFR added to the PRD with no TSD row; the NFR set is read from the PRD's table, never typed into the test.
- AC4 must fail on: a revision history out of date order, or a status value the document does not define.
- Sequence after US1098 (the census) and US1104 (which moves the PRD's NFRs that AC3 maps). Covers CR0646 AC1-AC4.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-31 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-31 | Claude Opus 5.5 | Groomed for run four (D0392): criteria with Verify lines, each criterion's mutant, overlaps and sequence |
