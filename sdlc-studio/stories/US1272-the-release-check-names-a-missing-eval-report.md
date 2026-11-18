# US1272: The release check names a missing eval report for the version being cut

> **Status:** Draft
> **Risk-class:** elevated
> **Delivers:** CR0718
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/release_cut.py, tools/eval_run.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py, tools/tests/test_eval_run.py
> **Epic:** EP0357
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The release check names a missing eval report for the version being cut
**So that** CR0718 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A missing eval report refuses the tag by name

- **Given** a project that holds scenario files under `evals/scenarios/`, a release gate recorded green on the commit, and no results file under `evals/.results/` for the version being cut
- **When** `release_cut.py tag-check` runs for that commit and version
- **Then** it exits 2 and its message names the version, the results path it looked for and the `eval_run.py report --run <version>` step that is owed. Fails on: a tag check that passes, or refuses without naming the eval report, when no run was ever recorded for the version
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::EvalReportTagCheckTests::test_a_missing_eval_report_refuses_the_tag_by_name

### AC2: A recorded report lets the tag through

- **Given** the same project with a results file for the version being cut under `evals/.results/`
- **When** `release_cut.py tag-check` runs for that commit and version
- **Then** the eval report is no longer a reason to refuse, and the check's message says an eval report was found for the version. Fails on: a check that refuses every tag once the eval step is wired in, or that accepts a results file recorded under another version's label
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::EvalReportTagCheckTests::test_a_recorded_report_for_the_version_is_accepted

### AC3: A project with no eval scenarios is not asked for a report

- **Given** a consuming project with no `evals/scenarios/` directory and a release gate recorded green on the commit
- **When** `release_cut.py tag-check` runs for that commit
- **Then** the tag is judged as it is today, with no mention of an eval report. Fails on: the shipped release check refusing every project that never had eval scenarios
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::EvalReportTagCheckTests::test_a_project_without_scenarios_is_not_asked_for_a_report

### AC4: The release check looks where `eval_run.py record` writes

- **Given** a fixture repository where `tools/eval_run.py record --run <version>` has recorded one verdict, and a second fixture where nothing was recorded
- **When** the release check's eval report lookup runs for that version in each
- **Then** it finds the report in the first and reports it absent in the second, reading the same path `record` wrote. Fails on: a lookup that reads a path or a label form `record` never writes, so a real run is reported missing
- **Verify:** pytest tools/tests/test_eval_run.py::ReleaseReportPresenceTests::test_the_release_check_finds_a_recorded_run_and_misses_an_absent_one

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
