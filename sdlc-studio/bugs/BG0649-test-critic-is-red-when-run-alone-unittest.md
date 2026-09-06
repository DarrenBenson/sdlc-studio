# BG0649: test_critic is red when run alone: unittest.mock is used at line 5131 without an import

> **Status:** Open
> **Verification depth:** functional [[derived: criteria 2; plan rows 3; EVIDENCE ABSENT - the mutation ledger holds no entry for this unit, which is not the same fact as nought killed; NOT RUN 3 (AC1 row 0, AC2 row 0, AC2 row 1); entry point 0 of 2 criteria through the shipped CLI, 0 in-process; 2 undetermined (the named node could not be isolated) | fp 72aaae347554 ]]
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_critic.py, tools/tests/test_skill_tests_env.py
> **Evidence:** Found by the BG0644 engineering delivery review (round 2, 2026-09-04) measuring modules alone; reproduced at ba715bd2. Present since 46cdf08b (2026-08-03).
> **Created:** 2026-09-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`.claude/skills/sdlc-studio/scripts/tests/test_critic.py` references `unittest.mock.patch.object` at line 5131 (and 5536) but never imports `unittest.mock`; the name resolves only when another test module has imported it first. Discovery order hides it, and a commit whose selection holds `test_critic` alone is refused by a test failure that is not the commit's.

## Steps to Reproduce

1. `cd .claude/skills/sdlc-studio/scripts/tests && python3 -B -m unittest test_critic`
2. Observe `ERROR: test_a_repair_does_not_answer_a_LATER_rejection` with `AttributeError: module 'unittest' has no attribute 'mock'` (rc=1).
3. Run the discovery suite or `python3 -B -m unittest test_config test_critic`: the same test passes, because a module loaded earlier imported `unittest.mock`.

## Proposed Fix

Import `unittest.mock` (or `from unittest import mock`) at the top of `test_critic.py` and reference it consistently; add a tools/ check or a test that runs each skill test module alone is out of scope here and is the subject of the selected-run lanes.

## Acceptance Criteria

- [ ] **AC1** Given `test_critic` is run as the only selected module, when `python3 -B -m unittest test_critic` runs from the tests directory with no other module imported first, then it exits 0 with no ERROR - the module imports `unittest.mock` itself at its head and every `unittest.mock.patch` site resolves through that import
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py
- [ ] **AC2** Given every skill test module, when each is run alone by name under `python3 -B -m unittest <module>` from a fresh interpreter, then every one exits 0 - a module that passes under discovery only because a sibling imported a name first is refused by this row, which is what let BG0649 pass for a month
  - **Verify:** pytest tools/tests/test_skill_tests_env.py::EveryModuleRunsAloneTests::test_every_skill_test_module_passes_alone

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `test_critic.py`, drop the head import of `unittest.mock` again, so the name resolves only through a sibling module's earlier import | Given `test_critic` is run as the only selected module, when `python3 -B -m unittest test_critic` runs from the tests directory with no other module imported first, then it exits 0 with no ERROR - the module imports `unittest.mock` itself at its head and every `unittest.mock.patch` site resolves through that import |
| AC2 | in `tools/tests/test_skill_tests_env.py`, run the modules under one interpreter in discovery order instead of one fresh interpreter each, so an import-order dependency passes | Given every skill test module, when each is run alone by name under `python3 -B -m unittest <module>` from a fresh interpreter, then every one exits 0 - a module that passes under discovery only because a sibling imported a name first is refused by this row, which is what let BG0649 pass for a month |
| AC2 | in `tools/tests/test_skill_tests_env.py`, read the module list from a hard-coded tuple instead of the tests directory, so a new module is never run alone | Given every skill test module, when each is run alone by name under `python3 -B -m unittest <module>` from a fresh interpreter, then every one exits 0 - a module that passes under discovery only because a sibling imported a name first is refused by this row, which is what let BG0649 pass for a month |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-04 | sdlc-studio | Filed |
