# BG0251: The engagement floor cannot see a violation the gating commit itself creates, because shipped is derived from git log --grep

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py,.githooks/pre-commit
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The floor only evaluates SHIPPED units, and `_git_touched_by_id` derives that from `git log --grep` over the history. A unit whose id has never appeared in a commit message is therefore invisible to the check. So the pre-commit gate structurally cannot detect a floor violation that the very commit it is gating is about to introduce: the condition does not exist until after the commit lands. Observed directly during RUN-01KY321Q. The floor was run, reported 5 violations, all 5 were given a planning pass, and it then reported `0 violation(s)`. The pre-commit gate passed and the delivery commit landed. Running the same check immediately afterwards reported 2 NEW violations, BG0244 and BG0246, which had been clean moments earlier only because no commit had yet mentioned them. Nothing changed in those two files. The gate green-lit a commit that was non-compliant the instant it existed. This is not cosmetic: it means the floor is permanently one commit behind, a sprint discovers its floor violations only at CLOSE rather than at commit, and closing then requires an extra commit whose own new units are in turn invisible - so the pattern can repeat. It also makes the pre-commit lane misleading rather than merely incomplete, because a PASS is read as 'this commit is compliant'.

## Steps to Reproduce

1. Take a bug artefact with a multi-file Affects and no acceptance criteria whose id has never been used in a commit message. 2. Run `engagement_floor.py` check. Observed: it is not listed, because it is not yet shipped. 3. Commit, with the id in the commit message. 4. Run `engagement_floor.py` check again. Observed: the unit is now a violation. The pre-commit gate at step 3 passed, and could not have done otherwise.

## Proposed Fix

Make the check see what the commit is ABOUT to ship rather than only what history records. The id is available at commit time from the staged artefact changes and from the commit message the hook is already handed, and `check-commit-msg` in this same script already parses that message, so the input exists and is simply not joined to the floor. Treat a unit named by the pending commit as shipped for the purposes of that commit's gate. Guard it with a test that stages an unplanned multi-file unit, runs the hook's floor lane against the pending message, and asserts it REFUSES - today it passes. Note the adjacent honesty problem to fix at the same time: a green floor lane currently means 'no already-shipped unit violates', not 'this commit is compliant', and the wording should say which until the check can mean the stronger thing.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
