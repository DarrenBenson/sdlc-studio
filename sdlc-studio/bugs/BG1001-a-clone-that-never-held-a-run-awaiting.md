# BG1001: A clone that never held a run awaiting its signature can end it only by signing it: stop there says there is nothing to stop

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_stop_a_run_from_any_clone.py, changelog.d/BG1001.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** BG0993 QA round 1 and round 2, 2026-10-08 (critic-verdicts.md).
> **Created:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T13:01:35Z

## Summary

BG0993 commits a run's record awaiting its signature, so every clone sees the run open and `plan --write` there refuses. But `sprint stop` reads only this checkout's `.local`, so in a clone that never held the run it answers 'no open run - there is nothing to stop' while the plan stays refused: the one way to end the run from that clone is to sign it. Found by BG0993's round-1 QA review (non-blocking); the round-2 review noted it had been claimed as carried to a follow-up without being filed.

## Steps to Reproduce

Close a run in one checkout and commit; clone; in the clone run `sprint.py stop --reason x --force` -> 'no open run'; `sprint.py plan --write` there is still refused, naming the run awaiting its signature.

## Proposed Fix

Let `stop` take up a tracked record awaiting its signature, as `sign` does, when this checkout holds no open run, and end it there (outcome stopped), refreshing the record; refuse when this checkout holds a different open run.

## Acceptance Criteria

- [ ] **AC1** `sprint stop` in a clone that never held a run awaiting its signature ends it from the committed record, and a plan there is then no longer refused by it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_stop_a_run_from_any_clone.py -k stop_ends_a_run_awaiting_signature_from_any_clone

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | sdlc-studio | Filed |
