# BG0424: test selection dropped a script's own test module the moment that module measured any read path

> **Status:** Fixed
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** Found by delivering US0485: adding AC4's gate-wiring assertions (reading `.githooks/pre-commit` and `package.json`) turned both tests red. The measured read set for `test_command_audit.py` went from 0 paths to 2, and the selection for `command_audit.py` went from including it to not.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (delivering US0485); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z
> **Verification depth:** functional

## Summary

`gate.select_tests` reached a script's own test module by two routes: the import graph, and the statically measured read set of each suite module's source. Neither route reaches a script the family loads through `spec_from_file_location(name, dir / f"{name}.py")` - the f-string is unresolvable, so there is no import edge and no measured read. Those modules were selected only as a side effect of measuring EMPTY and being swept in wholesale as unattributable. Adding two ordinary path reads to such a test (a hook and package.json, for a lane-wiring assertion) took it out of the unattributable set, and with it out of the selection for changes to the script it tests - so a commit touching that script would have run every suite except its own. The naming convention `check_script_tests.py` enforces repo-wide (`x.py` is tested by `test_x.py`) was not a selection route at all.

## Steps to Reproduce

1. `python3 -c "import gate; gate.select_tests('.', ['.claude/skills/sdlc-studio/scripts/command_audit.py'])"` with `test_command_audit.py` measuring at least one resolvable read path.
2. Before the fix: 66 selectors, `test_command_audit.py` absent - the module named after the changed script.
3. `test_gate.py::UnattributableSelectionTests::test_selection_comes_from_the_import_graph` and `TestSelectionTests::test_selection_comes_from_the_import_graph` both red, which is how it was found.

## Proposed Fix

FIXED in the same commit as US0485. A third selection route in `select_tests`: a changed `x.py` selects `test_x.py` by basename, the convention the repo already enforces. Independent of both the import graph and the read measurement, so it holds however a test loads its subject and whatever that test happens to read. The two pre-existing tests that named this property now pass for the reason they assert rather than by the unattributable sweep.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `gate.select_tests` reached a script's own test module by two routes: the import graph, and the statically measured read set of each suite module's source.
- [ ] The proposed fix lands, pinned by a test: FIXED in the same commit as US0485.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (delivering US0485) | Filed |
