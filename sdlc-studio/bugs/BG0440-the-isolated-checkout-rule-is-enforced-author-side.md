# BG0440: the isolated-checkout rule is enforced author-side only, so `critic brief` issues a reviewer prompt that never states it and nothing notices when parallel reviewers share one tree

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-review.md
> **Evidence:** The surviving mutant is itself a live lead against US0465 and is being reviewed separately: if the unresolved-questions gate really fires only for `Done` and not for a type's other terminal statuses, a bug can reach Fixed carrying unresolved questions, which is what US0465's title says cannot happen. That finding was produced by a reviewer working in the very tree this bug is about, so it is being re-established in isolation rather than trusted.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio agent (Claude Opus 5); human; v1
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`reference-review.md` (#mutation-isolation) states the rule plainly: a delegated reviewer mutates code in an isolated checkout, never the author's working tree, because a mutant written over an uncommitted change is indistinguishable from that change once the file is restored. The rule is enforced in exactly one direction. `scripts/mutation.py run` refuses a target with uncommitted changes, which protects the AUTHOR. Nothing protects the tree from the REVIEWER: `critic.py brief` assembles the reviewer's prompt from the charter, the ACs, the scope and the return contract, and says nothing about where the reviewer is to mutate. So the practice survives only if whoever dispatches the reviewer happens to remember it - and the shipped brief, which is the one artefact guaranteed to reach the reviewer, is silent.

## Steps to Reproduce

Executed on this repository, 2026-07-30, during the close of RUN-01KYPZ1G.

1. `git status --porcelain` - tree clean apart from one untracked evidence file.
2. Dispatched four independent adversarial reviewers concurrently over the same working tree, each briefed with this repo's own mutation discipline (assert a unique anchor, purge `__pycache__`, run `python3 -B`, revert afterwards and verify with `git status`). Three of the four had `sprint.py` in scope; the revert instruction given was the ordinary one, `git stash` or `git checkout --`.
3. Stopped all four after roughly a minute, while they were still orienting.
4. `git status --porcelain` - `.claude/skills/sdlc-studio/scripts/transition.py` came back MODIFIED.
5. `git diff` on that file showed a live mutant left behind in the tree at line 774: `sdlc_md.is_terminal_status(type_, target_canon)` replaced by `target_canon == "Done"`.

The mutant was reverted by hand. Two things make this worse than one stray edit. First, it was found only because the tree was otherwise clean and it was checked - had the author had uncommitted work in that file, the mutant would have been indistinguishable from it, which is the exact scenario the doctrine describes. Second, `git stash` and `git checkout --` are tree-wide: either one, run by any of the four, silently reverts the OTHER reviewers' mutants mid-run, so a mutant reported SURVIVED may never have been on disk when its test ran. Every mutation result from a shared-tree parallel review is therefore unsound in both directions, and nothing in the output says so.

## Proposed Fix

Put the rule where the reviewer will actually read it, and make sharing detectable rather than silent.

1. `critic.py brief` states the isolated-checkout requirement in the issued prompt, alongside the mutation discipline it already carries. The brief is the one artefact that reaches every delegated reviewer, so a practice absent from it is a practice held only by the dispatcher's memory.
2. The brief names the concrete mechanism for this harness (`Agent(isolation: 'worktree')`) rather than the abstract requirement, and states explicitly that `git stash` is forbidden because it is tree-wide - a reviewer told only to 'revert afterwards' will reach for it.
3. A reviewer's mutation result carries the tree it was measured in. A run that cannot establish it had an isolated tree reports that fact beside its KILLED/SURVIVED table rather than presenting the counts unqualified, on the same principle the repo already applies to a destination the dead-flag detector cannot judge.

Also worth checking during refine: whether the brief should refuse outright when it can tell that a concurrent review is already in flight against the same tree, or whether stating it is the honest limit of what a prompt can enforce.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `reference-review.md` (#mutation-isolation) states the rule plainly: a delegated reviewer mutates code in an isolated checkout, never the author's working...
- [ ] Following the recorded steps no longer reproduces the defect: Executed on this repository, 2026-07-30, during the close of RUN-01KYPZ1G.
- [ ] The proposed fix lands, pinned by a test: Put the rule where the reviewer will actually read it, and make sharing detectable rather than silent.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio agent (Claude Opus 5) | Filed |
