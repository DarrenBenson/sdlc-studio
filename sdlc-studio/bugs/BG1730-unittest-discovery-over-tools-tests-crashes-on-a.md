# BG1730: unittest discovery over tools/tests crashes on a test module name the skill's tests also use, so US0253 AC2 reads red

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_lean_migrate_config.py, tools/tests/test_config_refusal_pages.py, tools/tests/test_test_census.py, sdlc-studio/bugs/BG1634-three-reference-pages-still-say-the-scripts-fall.md, sdlc-studio/bugs/BG1642-config-py-show-prints-a-runtimeerror-traceback-without.md, changelog.d/BG1730.md
> **Evidence:** GitHub Actions scheduled run 45196238545 (corpus-verify, 65dc7d62): red-criteria 2, NEW US0253::AC2; reproduced locally at 94b4b86e
> **Created:** 2026-11-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-23T16:14:49Z

## Summary

tools/tests/`test_lean_migrate_config.py` (added in bda739d4 for BG1634) shares its module name with .claude/skills/sdlc-studio/scripts/tests/`test_lean_migrate_config.py.` `python3 -m unittest discover -s tools/tests -k NoiseShapeDetectorTests`, US0253 AC2's Verify, imports the skill's module first and raises ImportError ('module incorrectly imported'), so a Done story's criterion is red: the scheduled corpus-verify run 45196238545 failed on it, and a release gate's executing verify would too. The pytest suite does not see it.

## Steps to Reproduce

1. From the repository root, run US0253 AC2's Verify:

   ```text
   python3 -m unittest discover -s tools/tests -k NoiseShapeDetectorTests
   ```

2. Observe the discovery fail before any test runs: `ImportError: 'test_lean_migrate_config' module incorrectly imported from '.../.claude/skills/sdlc-studio/scripts/tests'. Expected '.../tools/tests'.`

## Proposed Fix

Rename the tools-side module to a name of its own (it pins the reference pages' config-refusal sentences), update the Verify line in BG1634 and the Affects in BG1642 that name its path, and add a census test that refuses a tools/tests module whose name a skill test module also uses.

## Acceptance Criteria

- [ ] **AC1** Given the repository, when `python3 -m unittest discover -s tools/tests -k NoiseShapeDetectorTests` runs from its root, then discovery imports every tools/tests module from tools/tests and the noise-shape tests pass, so US0253 AC2 reads green. Fails on: `ImportError: 'test_lean_migrate_config' module incorrectly imported`, raised because tools/tests and the skill's tests both hold a `test_lean_migrate_config.py`.
  - **Verify:** shell python3 -m unittest discover -s tools/tests -k NoiseShapeDetectorTests
- [ ] **AC2** Given the tools-side page check renamed to `tools/tests/test_config_refusal_pages.py`, when its tests run, then both still pass, BG1634's Verify line and BG1642's Affects name the new path, and neither names the old tools-side path. Fails on: a Verify line left naming `tools/tests/test_lean_migrate_config.py`, which reads red once the file is gone.
  - **Verify:** shell python3 -m pytest -q tools/tests/test_config_refusal_pages.py && ! grep -q 'tools/tests/test_lean_migrate_config' sdlc-studio/bugs/BG1634-*.md sdlc-studio/bugs/BG1642-*.md
- [ ] **AC3** Given a tools/tests module whose file name a module under `.claude/skills/sdlc-studio/scripts/tests` also uses, when `tools/tests/test_test_census.py` runs, then a census test fails naming the shared file name, and it passes on the tree as it stands once the rename lands. Fails on: a census that reads each tests folder alone, so a second shared name could land unseen while the pytest suite stays green.
  - **Verify:** pytest tools/tests/test_test_census.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-23 | sdlc-studio | Filed |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three orchestrator) | Groomed: the steps restated, three executable criteria (discovery green, the rename and its references, a census guard against a shared module name) |
