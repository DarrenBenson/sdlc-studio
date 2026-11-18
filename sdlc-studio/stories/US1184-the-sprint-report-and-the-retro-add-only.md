# US1184: The sprint report and the retro add only the delegated totals the meter cannot see, and name what they added

> **Status:** Draft
> **Risk-class:** elevated
> **Delivers:** CR0653
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_delegated_unseen_totals.py
> **Epic:** EP0322
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The sprint report and the retro add only the delegated totals the meter cannot see, and name what they added
**So that** CR0653 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The report adds only the totals the meter cannot see, and names them

- **Given** a closed run whose stamps say the readings hold the subagent transcripts, with one delegated record marked seen and one marked unseen
- **When** `sprint_report.py` composes the run's page
- **Then** the Tokens actual is the meter plus the unseen total only, and its basis names the total added and its agent count, and the total left out as already in the reading. Fails on: both totals dropped, as the per-session flag does today, or both added
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_delegated_unseen_totals.py::DelegatedUnseenTotalsTests::test_the_report_adds_only_the_unseen_total_and_names_it

### AC2: The retro states the same figure for the same run

- **Given** the same run
- **When** `retro.py accuracy` captures its actual
- **Then** its token total and its supplied figure equal the report's, and its basis sentence names what was added and what was not. Fails on: the retro and the report publishing two totals for one run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_delegated_unseen_totals.py::DelegatedUnseenTotalsTests::test_the_retro_states_the_figure_the_report_states

### AC3: Records that make no claim are added or left out as they are today

- **Given** a run whose delegated records carry no statement of visibility, once under stamps that hold the subagent transcripts and once under stamps that do not; and a record marked seen under a meter that did not read subagents
- **When** the report is composed for each
- **Then** the unstated totals are left out in the first and added in the second, exactly the figures the tree gives now, and the seen record is still added where the meter read no subagent. Fails on: a page filed before this change re-deriving to a different total
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_delegated_unseen_totals.py::DelegatedUnseenTotalsTests::test_unstated_records_keep_the_figures_filed_pages_carry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
