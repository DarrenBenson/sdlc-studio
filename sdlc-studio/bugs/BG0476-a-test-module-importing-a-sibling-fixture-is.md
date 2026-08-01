# BG0476: A test module importing a sibling fixture is unimportable under pytest, so the story's own verifier cannot run

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** tools/tests/test_precommit_claim_drift.py, tools/tests/test_precommit_scope_collapse_lane.py, tools/tests/test_check_spec_claims.py
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-08-01T08:00:52Z

## Summary

`tools/tests/` modules that reuse a sibling's hermetic fixture import it by module name (`import test_precommit_window_guard`). That resolves under `unittest discover -s tools/tests`, which puts the directory on the path, and fails under pytest, which does not. `verify_ac` invokes pytest, so a story whose Verify line names such a test reports FAIL with a ModuleNotFoundError - the criterion cannot be checked at all, and the failure looks like a broken feature rather than a broken import path.

Hit twice in one sprint: `test_precommit_claim_drift.py` (US0585) and, retrospectively, `test_precommit_scope_collapse_lane.py` written for BG0413, whose criterion had therefore never been verifiable by the tool that checks criteria. Both fixed with an explicit path insert, but nothing stops the next one - and the failure mode is silent until a story happens to name the test.

## Steps to Reproduce

1. python3 -m pytest tools/tests/`test_precommit_scope_collapse_lane.py` -> ModuleNotFoundError: No module named '`test_precommit_window_guard`' at collection.
2. PYTHONPATH=tools/tests python3 -m unittest `test_precommit_scope_collapse_lane` -> OK.
3. `verify_ac.py` run --story <one naming such a test> -> the criterion reports FAIL.

## Proposed Fix

A `conftest.py` in `tools/tests/` putting the directory on `sys.path` fixes every module at once and cannot be forgotten by the next author, which a per-file insert can. A guard asserting every tools/tests module imports under BOTH runners would stop the class returning.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `tools/tests/` modules that reuse a sibling's hermetic fixture import it by module name (`import test_precommit_window_guard`).
- [ ] The proposed fix lands, pinned by a test: A `conftest.py` in `tools/tests/` putting the directory on `sys.path` fixes every module at once and cannot be forgotten by the next author, which a per-file...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Filed |
