# BG1496: BG1487's README-opening guard lets a reworded approval claim through, though its docstring says it never would

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_readme_front_door.py, changelog.d/BG1496.md
> **Evidence:** Run fifteen (RUN-01M7HA6R) BG1487 QA verdict, 2026-11-16.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T05:06:26Z

## Summary

The QA seat approved BG1487 in run fifteen with a non-blocking finding: the test guarding the README's opening passes a reworded overclaim such as 'Each step is approved by a person you name.', although its docstring says such a claim can never pass; the independence and named-person sentences are also not fully pinned. A guard whose docstring claims more than it checks is lesson class LC-018. Verdict: sdlc-studio/reviews/verdicts/BG1487/f3f1a31e1f7c-f1eb209d.txt.

## Steps to Reproduce

Replace the README opening's signing sentence with 'Each step is approved by a person you name.' and run the BG1487 guard: it passes.

## Proposed Fix

Pin the opening's signing sentence to what sprint sign enforces (one named principal signs each run over its report) and refuse any wording that says a person approves each step; make the docstring say exactly what the test checks.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The QA seat approved BG1487 in run fifteen with a non-blocking finding: the test guarding the README's opening passes a reworded overclaim such as 'Each step...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Replace the README opening's signing sentence with 'Each step is approved by a person you name.' and run the BG1487 guard: it passes.
- [ ] **AC3** The proposed fix lands, pinned by a test: Pin the opening's signing sentence to what sprint sign enforces (one named principal signs each run over its report) and refuse any wording that says a person...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
