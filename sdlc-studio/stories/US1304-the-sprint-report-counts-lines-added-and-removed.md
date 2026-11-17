# US1304: The sprint report counts lines added and removed in the batch's declared files over a named commit range, and states priced cost per delivered line beside cost per point

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0734
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report_cost_per_line.py, changelog.d/US1304.md
> **Epic:** EP0371
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The sprint report counts lines added and removed in the batch's declared files over a named commit range, and states priced cost per delivered line beside cost per point
**So that** CR0734 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Lines are counted only in the batch's declared files over a named range

- **Given** a throwaway repo with a run whose base ref and verified commit differ by commits touching a declared source file, an undeclared file, a file under `sdlc-studio/` and a changelog fragment
- **When** the sprint report is built
- **Then** it states lines added and removed in the declared source file only, names the range as `<base>..<verified>`, and names the two excluded path classes. Fails on: lines from an undeclared file, an artefact or a fragment counted, or a range the reader cannot re-run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report_cost_per_line.py::CountTests::test_only_declared_source_lines_over_the_named_range_are_counted

### AC2: Dollars per delivered line sits beside dollars per point

- **Given** the same run with a priced cost
- **When** the sprint report is built
- **Then** a Dollars per delivered line row (cost over added plus removed lines) appears beside Dollars per point, and `help/sprint.md` says what it counts. Fails on: a figure over added lines alone while the help says both, or a row placed away from the per-point figure
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report_cost_per_line.py::RateTests::test_dollars_per_delivered_line_is_printed_beside_dollars_per_point

### AC3: No cost or no lines omits the figure with a reason

- **Given** one run with no priced cost and another whose declared files changed no lines
- **When** each report is built
- **Then** neither prints a per-line figure, and each says why. Fails on: `$0.00` per line, or a division error
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report_cost_per_line.py::RateTests::test_the_figure_is_omitted_with_a_reason_when_it_cannot_be_computed

## Notes

- The run state holds the base ref (`run_state.base_ref`) and the close stamps `verified_sha`; count with `git diff --numstat` over that range, never `git log` since a date.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-17 | Claude Opus 5.5 (grooming) | Groomed: authored criteria with Verify lines, Affects corrected to the skill's test folder and this unit's fragment, notes |
