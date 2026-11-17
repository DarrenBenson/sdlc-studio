# US1255: At plan time a unit's files are matched to the failure classes, and only matches reach its briefs, capped

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0706
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_failure_class_file_match.py
> **Epic:** EP0346
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** At plan time a unit's files are matched to the failure classes, and only matches reach its briefs, capped
**So that** CR0706 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The plan matches each unit's files to the classes that name them

- **Given** a store holding an active class that carries `files` and a batch of two units, one whose Affects names one of those files and one whose Affects names none
- **When** `sprint.py plan --format json` is run over the batch
- **Then** the plan records the class's code against the first unit and against no other, by the same path normalisation `Affects` is read with (a leading `./` or surrounding whitespace does not hide a match). Fails on: a class matched to every unit in the batch, or a match missed because the two paths were spelled differently
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_failure_class_file_match.py::PlanMatchTests::test_the_plan_records_a_class_only_against_the_unit_whose_files_it_names

### AC2: Only a matching class reaches a unit's build and review briefs

- **Given** the same store and batch, planned
- **When** `sprint.py lane brief` and `critic.py brief` are run for each of the two units
- **Then** the matching unit's build brief and review brief each carry the class's rule and behaviour, and the other unit's briefs do not name the class at all. A class that carries no `files` is general and is injected as it is today, so both units' briefs still carry it. Fails on: a file-scoped class printed in the brief of a unit that touches none of its files, or a class with no files dropped from every brief
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_failure_class_file_match.py::BriefMatchTests::test_a_file_scoped_class_reaches_only_the_matching_units_briefs

### AC3: The matched classes in one brief are held to a token cap

- **Given** a unit whose Affects matches more classes than fit under the cap the brief states for its lessons block
- **When** its build brief and its review brief are printed
- **Then** the lessons block stays at or under the cap, keeps the most-repeated classes first, and says how many matching classes it left out; with the matches under the cap, all of them are printed and no left-out count appears. Fails on: a block over the cap, a quiet class kept ahead of a repeated one, or classes dropped without the count
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_failure_class_file_match.py::BriefCapTests::test_matches_over_the_cap_are_cut_quietest_first_and_counted

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
