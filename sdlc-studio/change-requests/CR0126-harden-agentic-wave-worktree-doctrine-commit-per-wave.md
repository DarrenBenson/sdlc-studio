# CR-0126: harden agentic-wave worktree doctrine: commit-per-wave, cherry-pick order, forward-scaffold

> **Status:** Complete
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/reference-agentic-lessons.md
> **Depends on:** -

## Summary

Distilled from a consuming repo's project lessons log (EP0037-0041), which repeatedly lost time to
worktree-based agentic waves. `reference-agentic-lessons.md` already covers Wave-1-sequential and the
two-parallel sweet spot, but four hard-won rules surfaced there are not yet in the skill, so every
new project rediscovers them:

1. **Stale-HEAD: commit per WAVE, not per epic.** `Agent({ isolation: 'worktree' })` branches from a
   cached HEAD captured at an earlier agent-tool invocation, not current main. a consuming repo EP0040
   Wave 2 agents branched pre-Wave-1 and could not see the types/files they were told to replace
   (~20 min hand-diff to merge); EP0041 hit it again despite per-epic commits. The existing per-epic
   commit rule must tighten to **commit every wave to main before launching the next wave's worktree
   agents**, and recovery when it still happens is `git diff HEAD -- <files>` then `git apply` on
   main, not re-running the agent.
2. **Default single-agent-on-main; parallel worktrees are the exception.** Opt into parallel only
   when (a) both stories have hermetic file scopes (zero shared hub files), (b) combined story points
   exceed ~10 SP so parallel saves material wall-clock, and (c) the merge plan is written BEFORE
   launch. Below that, the merge overhead exceeds the throughput gain (EP0041's 19 SP shipped in 6
   sequential waves in roughly the wall-clock of a botched 3-parallel run).
3. **Cherry-pick worktree branches by scope narrowness, not SP or story number.** Surgical changes
   merge cleanly atop larger additions; the reverse creates 3-way conflicts (EP0037 Wave 1).
4. **Wave 1 forward-declares every shared type / interface / hub-file addition** the later waves
   consume, so Waves 2+ implement against a scaffold and never touch the shared file (EP0040 adapter
   parallelism worked because of this; the absence of it caused the EP0040 Wave-2 re-declaration mess).

These are agentic-execution doctrine, not project facts, so they belong in the skill where every
project benefits. Pairs with [[LL0007]] (plan from value) on the planning side.

## Acceptance Criteria

- [ ] `reference-agentic-lessons.md` Wave Structure section adds the **commit-per-wave** rule
      (HEAD must include all prior waves before any worktree branch) plus the `git apply` recovery
      pattern for stale-HEAD
- [ ] the same file states **single-agent-on-main as the default** and lists the three explicit
      opt-in-to-parallel criteria (hermetic scope, >~10 SP, merge plan pre-written)
- [ ] a **cherry-pick ordering** rule (narrowest scope first) is documented with the rationale
- [ ] a **Wave-1 forward-scaffold** rule is documented: Wave 1 enumerates types/interfaces/fixture
      surface that later waves consume; Waves 2+ implement against it
- [ ] the Agent Prompt Template guidance references the forward-scaffold enumeration so it lands in
      generated prompts
- [ ] **deterministic where possible** ([[LL0008]]): the commit-per-wave precondition is expressed as
      a mechanical pre-launch check (HEAD includes all prior waves' commits) rather than prose an
      agent must remember; the forward-scaffold file set is derived from `scripts/repo_map.py`, not
      memory; anything that stays advisory is named as such with the reason
- [ ] CHANGELOG `[Unreleased]` entry ([[LL0004]]); no broken anchors (link checker green)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-27 | field | Created via `new` (deterministic) |
