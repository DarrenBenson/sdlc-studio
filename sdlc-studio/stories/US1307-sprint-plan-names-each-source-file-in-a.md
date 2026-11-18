# US1307: `sprint plan` names each source file in a unit's Affects that no test reaches within one hop, never reporting a file the unit creates

> **Status:** Draft
> **Depends on:** US1305
> **Risk-class:** high
> **Delivers:** CR0736
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/repo_map.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_unpinned_code.py, changelog.d/US1307.md
> **Epic:** EP0373
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** `sprint plan` names each source file in a unit's Affects that no test reaches within one hop, never reporting a file the unit creates
**So that** CR0736 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Plan names the files no test reaches

- **Given** a fixture with a built map, where `src/a.py` is imported by a test file, `src/b.py` is imported only by `src/a.py`, `src/c.py` is reached by no test, and a unit's Affects lists all three plus `docs/x.md`
- **When** `sprint.py plan` is run on that unit
- **Then** it names `src/c.py` as unpinned and not `src/a.py` (direct) or `src/b.py` (one hop through a module a test imports), and does not report `docs/x.md`. Fails on: a one-hop file reported, a non-source file reported, or `src/c.py` missed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_unpinned_code.py::UnpinnedTests::test_plan_names_source_files_no_test_reaches_within_one_hop

### AC2: A file the unit creates is never unpinned

- **Given** a unit whose Affects names a source file that does not exist yet
- **When** `sprint.py plan` is run
- **Then** that file is not reported. Fails on: every new file reported, so a greenfield unit always warns
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_unpinned_code.py::UnpinnedTests::test_a_file_the_unit_creates_is_not_reported

### AC3: No map means not checked, said once

- **Given** the same fixture with no map built
- **When** `sprint.py plan` is run
- **Then** it says the check was not run and names `repo_map.py build`, and plans the batch. Fails on: silence read as nothing unpinned, or a refusal because the map is absent
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_unpinned_code.py::UnpinnedTests::test_no_map_says_the_check_did_not_run

## Notes

- A test file is one the project's test layout names (`test_*.py`, `*_test.py`, `*.test.ts`, `*.spec.ts`, or under a `tests/` folder); state the rule where the warning is documented.
- `sprint.py` is large; put the check in a helper the plan calls, not inline in `cmd_plan`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-17 | Claude Opus 5.5 (grooming) | Groomed: authored criteria with Verify lines, Affects corrected to the skill's test folder and this unit's fragment, notes |
