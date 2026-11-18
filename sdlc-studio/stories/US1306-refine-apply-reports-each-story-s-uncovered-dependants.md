# US1306: `refine apply` reports each story's uncovered dependants and near-duplicate symbols without changing its exit code or output, and says when the map is absent or stale

> **Status:** Draft
> **Depends on:** US1305
> **Risk-class:** elevated
> **Delivers:** CR0735
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/help/refine.md, .claude/skills/sdlc-studio/scripts/tests/test_refine_impact.py, changelog.d/US1306.md
> **Epic:** EP0372
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** `refine apply` reports each story's uncovered dependants and near-duplicate symbols without changing its exit code or output, and says when the map is absent or stale
**So that** CR0735 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Refine names each story's uncovered dependants

- **Given** a built map and a breakdown whose story changes `pkg/a.py`, which `pkg/b.py` and `pkg/c.py` import, with `pkg/b.py` in a second story's Affects
- **When** `refine.py apply --dry-run` and then `apply` are run
- **Then** both print, under the first story, `pkg/c.py` as a dependant no story covers, and do not list `pkg/b.py`. Fails on: a covered dependant listed, or the report printed by one of dry-run and apply only
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_impact.py::ImpactTests::test_each_story_lists_the_dependants_no_story_covers

### AC2: Refine names near-duplicates of what a story changes

- **Given** a module outside the breakdown that is a near-duplicate of `pkg/a.py` by the map's rule
- **When** `refine.py apply --dry-run` is run
- **Then** it names that module under the story, asking which one is meant. Fails on: a near-duplicate inside the same story's Affects reported against itself
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_impact.py::ImpactTests::test_a_near_duplicate_module_is_named_under_the_story

### AC3: The report is advice and changes nothing (D0516)

- **Given** the same breakdown with the map present, and again with no map
- **When** `refine.py apply` is run in two fresh copies of the fixture
- **Then** the exit code and every story file written are the same in both, and the run without a map prints one line saying impact was not checked and why. Fails on: a refusal, a changed story, or silence when the map is missing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_impact.py::AdviceTests::test_the_report_never_changes_the_exit_or_the_stories

## Notes

- Reconcile flagged this as possibly delivered by US1152 (shared refine files and title words); it is not: US1152 stamps a risk class and reads no import graph.
- Cost: one map query per story; the map is read, never rebuilt, by refine.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-17 | Claude Opus 5.5 (grooming) | Groomed: authored criteria with Verify lines, Affects corrected to the skill's test folder and this unit's fragment, notes |
