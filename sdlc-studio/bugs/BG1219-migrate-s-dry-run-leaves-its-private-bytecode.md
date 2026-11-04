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

- [ ] **AC1** A killed dry run leaves no sdlc-migrate-pyc directory.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_migrate.py

## Impact

TMPDIR fills with stale bytecode, and the transition gate reads a passing criterion red at its default.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
