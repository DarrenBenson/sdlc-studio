# BG0649: test_critic is red when run alone: unittest.mock is used at line 5131 without an import

> **Status:** Open
> **Verification depth:** functional [[derived: criteria 3; plan rows 5; EVIDENCE ABSENT - the mutation ledger holds no entry for this unit, which is not the same fact as nought killed; NOT RUN 5 (AC1 row 0, AC2 row 0, AC2 row 1, AC2 row 2, AC3 row 0); entry point 0 of 2 criteria through the shipped CLI, 0 in-process; 2 undetermined (the named node could not be isolated); 1 with no locatable test file | fp d99fbdb63563 ]]
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, AGENTS.md, tools/tests/test_check_spec_claims.py
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

- [ ] **AC1** Given `test_critic` is run as the only selected module under the UNITTEST runner - `python3 -B -m unittest test_critic` from the tests directory in a fresh interpreter, never pytest, which imports `unittest.mock` itself and so passes on the broken module - when it runs, then it exits 0 with no ERROR: the module imports `unittest.mock` at its head and every `unittest.mock.patch` site resolves through that import
  - **Verify:** shell cd .claude/skills/sdlc-studio/scripts/tests && python3 -B -m unittest test_critic
- [ ] **AC2** Given the push boundary gate (`gate.py --boundary push`), when its `module-alone` lane runs, then every skill test module is run alone under the unittest runner in a fresh interpreter and any failure names the module - bound at the push and release boundaries only, on `release-rehearsal`'s precedent, because it is the whole suite again serially and the per-commit gate is past its ceiling; pinned in a fixture tests directory of two modules where one passes only after the other imported a name
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ModuleAloneLaneTests::test_the_push_boundary_runs_every_module_alone_and_names_the_one_that_fails
- [ ] **AC3** Given the AGENTS.md lane roster, when `tools/tests/test_check_spec_claims.py` runs, then `module-alone` is named in the roster as bound at the push and release boundaries only, so a boundary-only lane the hook-derived sweep cannot see is not one nobody wrote down (LL0013)
  - **Verify:** pytest tools/tests/test_check_spec_claims.py::GateLaneTests::test_the_lane_roster_names_module_alone_as_boundary_bound

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `test_critic.py`, drop the head import of `unittest.mock` again, so the name resolves only through a sibling module's earlier import - killed by the unittest runner, not by pytest | Given `test_critic` is run as the only selected module under the UNITTEST runner - `python3 -B -m unittest test_critic` from the tests directory in a fresh interpreter, never pytest, which imports `unittest.mock` itself and so passes on the broken module - when it runs, then it exits 0 with no ERROR: the module imports `unittest.mock` at its head and every `unittest.mock.patch` site resolves through that import |
| AC2 | in `gate.py`, run the modules under one interpreter in discovery order instead of one fresh interpreter each, so an import-order dependency passes | Given the push boundary gate (`gate.py --boundary push`), when its `module-alone` lane runs, then every skill test module is run alone under the unittest runner in a fresh interpreter and any failure names the module - bound at the push and release boundaries only, on `release-rehearsal`'s precedent, because it is the whole suite again serially and the per-commit gate is past its ceiling; pinned in a fixture tests directory of two modules where one passes only after the other imported a name |
| AC2 | in `gate.py`, read the module list from a hard-coded tuple instead of the tests directory, so a new module is never run alone | Given the push boundary gate (`gate.py --boundary push`), when its `module-alone` lane runs, then every skill test module is run alone under the unittest runner in a fresh interpreter and any failure names the module - bound at the push and release boundaries only, on `release-rehearsal`'s precedent, because it is the whole suite again serially and the per-commit gate is past its ceiling; pinned in a fixture tests directory of two modules where one passes only after the other imported a name |
| AC2 | in `gate.py`, bind the lane per commit as well, so the per-commit gate pays the whole suite twice | Given the push boundary gate (`gate.py --boundary push`), when its `module-alone` lane runs, then every skill test module is run alone under the unittest runner in a fresh interpreter and any failure names the module - bound at the push and release boundaries only, on `release-rehearsal`'s precedent, because it is the whole suite again serially and the per-commit gate is past its ceiling; pinned in a fixture tests directory of two modules where one passes only after the other imported a name |
| AC3 | in `AGENTS.md`, leave the roster without the lane | Given the AGENTS.md lane roster, when `tools/tests/test_check_spec_claims.py` runs, then `module-alone` is named in the roster as bound at the push and release boundaries only |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-04 | sdlc-studio | Filed |
