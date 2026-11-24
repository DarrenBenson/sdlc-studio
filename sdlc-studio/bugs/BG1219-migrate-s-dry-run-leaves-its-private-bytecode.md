# BG1219: migrate's dry run leaves its private bytecode directory behind when verify_ac's ceiling kills it, and BG1183 AC1 cannot pass verify_ac at its 120 s default

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py, changelog.d/BG1219.md
> **Evidence:** BG1183 round-2 verdict, scratchpad run5/BG1183-verdict-r2.txt.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T19:15:41Z

## Summary

2026-11-04, BG1183's round-2 review (non-blocking). A verify run whose ceiling killed AC2's `timeout 120 migrate.py` left a 466-file sdlc-migrate-pyc-* directory under TMPDIR: `verify_ac` kills the timeout wrapper, so migrate's SIGTERM cleanup never runs (the test covers SIGTERM only). Also, AC1's bound is 300 s but `verify_ac`'s default ceiling is 120 s per verifier, so `verify_ac run --id BG1183` without `--timeout 300` reads AC1 red even when it meets its own bound.

## Steps to Reproduce

1. `verify_ac.py run --id BG1183` at load that pushes AC2 past 120 s.
2. `ls $TMPDIR | grep sdlc-migrate-pyc`.

## Proposed Fix

Clean the bytecode directory from an atexit hook or a parent-death signal as well as SIGTERM, and give AC1's Verify a declared ceiling `verify_ac` reads, or note --timeout 300 beside it.

## Acceptance Criteria

- [ ] **AC1** Given a `migrate.py run` whose collection guard has made its `sdlc-migrate-pyc-*` directory, when the process is killed with SIGKILL, then a later `migrate.py` start under the same TMPDIR removes the stale directory (a dead owner's) and leaves a live run's directory alone. Fails on: the directory left behind: SIGTERM is handled at migrate.py line 1132 but no hook runs on SIGKILL or on the timeout wrapper being killed by verify_ac.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_migrate.py::QuietCollectionTests::test_a_killed_runs_bytecode_directory_is_swept_by_the_next_run
- [ ] **AC2** Given BG1183's AC1 bound of 300 s, when its Verify line is read, then it declares the ceiling verify_ac honours so `verify_ac run --id BG1183` does not read it red at the 120 s default. Fails on: an AC1 Verify with no declared ceiling, red at the default for a run inside its own bound.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_migrate.py::QuietCollectionTests::test_bg1183_ac1_declares_its_own_ceiling

## Impact

TMPDIR fills with stale bytecode, and the transition gate reads a passing criterion red at its default.

QA note at HEAD: not reproduced as a leak by a clean SIGTERM, which `test_a_terminated_run_removes_its_bytecode_directory` pins and the code handles; the open part is SIGKILL (the wrapper `verify_ac` kills) and the undeclared ceiling. An atexit hook cannot run on SIGKILL, so the fix is a sweep of dead owners' directories at the next start (name the directory with the owner's pid) rather than the atexit hook the Proposed Fix names.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: the one criterion ran a whole module and named no failure; split into the SIGKILL sweep and the undeclared ceiling, and noted that an atexit hook cannot cover SIGKILL (class and test names are the builder's to create) |
