# US0824: module-alone at the push boundary runs the changed modules and everything that imports them

> **Status:** Draft
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

### AC1: the selection is the changed modules plus every test module reaching a changed file transitively

- **Given** a push whose diff against the merge-base with `origin/main` changes `lib/sdlc_md.py` alone
- **When** the module-alone lane selects
- **Then** it selects every test module whose import closure reaches `lib/sdlc_md.py`, not only those naming it directly, and the closure is computed over PRODUCTION modules rather than test-to-test edges
- **Mutant:** walk test-module imports only - `test_critic`'s founding case is then never selected, and the lane keeps its name while losing its yield
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ModuleAloneSelectionTests::test_selection_follows_production_imports_transitively

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

### AC4: the PUSH GATE's own figure is recorded before and after, and it is the figure the story is judged on

- **Given** `python3 tools/gate_timing.py estimate --suite boundary-push`, which reports the gate's measured wall clock from its recorded runs - 726s at the time of writing, of which module-alone was 551s on the run that measured it
- **When** the narrowed lane has landed and a push has run the boundary gate
- **Then** both the before and after figures come from THAT command, not from `module-alone-timings.json`, they are recorded in this story's Revision History, and the story is not Done while the after figure is at or above 300s
- **Mutant:** judge the story on the LANE's own timings file - a delivery can then record a truthful 80% saving on a four-minute lane while the push it was raised to shorten is still over ten minutes, which is a criterion's words outrunning its fixture in the one story written to prevent exactly that
- **Verify:** manual - the two `gate_timing.py estimate --suite boundary-push` figures, before and after, quoted in this story's Revision History

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
