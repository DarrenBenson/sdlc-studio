# BG0708: gate.py reads SDLC_VERIFY_TIMEOUT per call, so a previously hermetic suite now inherits whatever the environment sets

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** BG0676 qa delivery verdict, RUN-01M2JA6J 2026-09-16, brief 1ed13c1fd81c.
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0676 moved the per-verifier ceiling from a definition-time default to `_verify_timeout()` read when the lane RUNS (gate.py:2044), which is what let CI raise it. The same change makes every caller environment-sensitive: `test_gate.py`:4063, 4106 and 6119 took a fixed 120 s before and now take whatever `SDLC_VERIFY_TIMEOUT` holds in the ambient environment. Inside the corpus-verify job that is 300, which is more permissive and cannot redden a run, so nothing is wrong today. What is wrong is the coupling: a suite that used to assert against a constant now asserts against the environment it happens to run in, and the next person to set that variable - a developer shortening a local run, a CI job reusing the name - changes what those tests measure without touching them. Raised by the qa seat at BG0676's delivery review as new environment coupling in a previously hermetic suite.

## Steps to Reproduce

1. Export `SDLC_VERIFY_TIMEOUT`=1. 2. Run pytest on `test_gate.py`'s release-verify cases at :4063, :4106 and :6119. 3. They run under a 1 s ceiling rather than the 120 s they were written against, with nothing in the test naming the difference.

## Proposed Fix

Make the ambient value explicit where the suite depends on it: either clear `SDLC_VERIFY_TIMEOUT` in those tests' environment so they assert against the documented default, or have them set it to the value they mean and say so. A test whose ceiling comes from the environment should name that in its own text, so a reader can tell a deliberate ceiling from an inherited one.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: BG0676 moved the per-verifier ceiling from a definition-time default to `_verify_timeout()` read when the lane RUNS (gate.py:2044), which is what let CI raise...
- [ ] **AC2** The proposed fix lands, pinned by a test: Make the ambient value explicit where the suite depends on it: either clear `SDLC_VERIFY_TIMEOUT` in those tests' environment so they assert against the...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Filed |
