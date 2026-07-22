# CR-0388: Committing while an adversarial reviewer is mutating the tree can stage a mutant; nothing but the gate stands in the way

> **Status:** Complete
> **Decomposed-into:** EP0103, EP0105
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/reference-sprint.md,.githooks/pre-commit
> **Date:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The closing review is an independent instance that hand-applies mutants to source files, verifies a test goes red, and restores them. That is correct and is how the review earns its keep. But the author works in the SAME tree at the same time, and a `git add -A` during a mutation window stages the mutated file. Observed during RUN-01KY321Q: `git add -A` staged retro.py while the reviewer had a mutant applied that removed the `Note` column and the `_run_covers` extraction, and the commit was refused only because the mutated source failed the suite. Seconds later the reviewer restored the file and the tree matched HEAD again, so the window was transient and invisible either side of it. Nothing announces that a mutation window is open. The single-writer rule already exists for mutation.py runs during a build and is written down for that case; the same hazard at review time is not covered, and the review is precisely when the author is doing ceremony commits (retro, review anchor, findings) that touch nothing the reviewer is mutating and therefore feel safe. Worth noting how narrowly this was caught: the gate blocked it for the right outcome by the wrong route - because the mutant broke tests, not because anything knew a mutation was in flight. A mutant that leaves the suite green, which is exactly what a SURVIVING mutant is, would have been committed silently.

## CORRECTION - the mechanism in the Summary above is WRONG

Filed on the author's inference and contradicted by the reviewer's own disclosure. The staged
`retro.py` did NOT carry a hand-applied mutant. The reviewer had built a helper directory with
`ln -sf <repo>/scripts/*.py .` and then run `git show f8bbfb5:...retro.py > retro.py` inside it;
the redirect FOLLOWED THE SYMLINK and overwrote the live working tree with the pre-sprint version,
silently reverting all of BG0243 and BG0244. The reviewer detected it via `git status`, restored
from HEAD, verified the restore and disclosed it.

Three readings were offered before the truth arrived: the author first announced it as a reviewer
failing to restore two units' work, then retracted that and announced a transient mutation window
with no problem, and both were asserted from a diff rather than established. The first was closer.

**What survives, and it is still worth building.** The staging hazard is real and independent of
how the file came to be wrong: `git add -A` during a review stages whatever state a concurrent
process has left, and the gate refused this commit only because the reverted source failed the
suite. A change that left the suite GREEN would have been committed silently under a paperwork
commit message. That is the acceptance criteria below.

**What must be filed separately** is the symlink write-through, which is the sharper hazard and is
the L-0158 class again: a throwaway working directory built with `ln -sf` turns any shell redirect
onto one of those names into a write into the source tree. That deserves its own lesson rather
than being buried in a CR about staging.

## Impact

Every sprint that runs the mandatory closing review while the author continues to commit ceremony artefacts, which is the normal shape of a close in this project. The damage from a surviving mutant reaching main is a silent behaviour change in shipped code, attributed to a commit whose message is about paperwork, and it would pass the gate because a surviving mutant is by definition one the tests do not catch. The author also wasted time misdiagnosing the transient diff as a failed restore by the reviewer, which is its own cost: the state was genuinely alarming and genuinely fine.

## Acceptance Criteria

- [ ] The reviewer declares a mutation window, and the author's commit path refuses or warns while one is open
- [ ] Staging is scoped rather than wholesale during a review: a documented path that commits named paths instead of `git add -A`
- [ ] reference-sprint.md states the hazard where it states the single-writer rule for mutation runs, so the review-time case is covered by the same discipline
- [ ] A test drives the guard with a mutation window open and a green-but-mutated source, and asserts the commit is refused - the case the gate cannot catch today

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Raised |
