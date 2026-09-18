# US0837: the report opens with the sprint goal verbatim and carries DORA's four keys with this project's mapping stated

> **Status:** Draft
> **Delivers:** RFC0059
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0255
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** the report opens with the sprint goal verbatim and carries DORA's four keys with this project's mapping stated
**So that** RFC0059 is delivered by work that can be planned and checked

## Acceptance Criteria

The report is FILEABLE: it opens with the goal and closes with a signature block, which is what
makes it a document somebody senior reads rather than a terminal dump. The goal leads because
quoting it verbatim at the top of such a document is what exposed RUN-01M2JA6J's goal as a
shopping list of unit ids rather than a statement of value, and that became CR0587. A goal
nobody re-reads is a goal nobody corrects, so any trimming, reflow or summarising defeats the
section's only purpose.

DORA's four keys carry the project's own mapping beside each figure for the same reason the
model is named beside the cost: a figure whose definition is unstated cannot be compared with
anyone else's, and printing an unmeasured key as `0%` against an elite band of 0-15% reads as
the best possible result. THE GOAL is a multi-line string carrying unit ids, a semicolon list
and a parenthesis, so a renderer that reflows or truncates is caught by the comparison rather
than by a claim about how it renders.

### AC1: the goal is the first content of the report and is byte-identical to the one recorded

- **Given** a run whose `sprint_goal` is THE GOAL
- **When** the report JSON, the Markdown twin and the HTML rendering are produced
- **Then** in all three the goal appears before any figure, and the string compares EQUAL to `run_state.read(root)["sprint_goal"]` - no truncation, no ellipsis, no reflow, no first-sentence trim; and the goal verdict and its note follow the goal rather than standing in for it
- **Mutant:** render the goal through the first-sentence trim the status line uses - a goal that is a shopping list then reads as one tidy line, the defect a verbatim quote exposes is hidden again, and the section is still present and still labelled the sprint goal
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TheGoalLeadsTests::test_the_goal_is_first_and_verbatim_in_all_three_renderings
- **Verified:** yes (2026-09-18)

### AC2: an unjudged goal reads NOT MEASURED, and a run with no goal refuses

- **Given** two runs: one carrying THE GOAL with no recorded `sprint_goal_verdict`, one carrying no sprint goal at all
- **When** the report is built on each
- **Then** the first exits 0, still leads with THE GOAL verbatim, and its verdict reads `NOT MEASURED` with the reason `no goal verdict recorded on this run`; the second exits 2 naming the missing goal, because a report cannot invent what the run aimed at, and writes nothing
- **Mutant:** default the verdict to `achieved` when none is recorded - the run's own account then judges itself, and every reader of the report sees a verdict nobody gave
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TheGoalLeadsTests::test_an_unjudged_goal_reads_not_measured_and_a_goalless_run_refuses
- **Verified:** yes (2026-09-18)

### AC3: each DORA key states this project's mapping, and a key with no source reads NOT MEASURED

- **Given** a fixture whose git history holds three pushes to main across the run window and no release tag, and which has no forge access, so no CI run data can be read
- **When** the DORA section is built
- **Then** each of the four keys carries `value`, `mapping` - the sentence stating what this project counts, such as a deployment being a push to main - `source` and the elite band; deployment frequency reads 3 sourced to the git history; change failure rate and time to restore, which need CI runs, read `NOT MEASURED` with `no forge run data` rather than `0%` and `0h`
- **Mutant:** print the four keys and their elite bands with no mapping sentence - the report then asserts a comparison against an industry band on definitions nobody stated, and the two unmeasured keys read as elite performance
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::TheDoraKeysTests::test_each_key_states_its_mapping_and_an_unsourced_key_reads_not_measured
- **Verified:** yes (2026-09-18)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | render the goal through the first-sentence trim the status line uses - a goal that is a shopping list then reads as one tidy line, the defect a verbatim quote exposes is hidden again, and the section is still present and still labelled the sprint goal | the goal is the first content of the report and is byte-identical to the one recorded |
| AC2 | default the verdict to `achieved` when none is recorded - the run's own account then judges itself, and every reader of the report sees a verdict nobody gave | an unjudged goal reads NOT MEASURED, and a run with no goal refuses |
| AC3 | print the four keys and their elite bands with no mapping sentence - the report then asserts a comparison against an industry band on definitions nobody stated, and the two unmeasured keys read as elite performance | each DORA key states this project's mapping, and a key with no source reads NOT MEASURED |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-17 | grooming 2026-09-17 | Groomed: three criteria. The goal is compared byte-for-byte against the recorded string over a multi-line goal, so a reflow or first-sentence trim fails; an unjudged goal reads NOT MEASURED and a goalless run refuses; each DORA key carries its mapping and an unsourced key reads NOT MEASURED rather than 0%. |
