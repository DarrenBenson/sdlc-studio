# BG1000: The commit's test selection does not recognise loader.load_script, so 71 of 77 loader edges are never selected and a commit touching sprint.py skips 22 modules that drive it

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate_selection_reaches_loaders.py, changelog.d/BG1000.md, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** BG0993's commit on 2026-10-08: the hook selected 3311 tests, passed all but a known timing flake, and left test_lean_close_shows_the_page red at 3bc1620e; the QA reviewer found it. Measured with gate.reach_index at 9e2a86ba: 71 of 77 load_script edges missed.
> **Created:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T12:32:17Z

## Summary

`gate.reach_index` builds the commit selection from imports and `_LOADER_NAME`, which matches `spec_from_file_location("x"`, `_load("x"` and `SCRIPTS / "x.py"` but not `loader.load_script("x")`, the shared test loader most modules use. Measured at 9e2a86ba: 77 `load_script` edges across the suite, 71 missed, in 42 modules over 30 scripts. Nor does it follow a module that imports a fixture module which loads the script (`test_lean_close_shows_the_page` imports `test_lean_close)`, or read the `test-census-subject` header a module declares. So a commit staging sprint.py runs 59 modules and skips `test_lean_close`, `test_lean_close_shows_the_page`, `test_lean_sign` and every other module that loads sprint that way. AGENTS.md and `gate.py --suite-decision --help` both say selection takes the modules that 'import, load or are named for' a changed file. Pre-existing.

## Steps to Reproduce

python3 .claude/skills/sdlc-studio/scripts/gate.py --suite-decision --changed .claude/skills/sdlc-studio/scripts/sprint.py, then look for tests/`test_lean_close.py`, `test_lean_close_shows_the_page.py` or `test_lean_sign.py` among the suite-selector lines: none is there, though each runs sprint.main.

## Proposed Fix

Recognise `load_script("x")` in `_LOADER_NAME`; select a module whose `test-census-subject` names the changed file; and follow one level of fixture imports (a test module importing another test module inherits the modules it reaches). Pin each with the CLI's own --suite-decision output.

## Acceptance Criteria

- [ ] **AC1** A test module that loads a script through `loader.load_script("x")` is selected by `gate.py --suite-decision --changed` for a change to x
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_selection_reaches_loaders.py -k load_script_is_a_load
- [ ] **AC2** A test module whose `test-census-subject` names a changed file, or that imports a fixture test module which reaches it, is selected for that change
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_selection_reaches_loaders.py -k census_subject_and_fixture_imports_reach

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | sdlc-studio | Filed |
