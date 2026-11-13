# BG1330: 15 of RPT0028's 19 units have no priced cost of their own, because only a hand-run `lane return --agent` prices a unit, and the close counts no gap

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, changelog.d/BG1330.md, .claude/skills/sdlc-studio/scripts/tests/test_close_cost_regression.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_known_issues.py
> **Evidence:** sdlc-studio/reports/RPT0028-sprint-report-run-01m7061x.md (per-unit table); RUN-01M7061X
> **Created:** 2026-11-10
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-10T12:22:17Z

## Summary

RPT0028's per-unit table reads 'NOT MEASURED - no agent returned for it was priced from its own transcript' for 15 of 19 units. Only US0986, US1130, US1133 and US1143, which the orchestrator put through `sprint.py lane return --units X --agent A` by hand on their second round, are priced. `sprint.py lane land` already takes the builder's id from its worktree name (agent-<id>) as the self-check author, but records no return, and the close reported 0 gaps. A per-unit cost forecast cannot be compared with actuals until each unit is priced.

## Steps to Reproduce

1. Deliver a unit through `sprint.py lane brief`, a builder agent in a worktree, `sprint.py lane land` and `sprint.py lane accept`, without running `lane return`.
2. Close the run.
3. Read the report's per-unit table: the unit's Dollars and Priced cells read NOT MEASURED, and the close lists no gap for it.

## Proposed Fix

`lane land` records the builder's return from its worktree's agent id when that agent's transcript is readable, or `lane accept` warns while a unit has none; the close lists each unpriced unit as a gap.

## Acceptance Criteria

- [ ] **AC1** Given a lane worktree named `agent-<id>` whose builder transcript is readable in a fixture harness store (CLAUDE_CONFIG_DIR set to a temporary directory), when `sprint lane land` lands it, then each landed unit has a return recorded and priced from that transcript, as `lane return --agent <id>` records one; beside it, a worktree whose transcript cannot be read still lands and names the unit as unpriced. Fails on: a landed unit with a readable transcript left with no priced return.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LandPricesTheBuilderTests
  - **Verified:** yes (2026-11-13)
- [ ] **AC2** Given a closed run whose report reads a unit as NOT MEASURED for want of a priced return, the close counts that unit among the gaps it reports and names it. Fails on: the close reporting 0 gaps while a unit's cost is not measured.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::UnpricedUnitIsAGapTests
  - **Verified:** yes (2026-11-13)

## Evidence

A consuming project's measured cost, delivering with Grok 4.7 through Cursor and priced at xAI's API rates (double for a prompt of 200k tokens or more), from its usage exports of 6 to 10 November 2026 (supplied by the operator, 2026-11-10). One agent running the whole sprint: $282.09 over 2,181 requests for 79 points ($3.57 a point). Prompts of 200k tokens or more were 29% of its requests and 57% of its cost, and $157.11 (56%) could not be tied to any unit, because the export stamped whole runs with one time until 9 November. A fresh agent per batch: batch A cost $25.72 for 8 points ($3.22 a point; 32% of the cost in long prompts). Batch B cost $23.08 for 5 points ($4.62 a point) counting the run that prepared its units, or $12.98 ($2.60 a point) for its delivery run alone, where long prompts were still 72% of the cost. Coordinator usage ($82.54 across all batches) is outside these figures, and batch C waits on an export past 11:41 GMT on 2026-11-10. The samples are small (8 and 5 points).

The data is in `sdlc-studio/change-requests/evidence/consumer-sprint-cost-2026-11-10.tar.gz`: per-request and per-unit CSVs, batch summaries, and the time windows and script that built them (the script imports a pricing module the bundle does not include). It is a scrubbed copy of the bundle supplied (SHA-256 fc960de33f14a39f; the copy 1d814234b30c426f): the project's repository name, two other project names, the operator's name and two local paths were replaced, and every figure is unchanged. The 56% that no unit carries is this bug's gap seen from a consuming project.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-10 | Darren Benson (operator) | Filed |
| 2026-11-10 | Darren Benson (operator) | Evidence: a consuming project's batch cost figures |
| 2026-11-12 | Claude Opus 5.5 (run eleven orchestrator) | Groomed for run eleven (D0469, D0470): criteria rewritten with runnable Verify lines on the at-HEAD triage's evidence |
| 2026-11-12 | Claude Opus 5.5 (run eleven orchestrator) | Mid-run ruling (D0467's pattern): AC2 reaches two tests outside the Affects whose assertions contradict it (CostIssueHandOverTests, KnownIssuesTests); both join the Affects, each changed only as far as AC2 requires |
