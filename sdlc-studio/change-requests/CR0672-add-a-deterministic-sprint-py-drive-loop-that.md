# CR-0672: Add a deterministic `sprint.py drive` loop that advances each unit's lane through land, brief, review, accept, price and paperwork, lands several staged worktrees as one commit, and wakes the model only at a refusal, a REJECT, a conflict or a wave end

> **Status:** Proposed
> **Parent:** RFC0062
> **Priority:** High
> **Type:** Feature
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RFC0062 Phase 3, orchestration lens: findings 2, 4 and 6, combo.py replay (C 4.64M, B3+C 10.27M, B3+D 8.54M); ceremony lens: finding 2 (per-unit paperwork); run seven friction F4
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T12:23:03Z

## Summary

Run six's 64 orchestrator wake-ups were all hand-backs or task notifications, none from the operator, and 36 of them (80 calls, 3.44M direct) were purely mechanical: read a background command's output, run the next scripted step, spawn an agent, end the turn. The per-unit paperwork (self-check record, brief, record, verify stamp, commit, census fix-up, lane brief and return) took 61 orchestrator calls and 2.88M at about 47k a call. The orchestrator hand-rolled four scratch scripts for every landing (land.sh, verdict.sh copied from run five, batch-land.sh, batch-resume.sh) and never called `lane land` or `lane accept`: 21 hand-script runs came after `lane land` shipped at 13:48 and 10 after `lane accept` at 15:32. `lane land` takes one --worktree (sprint.py:12567), so batch landing, used five times to pay the 17-to-50-minute commit hook once, has no shipped equivalent (run seven friction F4). The lane action offers brief, return, land and accept (sprint.py:12546) but nothing chains them, and the orchestrator ran 95 diagnosis and repair calls itself at 400k and more.

## Impact

The orchestrator pays two to seven calls per hand-back at its full context. Replayed (combo.py), dropping the mechanical-only turns saves 4.64M alone; on top of the wave sessions it adds 1.73M (wave sessions 8.54M, both 10.27M: 15.12M to 4.85M).

## Acceptance Criteria

- [ ] `sprint.py drive` walks the batch's lane state machine (headless build on CR0667's `lane run`, `lane land`, QA brief, review, `lane accept`, `lane price`, paperwork commit), runs independent units in parallel, and exits with a one-screen decision record on any non-zero exit, any warning a step prints, a REJECT, a rebase conflict or a wave end; a fixture batch shows each stop.
- [ ] In session, `sprint.py drive step --after <agent-id>` performs the whole post-hand-back chain in one command and prints the next agent's prompt path, so a fixture hand-back is handled in two orchestrator calls.
- [ ] `lane land --worktree` is repeatable and lands several staged worktrees as one integration commit with one Refs trailer per unit, `--resume` continues after a refused commit, and `sprint close` names any unit landed without a lane-land record.
- [ ] A refused landing, a red integration commit or a REJECT yields a repair-scope `lane brief` carrying the refusal output and the reviewer's findings verbatim for a fresh repair agent, and the toolchain runbook says the orchestrator does not edit or run tests at its own context.
- [ ] Before and after: the next sprint's cost anatomy (US1124) shows no mechanical-only orchestrator turn, against run six's 36 of 64, and no hand-rolled landing script.

## Recommendation

Build `drive` and `drive step` on the shipped lane commands, make `lane land` multi-worktree with --resume, and route every repair to a repair-scope lane brief. Saving 1.73M per run, its marginal over the wave-session CR in one replay (B3+C 10.27M minus B3 8.54M); in session, where each spawn still needs a model call, about 0.2M less (B3+C''+D 9.73M against B3+C+D 9.95M). Counted inside that replay, not added: the ceremony lens's per-unit paperwork fold (1.5M), the refusal retries (0.37M) and repair delegation (3.73M alone). Once wave sessions land, delegating repairs saves no tokens (B3+D equals B3 at 8.54M), so it is carried for context discipline only. Risks: an unattended loop carries forward a warning nobody read (in run six `lane accept` moved a self-reviewed unit to Done, BG1235), so the loop stops on any warning and judgement turns stay with the model. Depends on CR0667 for headless builds and on the run-seven friction bug (lane land self-check after commit); refines BG1231 (lane land exit codes) and BG1229 and BG1237 (record refusals).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
