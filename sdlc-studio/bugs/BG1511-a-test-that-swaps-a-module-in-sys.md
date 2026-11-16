# BG1511: A test that swaps a module in sys.modules without restoring it reads green alone and in a selection, and red only in the batched release gate

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_test_hygiene.py
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T17:51:57Z

## Summary

BG1506: `CloseReportTests._mod` put a fresh `sprint_report` into sys.modules and left it there, so a later test's patch on its load-time import missed the module sprint.py re-imports at call time. The fault showed only in gate.py --release, which batches every pytest verifier in one session, and in CI's scheduled corpus check; the commit lanes, the push gate's module-parallel run and a lone run all passed. The release gate refused the first 6.4.0 tag candidate on it (US0996::AC3).

## Steps to Reproduce

1. Add a test that assigns sys.modules['`sprint_report`'] to a fresh module and does not restore it.
2. Run that file alone, and the push gate: both green.
3. Run gate.py --release: a later test that patches its load-time import reads red.

## Proposed Fix

A hygiene test that scans the skill's tests for an assignment to sys.modules[...] with no addCleanup, patch.dict or finally that restores it, refusing each one by file and line.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG1506: `CloseReportTests._mod` put a fresh `sprint_report` into sys.modules and left it there, so a later test's patch on its load-time import missed the...
- [ ] **AC2** The proposed fix lands, pinned by a test: A hygiene test that scans the skill's tests for an assignment to sys.modules[...] with no addCleanup, patch.dict or finally that restores it, refusing each one...

## Impact

A test-isolation fault surfaces for the first time at the release gate, on the critical path of a tag.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
