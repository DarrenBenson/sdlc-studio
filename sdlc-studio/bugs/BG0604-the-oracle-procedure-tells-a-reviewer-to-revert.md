# BG0604: The oracle procedure tells a reviewer to revert files by hand with no restore obligation, and it destroyed uncommitted work in the main tree

> **Status:** Open
> **Re-triaged:** High -> Medium, 2026-08-24, against the rubric in reference-bug.md. High is 'major feature broken, NO workaround'; Medium is 'feature impaired, workaround exists'. A workaround exists and the shipped tooling already prints it: every brief that critic.py brief generates carries 'Mutate in an ISOLATED CHECKOUT of your own, never the author's working tree' and 'Do NOT use git stash or git checkout --'. The defect is that D0149's oracle procedure does not repeat that guard, so the exposure is a decision record contradicting a brief rather than an unguarded path. The data loss it caused was real and is why it was filed High on consequence; re-triaged on likelihood and workaround.
> **Severity:** Medium
> **Premise corrected 2026-08-25:** AC4 as filed claimed D0149 'says only that the procedure is manual'. That is FALSE - D0149 reads 'run by the adversarial reviewer in an isolated worktree', committed hours before this bug was filed. The defect stands but is narrower and different in kind: the rule EXISTS in the decision and in every generated brief, and was broken anyway, so what is missing is enforcement rather than words. Found by an independent goal review before any code was written.
> **Points:** 3
> **Affects:** sdlc-studio/decisions.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** RUN-01M0JD1W, 2026-08-21: an adversarial reviewer briefed under D0149 ran the manual revert against the main working tree; `verify_ac.py` came back byte-identical to the base ref with the session's uncommitted work in it gone.
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

D0149's oracle rule requires a unit's revert evidence to come from a MANUAL procedure run by the adversarial reviewer, with the tool's output as cross-check only. The procedure as briefed is a bare `git show <base>:<path> > <path>`: it names no restore step, no snapshot to restore FROM, and nothing that fails loudly if the reviewer's shell is pointed at the wrong tree.

Three properties combine badly. Reviewers work in worktrees that SHARE the main repository's object store, so a path that resolves in one resolves in the other. The author is delivering in the main tree at the same time, by design - reviews run at lane boundaries, not after a freeze. And the redirect is a plain overwrite, so the previous contents are simply gone; there is no reflog, no stash and no index entry to recover from, because the work was never committed.

## Steps to Reproduce

Measured, not reconstructed. RUN-01M0JD1W, 2026-08-21:

1. Three adversarial reviewers were spawned in isolated worktrees, each briefed under D0149 to run the manual revert as the oracle.
2. The author continued delivering wave 2 in the MAIN tree, with roughly 400 uncommitted lines in `.claude/skills/sdlc-studio/scripts/verify_ac.py`.
3. A reviewer's manual revert ran against the main tree rather than its own worktree.
4. `git status` showed `verify_ac.py` modified; its sha256 was byte-identical to `git show da4beda1:<path>`, and every uncommitted line was gone.

Recovered only because the committed wave-1 work was at HEAD and the wave-2 edits were reconstructible from the session transcript. Nothing about the procedure made that recovery available; it was luck about what had already been committed.

## Proposed Fix

Two changes, and the first matters more than the second.

STOP HAND-REVERTING IN A SHARED TREE. The manual oracle exists because D0149 will not take the tool's word for its own correctness, which is right - but the reviewer can get an independent answer without mutating anything shared. `git worktree add --detach <tmp> <base>` gives the base revision as a separate checkout; overlay the unit's test files; run the verifiers there. That is the same measurement, taken by hand, with nothing at risk. It is the same isolation CR0552 proposes for the lane, so the two should land together.

MAKE THE BRIEF CARRY IT. The procedure reached the reviewer through a hand-written prompt rather than through `critic.py brief`, which is how it came to omit a restore step at all. The seat brief already carries the diff scope and the criteria; the revert procedure belongs there too, so it cannot be paraphrased into something unsafe by whoever writes the next prompt.

Filed as High rather than Medium on consequence, not on frequency: the failure is silent, it destroys work that was never committed, and this repository has now recorded the same class three times - a reviewer's tree-wide cleanup reverting a shipped repair, an early `git checkout HEAD --` restore inside `revert-check` itself, and this.

## Acceptance Criteria

- [ ] **AC1** Given a reviewer following the oracle procedure as briefed, when they take the base revision of a unit's production files, then no file in any shared checkout is written at any point - the measurement happens in a checkout created for it and removed afterwards
- [ ] **AC2** Given the procedure, when it is delivered to a reviewer, then it arrives from `critic.py brief` rather than from a hand-written prompt, so it cannot be paraphrased into a form with no restore step
- [ ] **AC3** Given a reviewer who nevertheless reverts in place, when the procedure runs, then it takes a byte snapshot FIRST and restores from it unconditionally - the paired control being that an interrupted run leaves the tree unchanged
- [ ] **AC4** Given a reviewer briefed to run the manual oracle, when the brief is generated, then it names the restore obligation as well as the worktree - D0149 already SAYS 'in an isolated worktree' and a reviewer still ran it against the main tree, so the gap is enforcement rather than specification, and the brief is the surface a reviewer actually reads

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Filed |
