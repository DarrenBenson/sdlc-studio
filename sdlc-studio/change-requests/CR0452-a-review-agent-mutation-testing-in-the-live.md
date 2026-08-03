# CR-0452: A review agent mutation-testing in the live working tree can silently revert the author's code

> **Status:** Complete
> **Decomposed-into:** EP0177
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-audit.md, .claude/skills/sdlc-studio/scripts/mutation.py
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYHVWK re-review, observed silent revert); agent; skill v5.0.0

## Summary

The doctrine tells a reviewer to mutation-test - break the production code on purpose, confirm the test reddens, restore. It does not say WHERE, so a review agent does it in the working tree the author is still committing from. On 2026-07-27 a repair to sprint.py's drift warning was reverted between its own commit and the next one: the else-branch vanished, leaving a variable computed and unused. The commit that carried the revert (14eb4447) was about something else entirely and never mentions sprint.py; the author swept it up with `git add -A` while two review agents were running.

It survived a fully green 4,600-test suite because nothing asserted the message, and it was found only because an independent re-reviewer diffed the claim against HEAD rather than against the commit that made it. Had the re-review been skipped as an efficiency measure, a shipped repair would have been silently absent from the release it was recorded as part of.

## Impact

Who: any project whose reviewers run in the same checkout as the author, which is the default the doctrine implies. What breaks: the author's tree is mutated by a process the author does not control and cannot see, and `git add -A` - the natural way to stage a paperwork commit - launders it into history under an unrelated message. Worse than a lost fix, it is a lost fix with a green suite and a commit trail that attributes the change to nobody. The related hazard is the same shape: an author committing while reviewers run can also stage a half-finished mutant as though it were work.

## Acceptance Criteria

- [ ] The doctrine states that mutation testing by a delegated reviewer runs in an isolated checkout - a worktree or a copy - never in the tree the author is working from, and says why.
- [ ] It states the author-side rule that follows: do not stage with a whole-tree add while delegated agents are running, because their working state is indistinguishable from your own.
- [ ] `mutation.py` refuses, or loudly warns, when asked to mutate a file with uncommitted changes or inside a checkout that is not its own, so the safe path is the default rather than a thing to remember.
- [ ] A repair that changes behaviour carries a test asserting that behaviour, so a later silent revert reddens the suite instead of passing it - three repairs in this sprint shipped unpinned and one of them was reverted.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (RUN-01KYHVWK re-review, observed silent revert) | Raised |
