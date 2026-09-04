# BG0649: test_critic is red when run alone: unittest.mock is used at line 5131 without an import

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** Found by the BG0644 engineering delivery review (round 2, 2026-09-04) measuring modules alone; reproduced at ba715bd2. Present since 46cdf08b (2026-08-03).
> **Created:** 2026-09-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`.claude/skills/sdlc-studio/scripts/tests/test_critic.py` references `unittest.mock.patch.object` at line 5131 (and 5536) but never imports `unittest.mock`; the name resolves only when another test module has imported it first. Discovery order hides it, and a commit whose selection holds `test_critic` alone is refused by a test failure that is not the commit's.

## Steps to Reproduce

1. `cd .claude/skills/sdlc-studio/scripts/tests && python3 -B -m unittest test_critic`
2. Observe `ERROR: test_a_repair_does_not_answer_a_LATER_rejection` with `AttributeError: module 'unittest' has no attribute 'mock'` (rc=1).
3. Run the discovery suite or `python3 -B -m unittest test_config test_critic`: the same test passes, because a module loaded earlier imported `unittest.mock`.

## Proposed Fix

Import `unittest.mock` (or `from unittest import mock`) at the top of `test_critic.py` and reference it consistently; add a tools/ check or a test that runs each skill test module alone is out of scope here and is the subject of the selected-run lanes.

## Acceptance Criteria

- [ ] **AC1** Given `test_critic` is run as the only selected module, when `python3 -B -m unittest test_critic` runs from the tests directory, then it exits 0 with no ERROR, without any other module having been imported first.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-04 | sdlc-studio | Filed |
