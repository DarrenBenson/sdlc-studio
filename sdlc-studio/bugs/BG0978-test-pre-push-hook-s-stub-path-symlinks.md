# BG0978: `test_pre_push_hook`'s stub PATH symlinks python3, which drops a virtualenv's packages, so the push gate cannot pass where pytest lives in a venv

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_pre_push_hook.py, tools/tests/test_pre_push_stub_interpreter.py
> **Evidence:** Found 2026-10-06/07 during the triage session that filed BG0955-BG0963 in this repository. Reproduced in a clean worktree with pytest in a venv.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:37:52Z

## Summary

`stub_path` symlinks `shutil.which('python3')` into a temporary directory (tools/tests/`test_pre_push_hook.py`:139-151). A virtualenv's interpreter finds its packages through `pyvenv.cfg` beside the executable it was started as, so started through the symlink it loses them: under a venv-installed pytest the hook's gate reports 'No module named pytest' and BoundaryMarkerReachesThePushTests and FrozenNotesTests::`test_filing_a_finding_reddens_no_test` fail. They pass once pytest is in the system interpreter. A contributor using a venv cannot get a push through the gate.

## Steps to Reproduce

Install pytest only in a virtualenv, put it first on PATH, run `pytest tools/tests/test_pre_push_hook.py -k red_boundary_only_test_refuses_the_push` -> 'No module named pytest' from the stub PATH.

## Proposed Fix

Write a small python3 wrapper script that execs `sys.executable` (or symlink `sys.executable` itself rather than the resolved interpreter) so the stub PATH keeps the running interpreter's environment.

## Acceptance Criteria

- [ ] **AC1** With pytest installed only in the active virtualenv, the pre-push hook tests pass
  - **Verify:** pytest tools/tests/test_pre_push_stub_interpreter.py -k stub_path_keeps_the_running_interpreter

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Filed |
