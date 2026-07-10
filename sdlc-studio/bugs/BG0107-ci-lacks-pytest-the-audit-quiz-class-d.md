# BG0107: CI lacks pytest; the audit-quiz class-D grader fails its first CI exposure

> **Status:** Fixed
> **Verification depth:** functional (dep added on the pinned interpreter's early install step; grader dependency and knock-on average both root-caused; CI run on this push is the closing oracle)
> **Severity:** Low
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

tools/bench/`audit_quiz.py` grades class-D auditor answers by shelling python -m pytest inside the fixture workspace. The Lint workflow's unit-test step installs coverage/pyyaml/bandit but not pytest, so the three ClassD tests (added with the bench harness after the last green CI run) fail on CI with 'cited check does not pass on the workspace', and one IndependenceWeight average shifts as a knock-on. Local dev has pytest, masking it - the third local-environment mask found on release day (with BG0105's 3.13 API and BG0106's comparator). Fix: add pytest to the unit-test step's pip install.

## Steps to Reproduce

CI run 29117924298: `test_audit_quiz` ClassDTests x2 + IndependenceWeightTests fail; python -m pytest absent on the runner

## Proposed Fix

add pytest to the workflow's unit-test pip install line

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Filed |
