# BG0758: command_audit._surface_module reuses whatever surface module the process already imported

> **Status:** Fixed
> **Verification depth:** functional (after a dev import surface, the fixture tree now resolves its own module and a tree with none reads unreadable; three mutants killed by the QA reviewer)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/command_audit.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_surface_module.py, .claude/skills/sdlc-studio/scripts/tests/test_command_audit.py, changelog.d/BG0758.md
> **Evidence:** US0895 review, RUN-01M39MC0: scratchpad u895r_leak.py and u895r_diag.jsonl
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`command_audit._surface_module` (`command_audit.py`:1072-1087) is documented to load the surface module of the skill tree it is judging, but it resolves any `surface` already in sys.modules. `test_docgen.py` puts scripts/lib on sys.path at import and caches `surface`, so any later in-process caller - the close checklist's doc-surface row, `sprint preflight` - judges a fixture tree with the dev repo's module and drops or misreads the doc-surface row. Reproduced under xdist (2 failed of 7303) and deterministically in one process after `import surface` (19 rows against 20). Same class as BG0559.

## Steps to Reproduce

1. In one Python process, `import surface` from the dev repo's scripts/lib. 2. Call sprint preflight's in-process checklist over a fixture skill tree with no scripts/lib. 3. The doc-surface row is missing; the CLI prints it as unreadable.

Re-run at 65cdf1ca on 2026-09-25, with a fixture skill tree whose `scripts/lib/surface.py` sets `MARK = 'fixture'`. In a fresh process `_surface_module(<fixture skill>)` returns the fixture's module. After `import surface` from the dev repo's lib, the same call returns the dev repo's module.

## Proposed Fix

Load the tree's own surface module by path under a unique module name, never through sys.modules, and report unreadable when the tree has none.

## Acceptance Criteria

- [ ] **AC1** Given a process that has already imported the dev repo's `surface`, when `_surface_module` is asked for a fixture skill tree with its own `scripts/lib/surface.py`, then it returns the fixture's module, and `sys.modules["surface"]` still holds the dev module afterwards. Fails on: HEAD's `import surface`, which returns the cached dev module (measured); popping `sys.modules["surface"]` and re-importing, which returns the fixture's module but leaves it cached for the next caller.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_surface_module.py::SurfaceModuleTests::test_the_judged_trees_own_surface_module_is_loaded_whatever_is_cached
  - **Verified:** yes (2026-09-25)
- [ ] **AC2** Given a process that has already imported the dev repo's `surface`, when `command_audit.verb_coverage` runs over a fixture tree with no `scripts/lib/surface.py`, then it reports the surface as unreadable rather than counting the dev repo's verbs. The close checklist's in-process doc-surface row reads the same as the CLI's. Fails on: falling back to `sys.modules["surface"]` when the tree has none, which is HEAD's behaviour.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_surface_module.py::SurfaceModuleTests::test_a_tree_with_no_surface_module_reads_unreadable_in_process
  - **Verified:** yes (2026-09-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
| 2026-09-25 | QA seat | Groomed for Sprint 4: still real (after a dev `import surface`, `_surface_module` returns the dev module for a fixture tree that has its own); criteria rewritten Given/When/Then with executable Verify lines in a new test_lean module, each naming the wrong fix it fails on; 2 points stand |
