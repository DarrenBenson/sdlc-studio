# BG0348: An all-skipped run is still stamped green for unittest, jest, vitest and go

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYHVWK closing review, independent reviewers); agent; skill v5.0.0

## Summary

BG0317 made an all-skipped PYTEST run not-a-pass. The reviewer verified the same hole survives for every other runner family: a real unittest all-skipped run prints 'Ran 1 test' then 'OK (skipped=1)' and exits 0; jest prints 'Tests: 3 skipped, 3 total'; vitest 'Tests 3 skipped (3)'; a go run of only t.Skip tests prints 'ok pkg'. None matches the zero-count signature `_ran_no_tests` looks for, so each is stamped green by tests that never ran.

## Steps to Reproduce

1. Write a story whose Verify line names an all-skipped unittest selector. 2. Run `verify_ac`: the AC is stamped green. 3. Confirm the runner exits 0 with 'OK (skipped=1)' and no 'no tests ran' text. 4. Repeat for jest, vitest and go using the summary strings above.

## Proposed Fix

Give each runner family its own all-skipped signature beside the pytest one, and make a run whose counts are entirely skipped (plus deselections and warnings) vacuous and not-ok, as the pytest path now is. unittest matters most: it is this repository's own default runner, so the silent pass is live on the path the project itself uses.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (RUN-01KYHVWK closing review, independent reviewers) | Filed |
