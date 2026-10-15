# BG1057: The one-list test's check that ci installs from requirements-dev.txt sits outside its self-tested rules

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_prereq_list_is_ci_list.py
> **Evidence:** BG1056 round-1 QA verdict (APPROVE, BLOCKING: none) in sdlc-studio/reviews/critic-verdicts.md, its NOSUITE and U1/U2 notes.
> **Created:** 2026-10-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-15T20:18:28Z

## Summary

In tools/tests/`test_prereq_list_is_ci_list.py` the closed-world rules live in `_job_violations` and are self-tested over synthetic workflows, but the check that some ci step installs `-r requirements-dev.txt` is an assertion in the AC1 test itself. Deleting it leaves the module green, and a ci job with no suite install then fails only `test_lint_workflow_coverage`'s S1-S3 pins, not US1004 AC1's own Verify. The module's docstring also names wrapper scripts, but an install through a `uses:` action or a command held in a variable is the same unread class (found by BG1056's QA seat, U1 and U2).

## Steps to Reproduce

Delete the `assertIn(["-r", SUITE_FILE], suite, ...)` line from the AC1 test and remove the suite install from lint.yml's ci job: `test_prereq_list_is_ci_list.py` stays green.

## Proposed Fix

Move the suite-install requirement into `_ci_allow` or `_job_violations` (a ci job with no `-r requirements-dev.txt` install is a violation), self-test it, and list actions and variable-held commands beside wrapper scripts in the docstring.

## Acceptance Criteria

- [ ] **AC1** Given a ci job whose only pip install is a non-suite tool, when `test_prereq_list_is_ci_list.py`'s own rules judge it, then a violation names the missing requirements-dev.txt install.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-15 | sdlc-studio | Filed |
