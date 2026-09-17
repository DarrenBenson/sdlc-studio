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

### AC4: the push gate's cost after this change is measured against US0843's figures and recorded

- **Given** US0843's `module-alone-timings.json` from before this change
- **When** the narrowed lane runs on a push touching one test module's production file
- **Then** the delivery records both figures in this story's Revision History, and the story is not Done while the narrowed push gate is within 10% of the full one
- **Mutant:** land the change with no figure - the epic can then be delivered in full and still leave a twelve-minute push, which is what the operator raised it for
- **Verify:** manual - two recorded figures from `sdlc-studio/.local/module-alone-timings.json`, before and after, in the Revision History

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
