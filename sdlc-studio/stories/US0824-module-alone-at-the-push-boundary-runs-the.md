# US0824: module-alone at the push boundary runs the changed modules and everything that imports them

> **Status:** Superseded
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), SUPERSEDED
> **Delivers:** CR0586
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Epic:** EP0253
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** module-alone at the push boundary runs the changed modules and everything that imports them
**So that** CR0586 is delivered by work that can be planned and checked

## Acceptance Criteria

The selection must be judged against the defect the lane exists for: `test_critic` was red alone because a SIBLING imported a name first, and `test_critic` has no import edge to that sibling. A test-module-to-test-module graph would never select it. The graph is therefore test module to PRODUCTION module, transitively, and the criteria say so (stakeholder consult 2026-09-16, all three personas).

### AC1: the selection is built from US0843's measured census, not from an import graph this codebase does not have

- **Given** US0843's census, in which 103 of 133 test modules reach production code through `importlib.util.spec_from_file_location` on a runtime path and only 27 resolve through a static import
- **When** the lane selects for a push changing `lib/sdlc_md.py`
- **Then** a module is selected when ANY of its recorded routes reaches a changed file - static import, runtime spec load, or subprocess - and the lane's line names how many modules each route contributed
- **Mutant:** select by static import closure alone, transitive or not - it matches 27 of 133 modules here, so the narrowing would skip the 106 that reach production another way while reporting a clean selection
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ModuleAloneSelectionTests::test_selection_uses_every_route_the_census_records

### AC1b: a module that reaches production only by subprocess is always selected, because no import edge can find it

- **Given** the 19 test modules that drive production code through `subprocess` alone and import no production module at any depth - `test_rehearse_release` (the serial_only module), `test_conformance`, `test_changelog`, `test_mutation`, `test_cli_grammar` and the rest of that set
- **When** the lane selects for any push
- **Then** every module in that set runs regardless of the diff, the set is DERIVED by scanning for a subprocess invocation of a production path rather than listed by hand, and the lane's line names how many were included for that reason
- **Mutant:** select by import closure alone - those 19 become unselectable by any diff, the lane silently exempts the modules guarding conformance, changelog and mutation, and the founding defect class (a name present only because a sibling imported it) is exactly the kind that leaves no edge to find
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ModuleAloneSelectionTests::test_subprocess_only_modules_are_always_selected

### AC2: the base ref is the merge-base with origin/main, and it is named in the lane's line

- **Given** a working branch whose main has moved since the local commits were written
- **When** the lane selects
- **Then** the diff base is `git merge-base HEAD origin/main`, the lane's line names that sha, and a push whose base cannot be resolved runs the FULL sweep rather than a guess
- **Mutant:** diff against `HEAD~1` - with concurrent authors a helper change and the module that depends on it land in separate pushes and are covered by neither selection
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ModuleAloneSelectionTests::test_base_ref_is_the_merge_base_and_an_unresolvable_base_runs_everything

### AC3: the release boundary still runs all 133

- **Given** `gate.py --boundary release`, which shares `at_boundary` with the push boundary (gate.py:3881)
- **When** the lane runs
- **Then** every module runs regardless of the diff, and the lane's line says the selection was not applied at this boundary
- **Mutant:** let `at_boundary` carry the narrowing to both - a tag cut then ships on a narrowed lane to save nine minutes on an operation that happens monthly
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ModuleAloneSelectionTests::test_release_boundary_runs_every_module

### AC4: the saving is measured on the push itself, not on a median that cannot move inside the run

- **Given** `gate_timing.py estimate --suite boundary-push` reads 726s as the MEDIAN of the last ten boundary runs (tools/gate_timing.py:194, HISTORY = 10), so six post-landing pushes would be needed before that command could read under 300
- **When** the narrowed lane lands and a push touching one production file runs the boundary gate
- **Then** the figure judged is THAT push's own recorded boundary-gate wall clock, taken from the run it wrote to `gate-timings.json`, before and after, quoted in this story's Revision History - and the story is not Done while the after figure is at or above 300s
- **Mutant:** judge the story on `gate_timing estimate`'s median - nine pre-change runs sit in its window, so a delivery that genuinely halved the gate reports failure, and one that changed nothing reports success six pushes later
- **Verify:** manual - the two single-run boundary-gate figures, before and after, quoted in this story's Revision History with their run timestamps

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-18 | goal review round 2 | AC1 rebuilt on US0843's census: 103 of 133 test modules reach production through `spec_from_file_location` on a runtime path and only 27 through a static import, so an import closure would have exempted 106 modules while reporting a clean selection. AC4 now judges the push's OWN recorded figure - `gate_timing estimate` is a ten-run MEDIAN (gate_timing.py:194), so it could not move inside the run. |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): SUPERSEDED - US0881 |
