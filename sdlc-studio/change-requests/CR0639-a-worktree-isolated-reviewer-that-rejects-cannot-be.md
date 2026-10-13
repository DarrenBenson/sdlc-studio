# CR-0639: A worktree-isolated reviewer that REJECTs cannot be resumed for its round 2 once its worktree is removed, and nothing says to keep it until the review converges

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Date:** 2026-10-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (triage); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-13T08:59:14Z

## Summary

The review brief tells a reviewer to mutate in `Agent(isolation: 'worktree')`, and the round rule requires round 2 after a REJECT to come from the reviewer who rejected. In RUN-01M4R168 the orchestrator removed BG0950's round-1 reviewer's worktree once it was clean, as housekeeping; the harness then refused to resume that agent ('its worktree no longer exists'), and round 2 had to be given to a fresh instance of the same seat on the rejoinder brief, which quotes the prior verdict verbatim. The rejoinder brief makes that workable, but the reviewer's own probes and context were lost, and the toolchain runbook's review rows say nothing about when a reviewer's worktree may go.

## Impact

Every orchestrator running isolated reviews: a tidy-up between rounds costs the rejecting reviewer's context, and the round-2 row is then recorded for a seat instance that did not write round 1.

## Acceptance Criteria

- [ ] Given the toolchain runbook's review step, when an orchestrator reads it, then it says a REJECTing reviewer's worktree is kept until that unit's round 2 is recorded, and names what to do when it is gone (a fresh instance of the same seat on `critic.py brief --rejoinder`)
- [ ] Given a REJECT recorded through `critic.py record`, when it is written, then the command's output says the rejecting reviewer is needed for round 2

## Further evidence

- 2026-10-13, BG0976: the harness removed the round-1 reviewer's `isolation: worktree` checkout itself, at the agent's completion, because the reviewer had left it unchanged (it mutated and restored byte-identically, as the brief demands). Keeping the worktree is therefore not in the orchestrator's hands when the harness owns it: round 2 again went to a fresh instance of the seat. A reviewer that makes its own checkout (`git worktree add --detach <scratch dir> <commit>`) instead of harness isolation stays resumable, and the brief's isolation requirement is still met.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | Claude Opus 5.5 (triage) | Raised |
| 2026-10-13 | Claude Opus 5.5 (triage) | Further evidence: the harness auto-removes an unchanged isolated worktree, so a resumable reviewer makes its own checkout |
