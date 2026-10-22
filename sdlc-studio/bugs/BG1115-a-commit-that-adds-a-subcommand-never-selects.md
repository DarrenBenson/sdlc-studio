# BG1115: A commit that adds a subcommand never selects test_cli_grammar.py, which reaches every script through surface.enumerate_scripts, so a grammar defect is first seen by the full suite at push

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate_selection_reaches_loaders.py, .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py, .claude/skills/sdlc-studio/scripts/tests/test_gate_census_glob.py, changelog.d/BG1115.md, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** US1088 build, 2026-10-22: the local hook's unit-tests lane (94 modules) did not select test_cli_grammar.py; run-suite.sh all on devserver1 failed RootPlacementConformance for tree f10299e4.
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T06:11:09Z

## Summary

Per-commit selection (gate.py `_selection_indexes`) selects a test module for a staged file through a direct import, a `load_script` literal, a `test-census-subject` header or one level of fixture import. `test_cli_grammar.py` reaches every shipped script through `surface.enumerate_scripts(DIR)` and declares only `lib/sdlc_md.py` as its census subject, so no change to a script's own parser selects it. US1088 added `critic.py self-check record` with a nested `--root` defaulting to '.': the local hook ran 94 modules and stayed green on it, and the host's full suite was the first to fail `RootPlacementConformance` (2026-10-22, 453 s on devserver1).

## Steps to Reproduce

Stage a change to any script's `build_parser` and run the pre-commit hook: `test_cli_grammar.py` is not among the selected modules.

## Proposed Fix

Let a census header name a glob (`# test-census-subject: .claude/skills/sdlc-studio/scripts/*.py`), matched with fnmatch against each staged path, and declare it in `test_cli_grammar.py.` Its run costs about 20 s, which is cheaper than a red push and a repair round.

## Acceptance Criteria

- [ ] **AC1** Given a test module whose census header names a glob, when a staged path matches it, then selection includes that module, and a path the glob does not match does not select it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_census_glob.py::CensusGlobTests::test_a_glob_census_subject_selects_each_matching_path
- [ ] **AC2** Given a staged change to .claude/skills/sdlc-studio/scripts/critic.py, selection includes `test_cli_grammar.py`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_census_glob.py::CensusGlobTests::test_a_script_change_selects_the_grammar_test

## Impact

A grammar defect in a new subcommand passes the commit hook and costs a red full-suite run at push before it is found.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Filed |
