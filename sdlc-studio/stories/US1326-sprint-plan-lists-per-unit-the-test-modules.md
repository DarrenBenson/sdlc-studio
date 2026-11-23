# US1326: sprint plan lists, per unit, the test modules outside its Affects that import or run a script its Affects names, as an advisory grooming list

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0749
> **Created:** 2026-11-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/US1326.md
> **Epic:** EP0378
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** sprint plan lists, per unit, the test modules outside its Affects that import or run a script its Affects names, as an advisory grooming list
**So that** CR0749 is delivered by work that can be planned and checked

## Acceptance Criteria

A "script" is a `.py` file the unit's `Affects` declares. The list is advice, gathered and printed the way `registry_advisories` is at plan: it changes no exit code, no batch and no grooming verdict.

### AC1: The plan lists each test module outside a unit's Affects that imports or runs a script it declares

- **Given** a git project whose tracked tree holds `scripts/tool.py` and, under `tests/`, `test_tool_import.py` (`import tool`), `test_tool_from.py` (`from tool import run`), `test_tool_cli.py` (runs `scripts/tool.py` through `subprocess`) and `test_toolkit.py` (`import toolkit`), with a Ready story `US0001` whose `Affects` names `scripts/tool.py`
- **When** `sprint.py plan --stories Ready --no-fetch --skip-personas` runs
- **Then** it exits 0 and prints, once, a two-space-indented header holding `Test modules outside` and `(advisory - nothing is refused)`, followed by the one four-space-indented line `US0001: scripts/tool.py -> tests/test_tool_cli.py, tests/test_tool_from.py, tests/test_tool_import.py`, its modules sorted, and `test_toolkit.py` appears nowhere in the block. Fails on: no such block, which is the plan at HEAD; a substring match that lists `test_toolkit.py` for `tool.py`; a scan that sees imports but not a script run by its path
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanTestModuleAdvisoryTests::test_the_plan_lists_test_modules_that_import_or_run_a_declared_script

### AC2: The list rides beside the registry advice and refuses nothing

- **Given** the AC1 project, once as it is and once with `sprint.affects_check: block` in `sdlc-studio/.config.yaml`
- **When** `sprint.py plan --stories Ready --no-fetch --skip-personas --format json` runs, and the human plan runs under `block`
- **Then** the JSON's `breakdown.test_advisories` is `[{"id": "US0001", "items": [{"script": "scripts/tool.py", "tests": ["tests/test_tool_cli.py", "tests/test_tool_from.py", "tests/test_tool_import.py"]}]}]` and `breakdown.affects_advisories` is `[]`, and the human plan under `block` exits 0 with the AC1 block printed and `US0001` still in the batch. Fails on: a list only the human render can see; the list put into `affects_advisories`, which `sprint.affects_check: block` refuses on, so advice becomes a refusal
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanTestModuleAdvisoryTests::test_the_list_rides_beside_the_registry_advice_and_refuses_nothing

### AC3: A test module the unit already declares is not listed

- **Given** the AC1 project with `US0001`'s `Affects` also naming `tests/test_tool_import.py`, and a second run where it names all three importing modules
- **When** the plan runs
- **Then** the first run's line is `US0001: scripts/tool.py -> tests/test_tool_cli.py, tests/test_tool_from.py`, and the second prints no line for `US0001` and no header. Fails on: a list that ignores the unit's own `Affects`, telling a groomed unit to add what it already holds; a header printed over an empty list
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanTestModuleAdvisoryTests::test_a_test_module_in_the_units_affects_is_not_listed

### AC4: A unit that declares no script, or a script no test reaches, prints nothing

- **Given** the AC1 tree with two Ready stories and no other: `US0002` whose `Affects` names only `docs/guide.md`, and `US0003` whose `Affects` names `scripts/lonely.py`, which no test module imports or runs
- **When** the plan runs, human and `--format json`
- **Then** the human plan prints no header and no line for either unit, and `breakdown.test_advisories` is `[]`. Fails on: a header printed for a batch with nothing to list; a line naming a unit with an empty module list; a markdown path treated as a script
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanTestModuleAdvisoryTests::test_a_unit_with_no_script_or_no_reaching_test_prints_nothing

### AC5: Only the project's own tracked test modules are read

- **Given** the AC1 project with a git worktree added under `.claude/worktrees/w1`, which holds its own copy of `tests/test_tool_import.py`, and an untracked `tests/test_scratch_tool.py` (`import tool`) in the main tree
- **When** the plan runs from the main tree
- **Then** the `US0001` line is exactly the AC1 line: no path under `.claude/worktrees/` and no `tests/test_scratch_tool.py`. Fails on: a filesystem walk; in this repository on 2026-11-23 one would read 15,599 `test_*.py` files on disk against 679 tracked, nearly all of them copies inside `.claude/worktrees/`, and list each copy
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanTestModuleAdvisoryTests::test_only_the_projects_own_tracked_test_modules_are_read

### AC6: A script many test modules reach is listed to a cap, with the rest counted

- **Given** the AC1 project with twelve further tracked modules `tests/test_tool_more_01.py` to `tests/test_tool_more_12.py`, each holding `import tool`, so fifteen modules reach `scripts/tool.py`
- **When** the plan runs, human and `--format json`
- **Then** the human `US0001` line names the first ten modules in sorted order and ends `, +5 more (--format json lists all)`, and the JSON item's `tests` holds all fifteen, sorted. Fails on: a human line naming all fifteen, which for a script like this repository's `sprint.py`, imported by about 210 test modules, is a list nobody reads; a JSON list cut to the cap; a count that is not the number left out
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanTestModuleAdvisoryTests::test_a_script_many_modules_reach_is_listed_to_a_cap

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three qa seat) | Groomed: authored five criteria with Verify lines, each premise run at HEAD 17dc7829; Affects widened to this unit's fragment |
