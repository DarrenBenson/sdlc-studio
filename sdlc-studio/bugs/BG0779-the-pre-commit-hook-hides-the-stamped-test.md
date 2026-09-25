# BG0779: The pre-commit hook hides the stamped-test re-read list on a passing commit

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .githooks/pre-commit, tools/tests/test_precommit_stamps_advisory.py, changelog.d/BG0779.md
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T18:44:42Z

## Summary

US0945 makes `verify_ac` `staged_stamps` list every stamped criterion whose test the commit changes (advisory, exit 0). .githooks/pre-commit's verdict() prints a lane's output only on FAIL, so on a passing commit the list is never shown, and the advisory reaches the author only when the commit is already refused for an orphan. Found by US0945's builder.

## Steps to Reproduce

1. Stage an edit to a test node a Verified: yes criterion names. 2. git commit. 3. The stamps-staged lane prints ok and no re-read list.

## Proposed Fix

Print the stamps-staged lane's output on success when it carries a re-read block (advisory only, no new refusal), with a hook test.

## Acceptance Criteria

- [ ] **AC1** Given a commit that stages an edit to a test node a `Verified: yes` criterion names and is otherwise clean, when `.githooks/pre-commit` runs, then the `stamps-staged` lane reads `ok` and its re-read list (the criterion's id, AC and words) is printed beneath it, and the hook exits 0. Fails on: `verdict()` printing a lane's output only on FAIL
  - **Verify:** pytest tools/tests/test_precommit_stamps_advisory.py::StampsAdvisoryTests::test_a_passing_commit_shows_the_re_read_list
  - **Verified:** yes (2026-09-25)
- [ ] **AC2** Given a clean commit that changes no stamped test, when the hook runs, then the `stamps-staged` lane prints `ok` and nothing else, and no other lane's success output is newly printed. Fails on: printing every lane's output on success
  - **Verify:** pytest tools/tests/test_precommit_stamps_advisory.py::StampsAdvisoryTests::test_a_commit_touching_no_stamped_test_prints_only_ok
  - **Verified:** yes (2026-09-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
| 2026-09-25 | sdlc | Groomed for Sprint 5: criteria and Verify selectors written |
