# RETRO-0127: Jonah's team installs v6 via Claude Code or Copilot CLI; migrate predicts the gate's reconcile, conformance, validate and floor failures

> **Date:** 2026-09-30
> **Batch:** BG0842, BG0844, BG0843, BG0845, BG0853, BG0854, BG0856

## Keep

- The goal review before any code: all three seats rejected an over-claiming goal in round 1, and the regroom added BG0854, the end-to-end unit that now proves the goal (migrate and gate agree 3/2/4/2 on a committed v4.1 project).
- Reviews on a detached worktree at the unit's commit let the next build run in the main tree at the same time with no tree contention, and the rejecting reviewer re-judged its own repair every time.

## Stop

- Filing every non-blocking review note as its own Low: CR0592 took eleven this run and grows faster than anything drains it.

## Try

- [LC-002] Four of nine round-1 REJECTs were probes outside the unit's fixture (a second folder a tool reads, a ./ prefix, a lost test pin, a waiver); before asking for review, add one fixture per path form the criterion's words cover.
- [new: suite verdict before the commit] A suite verdict authorises only the commit it ran at. Run the full suite after committing and read `run-suite --check` at your own sha before reporting green.
- [LC-003] Since US0918 retired the review-batch verbs nothing opens a delivery batch, so every Raised-in-batch stamp and the close's placement figure are fed by nothing (BG0861); when a verb is retired, grep for the functions only it called.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG0850 | not-stop-ship | Claude (orchestrator), operator ruling D0288 | 2026-09-30 |
| BG0855 | deferred | Claude (orchestrator) | 2026-09-30 |
| BG0857 | not-stop-ship | Claude (orchestrator) | 2026-09-30 |
| BG0858 | not-stop-ship | Claude (orchestrator) | 2026-09-30 |
| BG0859 | not-stop-ship | Claude (orchestrator), operator ruling 2026-09-30 | 2026-09-30 |
| BG0860 | not-stop-ship | Claude (orchestrator) | 2026-09-30 |
| BG0861 | not-stop-ship | Claude (orchestrator) | 2026-09-30 |
| CR0592 | deferred | Claude (orchestrator) | 2026-09-30 |
