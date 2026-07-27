# US0494: The gate selects the tests a change can reach from the import graph, reporting what it excluded and falling back to everything when it cannot resolve

> **Status:** Ready
> **Delivers:** CR0451
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/repo_map.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Epic:** EP0177
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** developer changing one script
**I want** the gate to run the tests that change can reach, not all 4,624
**So that** the cost of a commit is proportional to what it risks rather than to the size of the whole repository

## Acceptance Criteria

### AC1: the selected set is derived from the import graph

- **Given** a change to a single module and the repo map's import index
- **When** the gate selects tests
- **Then** it runs the tests reachable from that module and its dependents, and the selection is derived from the index rather than a hand-written map
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::TestSelectionTests::test_selection_comes_from_the_import_graph

### AC2: what was excluded is reported

- **Given** a selected run
- **When** it completes
- **Then** it names how many tests it skipped and why, so a reader sees a judgement was made rather than assuming everything ran
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::TestSelectionTests::test_a_selected_run_reports_what_it_excluded

### AC3: an unresolvable change falls back to everything

- **Given** a changed file whose dependents cannot be resolved from the index
- **When** the gate selects
- **Then** it runs the whole suite and says why, because the safe direction of a selection failure is more testing, never less
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::TestSelectionTests::test_an_unresolvable_change_runs_everything

### AC4: selection never silently reduces coverage below the boundary run

- **Given** a selected run and the boundary policy
- **When** both are consulted
- **Then** the boundary still runs the full suite, so selection trades WHEN coverage is paid, never WHETHER
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::TestSelectionTests::test_selection_does_not_replace_the_boundary_run

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the operator's two policy rules |
