# BG0251: The engagement floor cannot see a violation the gating commit itself creates, because shipped is derived from git log --grep

> **Status:** Fixed
> **Verification depth:** functional - the defect was reproduced first (a staged, unplanned, multi-file unit passes the hook, and the same check refuses it the moment the commit lands), the fix was driven from that red test, and both the unit lane and the hook lane were then mutation-proven with 14 hand-applied mutants against the two changed files. Two survived first time and each drove a change rather than a re-run: the pending leg's judged-id filter was unobservable until a test pinned the returned key set, and the scope caveat was printed on the REFUSAL but not on the PASS, which is the half that gets misread. Not verified: any claim that the message-only case is now covered - it is not, and `test_a_unit_named_only_in_the_message_is_still_not_seen` holds that limit red-handed rather than leaving it to prose.
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py,.githooks/pre-commit,.claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py,tools/tests/test_precommit_floor_pending.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The floor only evaluates SHIPPED units, and `_git_touched_by_id` derives that from `git log --grep` over the history. A unit whose id has never appeared in a commit message is therefore invisible to the check. So the pre-commit gate structurally cannot detect a floor violation that the very commit it is gating is about to introduce: the condition does not exist until after the commit lands. Observed directly during RUN-01KY321Q. The floor was run, reported 5 violations, all 5 were given a planning pass, and it then reported `0 violation(s)`. The pre-commit gate passed and the delivery commit landed. Running the same check immediately afterwards reported 2 NEW violations, BG0244 and BG0246, which had been clean moments earlier only because no commit had yet mentioned them. Nothing changed in those two files. The gate green-lit a commit that was non-compliant the instant it existed. This is not cosmetic: it means the floor is permanently one commit behind, a sprint discovers its floor violations only at CLOSE rather than at commit, and closing then requires an extra commit whose own new units are in turn invisible - so the pattern can repeat. It also makes the pre-commit lane misleading rather than merely incomplete, because a PASS is read as 'this commit is compliant'.

## Acceptance Criteria

- [x] **AC1:** A unit the pending commit puts below the floor is visible BEFORE the commit
      lands: `detect(root, include_staged=True)` folds the staged index in and marks the unit
      `staged_new`.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_engagement_floor.py
- [x] **AC2:** The pending verdict is the verdict the commit actually produces: the same unit,
      the same kind and the same file count as the unchanged history leg reports once the
      commit exists. Without this the lane could refuse commits for reasons the floor never held.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_engagement_floor.py
- [x] **AC3:** The pre-commit hook runs that lane and REFUSES the commit (D0053), staging an
      unplanned multi-file unit that passed the gate before this fix.
      **Verify:** shell python3 -m unittest tools.tests.test_precommit_floor_pending
- [x] **AC4:** The gap that remains is stated where it is read, not only in a docstring: both
      the lane's refusal and its PASS print that they judge the staged index and cannot read
      the commit message, and the gate-facing line says its evidence is committed history.
      **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_engagement_floor.py
- [x] **AC5:** The message-only case is held to a test that asserts it is NOT covered, so no
      later edit can quietly claim it is.
      **Verify:** shell python3 -m unittest tools.tests.test_precommit_floor_pending

## Resolution

Partly closed, partly documented, and the boundary is the point.

**Closed.** `detect(root, include_staged=True)` folds the STAGED INDEX into the file-count
signal: the judged units whose artefact this commit stages are attributed this commit's staged
source files, which is what the history leg attributes to them the moment the commit exists.
`check --pending` reports only what the commit CREATES (`staged_new`), and the hook runs it as
the `floor-pending` lane, before the unit suites. The delivery-commit shape that produced the
observed failure - a batch commit staging each unit's artefact beside the code - is caught
before it lands. Proven by an equivalence test, not by assertion: the pending verdict and the
post-commit verdict are compared field by field on the same fixture.

**Documented, not closed.** A unit named ONLY in the commit message, whose artefact this commit
does not stage, is still invisible until the commit exists. This is not an oversight to be
fixed later in the same lane: a pre-commit hook is not given the message it is gating. Verified
directly rather than recalled - a hook printing `.git/COMMIT_EDITMSG` at pre-commit time shows
the PREVIOUS commit's message, so reading it would judge the wrong commit. Closing that case
needs the commit-msg hook, which is where the message first exists, and that is a different
file and a different unit of work. Until then the floor remains one commit behind for that
shape, and both the lane and the gate line now SAY which evidence they rest on.

**The adjacent honesty problem, also fixed.** A green floor previously read as "this commit is
compliant" when it meant "no already-committed unit violates". Both the CLI line and the
gate-facing `remedy_detail` now say "on committed evidence", and the pending lane prints its
scope on the pass as well as on the refusal.

## Steps to Reproduce

1. Take a bug artefact with a multi-file Affects and no acceptance criteria whose id has never been used in a commit message. 2. Run `engagement_floor.py` check. Observed: it is not listed, because it is not yet shipped. 3. Commit, with the id in the commit message. 4. Run `engagement_floor.py` check again. Observed: the unit is now a violation. The pre-commit gate at step 3 passed, and could not have done otherwise.

## Proposed Fix

Make the check see what the commit is ABOUT to ship rather than only what history records. The id is available at commit time from the staged artefact changes and from the commit message the hook is already handed, and `check-commit-msg` in this same script already parses that message, so the input exists and is simply not joined to the floor. Treat a unit named by the pending commit as shipped for the purposes of that commit's gate. Guard it with a test that stages an unplanned multi-file unit, runs the hook's floor lane against the pending message, and asserts it REFUSES - today it passes. Note the adjacent honesty problem to fix at the same time: a green floor lane currently means 'no already-shipped unit violates', not 'this commit is compliant', and the wording should say which until the check can mean the stronger thing.

### Round-1 review addition: an unreadable index refused rather than read clean

The closing review found the pending leg printing a CLEAN when it could not read the index:
`_staged_paths` returned `[]` both when git ANSWERED that nothing was staged and when git could
not be asked at all, so a lane that failed to read the index printed "no new violation" and
exited 0. That is a false clean on the single signal this leg exists to provide, and it is this
bug's own defect class committed inside this bug's own fix.

`_staged_paths` now returns None when git cannot answer, `_pending_touched_by_id` raises
`StagedIndexUnreadable` rather than letting any caller treat it as empty, and the lane REFUSES
with a line saying plainly that it is reporting nothing rather than reporting no violations.

Mutation-proven, and the first pass found a survivor worth recording: reverting the `OSError`
branch to `[]` - the original defect exactly - left the suite green, because the non-git-directory
test reaches the `returncode != 0` branch instead. The guard for a MISSING git binary was pinned
by nothing while reading as covered. A direct test patching `subprocess.run` to raise, and to
time out, kills it. Three of the four mutants were killed on the first pass; this was the fourth.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-22 | sdlc-studio | Acceptance criteria authored, fixed red-first, resolution recorded: staged-index leg closed, message-only case documented and held to a test |
