# BG1325: A hand-run mutation pass can leave a stale `.pyc` that Python reuses after the source is restored, so a later test run, the commit hook's among them, judges the mutant rather than the code

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** US1142's refused landing (land-US1142.log, '7 != 6' against restored source) and the US1147 builder's runner note (RUN-01M7061X)
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T18:59:39Z

## Summary

Hit twice in run nine (2026-11-09). A mutant that changes a source file without changing its size (US1142's `assertEqual(6` to `assertEqual(7`; two same-size mutants in US1147's pass), restored within the same second, leaves the mutant's bytecode in `__pycache__` with a source mtime and size Python accepts as current. US1142's landing commit was then refused by its own test asserting the mutant's number, while the traceback showed the restored source. Nothing in the self-check guidance, the lane brief or the commit hook's test run guards against it.

## Steps to Reproduce

1. In a scratch copy, change a test's `assertEqual(6` to `assertEqual(7`, run the test, and restore the line within the same second.
2. Run the test again: it fails as the mutant would, because the cached bytecode is reused.

## Proposed Fix

Have the mutation guidance and any shipped mutation runner set PYTHONDONTWRITEBYTECODE=1 (or a throwaway PYTHONPYCACHEPREFIX), and have the commit hook's unit-test lane run with a fresh pycache prefix so no worktree bytecode is trusted; add a test that a same-size, same-second restore is judged on its source.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Hit twice in run nine (2026-11-09).
- [ ] **AC2** The proposed fix lands, pinned by a test: Have the mutation guidance and any shipped mutation runner set PYTHONDONTWRITEBYTECODE=1 (or a throwaway PYTHONPYCACHEPREFIX), and have the commit hook's...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
