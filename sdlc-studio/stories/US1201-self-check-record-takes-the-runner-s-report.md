# US1201: Self-check record takes the runner's report and mutant list, and the author brief names the runner command

> **Status:** Done
> **Risk-class:** high
> **Delivers:** CR0673
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-agent-prompt-template.md, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py, sdlc-studio/reviews/command-audit.md, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, changelog.d/US1201.md
> **Epic:** EP0327
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Self-check record takes the runner's report and mutant list, and the author brief names the runner command
**So that** CR0673 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The record takes the runner's report and keeps the mutant list

- **Given** a unit and the report the mutation runner wrote for it: three mutants, all killed
- **When** `critic.py self-check record --unit <id> --claims <file> --mutants-from <report>` is run
- **Then** the row's mutant counts equal the report's, and the full list (each mutant's file, old, new, test and verdict) is kept with the row where `critic.py brief` can read it; a record made with `--mutants` and no report still succeeds. Fails on: a record that keeps only the counts, so the brief cannot say which mutants the author ran
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_the_runners_report_is_recorded_with_its_full_mutant_list
- **Verified:** yes (2026-11-19)

### AC2: A survivor with no answer is refused

- **Given** a runner report with one survivor, handed in once with no answer for it and once with one
- **When** `critic.py self-check record --mutants-from <report>` is run for each
- **Then** the first is refused, naming the survivor, and writes nothing; the second is recorded with the answer beside the survivor; a report whose mutant names a test outside the unit's Affects is refused as `--mutants` refuses it. Fails on: an unanswered survivor recorded and so reaching review as though the author had ruled on it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_a_report_with_an_unanswered_survivor_is_refused
- **Verified:** yes (2026-11-19)

### AC3: The author's brief prints the runner command for the unit's Verify selectors

- **Given** a unit whose criteria carry two pytest Verify selectors
- **When** its author self-check section is printed by `sprint.py lane brief`, and `reference-sprint-toolchain.md` and `reference-agent-prompt-template.md` are read
- **Then** the section prints the runner command with the unit's id and its Verify selectors and the `--mutants-from` record command, and no longer asks for hand-chosen mutants as the only route; the runbook's mutation row and the prompt template name the same command, which the `mutation.py` parser accepts. Fails on: a brief that still tells the author to choose and apply mutants by hand, or pages naming a command the parser refuses
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_the_author_brief_names_the_runner_command_for_the_units_selectors
- **Verified:** yes (2026-11-19)

### AC4: Lane land records the self-check through the runner's report

- **Given** a builder's hand-in holding the runner's report for the unit in place of a hand-written `<id>-mutants.json`, and a second hand-in holding only `<id>-mutants.json`
- **When** `sprint.py lane land` records each unit's self-check
- **Then** the first is recorded through `--mutants-from` that report, so the row keeps the full list (AC1) and an unanswered survivor refuses the land's record as AC2 does; the second records as it does today; and `sprint.py lane brief` tells the builder to hand in the runner's report under the name lane land reads. Fails on: lane land passing the report to `--mutants`, ignoring it and recording no mutants, or a brief naming a hand-in file lane land does not read
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_lane_land_records_through_the_runners_report
- **Verified:** yes (2026-11-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
