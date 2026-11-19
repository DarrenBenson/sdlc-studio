# EP0326: A sprint drives each unit's lane to its paperwork and wakes the model only for judgement

> **Status:** Draft
> **Derived Point Total:** 26
> **Parent:** CR0672
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** XL

## Summary

Decomposed from CR0672. Delivers the work CR0672 requested.

## Story Breakdown

- [x] [US1192: Lane land takes several worktrees and lands them as one commit with a Refs trailer for each unit](../stories/US1192-lane-land-takes-several-worktrees-and-lands-them.md)
- [x] [US1193: Lane land resumes a landing whose commit was refused without repeating the steps already done](../stories/US1193-lane-land-resumes-a-landing-whose-commit-was.md)
- [ ] [US1194: Sprint close names each unit that reached main with no lane land record](../stories/US1194-sprint-close-names-each-unit-that-reached-main.md)
- [x] [US1195: A refused landing or a REJECT yields a repair brief carrying the refusal and the findings verbatim](../stories/US1195-a-refused-landing-or-a-reject-yields-a.md)
- [ ] [US1196: Sprint drive walks one unit's lane from build to paperwork and stops with a decision record at any refusal](../stories/US1196-sprint-drive-walks-one-unit-s-lane-from.md)
- [ ] [US1197: Sprint drive runs a wave's independent units in parallel and stops at a warning, a conflict or the wave end](../stories/US1197-sprint-drive-runs-a-wave-s-independent-units.md)
- [ ] [US1198: Sprint drive step performs the whole chain after a hand-back in one command and prints the next prompt path](../stories/US1198-sprint-drive-step-performs-the-whole-chain-after.md)

## Acceptance Criteria (Epic Level)

- [ ] `sprint.py drive` walks the batch's lane state machine (headless build on CR0667's `lane run`, `lane land`, QA brief, review, `lane accept`, `lane price`, paperwork commit), runs independent units in parallel, and exits with a one-screen decision record on any non-zero exit, any warning a step prints, a REJECT, a rebase conflict or a wave end; a fixture batch shows each stop.
- [ ] In session, `sprint.py drive step --after <agent-id>` performs the whole post-hand-back chain in one command and prints the next agent's prompt path, so a fixture hand-back is handled in two orchestrator calls.
- [ ] `lane land --worktree` is repeatable and lands several staged worktrees as one integration commit with one Refs trailer per unit, `--resume` continues after a refused commit, and `sprint close` names any unit landed without a lane-land record.
- [ ] A refused landing, a red integration commit or a REJECT yields a repair-scope `lane brief` carrying the refusal output and the reviewer's findings verbatim for a fresh repair agent, and the toolchain runbook says the orchestrator does not edit or run tests at its own context.
- [ ] Before and after: the next sprint's cost anatomy (US1124) shows no mechanical-only orchestrator turn, against run six's 36 of 64, and no hand-rolled landing script.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
