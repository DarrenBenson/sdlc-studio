# BG0222: the pre-commit suite lanes break under git commit -a because hook GIT_* env leaks into test git calls

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/skill-tests.sh
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

git commit -a exports `GIT_INDEX_FILE` (and friends) to the pre-commit hook; the skill-tests and tool-tests lanes inherit them, so every test that spawns git inside its own temp fixture acts on the OUTER repo instead - 10 `test_lessons` failures, `test_mutation.StoryLaneTests` and `test_evidence_in_git` errors, none reproducible standalone. A commit made with git add + git commit passes the same gate, so the failure looks like flaky tests rather than an environment leak. Reproduce: `GIT_INDEX_FILE`=$PWD/.git/index python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p `test_lessons.py` -> FAILED (failures=10).

## Steps to Reproduce

1. Stage nothing; run git commit -am msg in this repo (hook enabled). 2. skill-tests lane fails with `test_lessons`/`test_review_prep_staleness`/`test_mutation` git-env failures. 3. Re-run the same suite standalone: green. 4. `GIT_INDEX_FILE`=$PWD/.git/index python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p `test_lessons.py` reproduces deterministically.

## Proposed Fix

Sanitise the suite environment in the hook lanes (env -u `GIT_DIR` -u `GIT_INDEX_FILE` -u `GIT_WORK_TREE` -u `GIT_PREFIX` before python3 -m unittest discover in tools/skill-tests.sh and the tool-tests lane), so the suites run in the environment they are written for regardless of how the commit was invoked.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
