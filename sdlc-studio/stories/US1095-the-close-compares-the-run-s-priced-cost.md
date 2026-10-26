# US1095: The close compares the run's priced cost per point with the median of recent runs, or a configured baseline until three exist, and carries a run over 1.5 times it as a known issue with a per-unit breakdown, whose cause the retro must name

> **Status:** Ready
> **Delivers:** CR0651
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_close_cost_regression.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-retro.md, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, changelog.d/US1095.md, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/reference-scripts-surface.md
> **Epic:** EP0292
> **Points:** 5
> **Depends on:** US1091, US1092
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, judging whether the process is earning its keep
**I want** a run that costs more than 1.5 times the recent median per point, or a configured baseline until three priced runs exist, named on the report as a known issue with a per-unit breakdown and a cause the retro must name
**So that** a cost regression is caught at the close that caused it, not discovered runs later, and the close still completes

## Acceptance Criteria

- **AC1:** Given VELOCITY.md with five rows carrying a priced-per-point figure (median M) and an open run whose priced cost per gate-cleared point is 1.6 x M, when `sprint.py close --retro <id> --goal-verdict achieved --note <text>` runs, then the run state's close known issues hold one `cost` issue naming the run's figure, M, the ratio and the retros M was taken from, with each batch unit's priced span cost (NOT MEASURED where it has none) and the run's unattributed remainder, and the close files the report as it does with any other known issue
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_cost_regression.py::CloseCostRegressionTests::test_a_run_over_one_and_a_half_times_the_median_is_a_known_issue
- **AC2:** Given a run at exactly 1.5 x M, no cost issue is recorded; a VELOCITY row whose priced cell is absent is not counted towards the median and is never read as 0
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_cost_regression.py::CloseCostRegressionTests::test_the_boundary_and_an_absent_cell_record_no_issue
- **AC3:** Given a run carrying the cost issue, `retro.py validate --id <retro>` refuses a retro with no `## Cost` section holding at least one bullet that is not a template placeholder, naming the section, and accepts it once it holds one; a retro for a run with no cost issue is not asked for the section
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_cost_regression.py::RetroCostCauseTests::test_the_retro_must_name_the_cause_of_a_flagged_run
- **AC4:** Given the same history, when `sprint.py plan <batch> --sprint-goal <goal>` previews the run, then it prints the batch's cost budget, its points x 1.5 x M priced tokens, with M and the retros it came from, beside the token forecast; with fewer than three priced runs it prints the budget from the configured baseline and names it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_cost_regression.py::PlanBudgetTests::test_the_plan_prints_the_budget_and_its_basis
- **AC5:** Given fewer than three priced runs (VELOCITY rows and baseline rows together), when the close runs, then it compares against `cost.baseline_per_point` from the project config, whose shipped default in `templates/config-defaults.yaml` is this repository's measured figure, and the comparison names the configured baseline as its basis; with the key set to `off` it prints UNMEASURED, naming how many priced runs it has and that three are needed, and records no cost issue
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_cost_regression.py::CloseCostBaselineTests::test_fewer_than_three_runs_use_the_configured_baseline
- **AC6:** Given transcripts covering a past run's window, when `retro.py cost-baseline add --retro <id> --since <iso> --until <iso>` runs, then it derives the window's priced cost with US1091's reader and appends one row to `sdlc-studio/retros/COST-BASELINE.md` naming the retro, the window, the points, the priced cost per point and the weights used; VELOCITY.md is byte-for-byte unchanged; the trailing median reads baseline rows beside VELOCITY's priced rows; a window holding no transcript record is refused and nothing is written
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_cost_regression.py::CostBaselineSeedTests::test_a_seeded_run_joins_the_median_and_velocity_is_untouched

## Notes

- Serves: Maya Okafor, End goal 3.
- AC1 must fail on: the close refusing; raw tokens compared instead of priced; the mean taken for the median; the current run included in its own baseline
- AC2 must fail on: `>=` in place of `>`; an absent priced cell read as 0
- AC3 must fail on: the section demanded of every retro; a `{{placeholder}}` bullet accepted; the demand read from the retro's own text rather than from the run's recorded known issues
- AC4 must fail on: the budget derived from the forecast's tokens-per-point rate, which is a different basis; a budget printed with no M or rows beside it
- AC5 must fail on: the default typed in sprint.py beside the config file; a median taken over one or two rows; the baseline used without being named
- AC6 must fail on: a VELOCITY row rewritten; the window priced by a second summing loop beside the meter's; an empty window written as 0
- D0390 (3): once this lands, record RETRO0133-RETRO0135 with `retro.py cost-baseline add`, and set the shipped default from those rows.
- Overlap: id: CR0651; relation: parent change request (D0389); evidence: Recommendation: 'E4 the close flags a run over 1.5 times the trailing median cost per point as a known issue, with a per-unit breakdown, and the retro names the cause'
- Overlap: id: US1000; relation: complementary: money on the report; E4 compares input-equivalent priced tokens and needs no prices; evidence: Title: 'The cost section states the run's cost in money from a pricing snapshot frozen at the close'
- Overlap: id: BG1065; relation: no overlap: a gate wall-time budget, not a run cost budget (run four, D0389 (3)); evidence: Title: 'The gate's 45-second cost budget is exceeded on every run'
- Risk: Where it lands: the close collects known issues in `cmd_close`'s `known` list (sprint.py ~9255-9331) and stamps `run_state.CLOSE_KNOWN_ISSUES` before `_file_the_report`; the report renders them in `sprint_report._known_issues_section` (~3865). The VELOCITY row is written by `retro.record_velocity` (retro.py:2673) from `_apply_signoff_tail`, and the retro's accuracy block, with the 'Sprint tokens/point' line, by `retro.py accuracy --write` (~1695). One baseline function in retro.py should serve the close, `validate` and the plan.
- Risk: Denominator: no unit is terminal until `sign` (D0213), so 'per point' at the close must be the gate-cleared points the report states as delivered, not points by status.
- Risk: Per-unit attribution comes from unit spans (`start_tokens` on `record_unit_actual`). Concurrent builders overlap spans, so the unit costs can sum past the run total; the remainder must be clamped and say so, never reported negative.
- Risk: Check that the cost issue does not block `sprint.py boundary` or `sign` (sprint.py ~10673 refuses on unresolved close known issues); D0389 says the close completes and the issue is handed over.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-26 | sdlc | Affects gains `sprint_report.py` (`NON_CEREMONY_VERBS` declares retro cost-baseline as mechanics) and reference-scripts-surface.md (regenerated for the new verb); AC6's new verb needs both, as US1088's did |
