# CR-0411: sprint plan should offer sequential or parallel delivery at run start, and only offer parallel when the batch can actually be parallelised

> **Status:** Complete
> **Decomposed-into:** EP0154
> **Priority:** High
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/reference-sprint.md,.claude/skills/sdlc-studio/reference-delivery.md
> **Date:** 2026-07-23
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; operator request during RUN-01KY5Y3W, filed by Claude Opus 4.8

## Summary

Operator request, made while watching a sprint deliver ten epics and bugs by fanning them out to parallel worktree builders. That fan-out is the behaviour the operator wants offered by default at the START of a run, rather than reached ad hoc by the agent partway through.

The ask: when a sprint run commences, the operator is asked which delivery mode they want - SEQUENTIAL (one unit at a time, one context) or PARALLEL (file-disjoint clusters fanned out to isolated worktree builders, merged and reviewed in waves). The choice is deterministic and explicit, not left to the agent to infer.

The crucial constraint, in the operator's words: only offer parallel when the batch can actually be parallelised. A single story, or a batch whose units are all coupled through shared files, or one with too many dependencies to split, has no parallel form worth offering - and offering it there is a false choice that wastes the operator's attention and invites a fan-out that will only conflict on merge. So the prompt is CONDITIONAL: `sprint plan` already computes the shared-file clusters and the dependency waves, so it already knows whether a genuine parallel decomposition exists. It should offer the choice only when it does, and say plainly when it does not and why (one unit; one coupled cluster; a dependency chain with no width).

This run is the evidence for both halves. The parallel fan-out delivered six file-disjoint clusters (two epics, four bugs) concurrently and correctly. But the coupled core - everything sharing critic.py or sprint.py - could NOT be parallelised, and the one place the clustering under-counted coupling (it excluded test files) produced a real three-file merge conflict that had to be resolved by hand. A determination the tool makes deterministically, surfaced as a choice at plan time, would have set the operator's expectation correctly and kept the agent from having to decide the mode itself.

## Impact

Every sprint run, and the operators who run them. Today the delivery mode is an implicit decision the agent makes, so two runs of the same batch can be delivered differently depending on what the agent infers, and an operator who wants one mode has no deterministic point at which to ask for it. Worse, the agent may fan out a batch that cannot be safely parallelised (all-coupled, or a lone unit) and hit the merge conflicts this very run hit. A conditional prompt at plan time makes the mode an operator decision, makes the parallelisability a computed fact rather than a guess, and refuses to offer a parallel path that does not exist.

## Acceptance Criteria

- [ ] sprint plan, at run start, offers the operator a SEQUENTIAL or PARALLEL delivery mode when the batch has a genuine file-disjoint decomposition, and records the chosen mode on the run.
- [ ] The parallel option is offered ONLY when a real parallel decomposition exists: more than one unit, at least two clusters with disjoint file sets, and the dependency waves permit concurrency. A one-unit batch, an all-coupled batch, or a pure dependency chain is delivered sequentially and the prompt says why parallel was not offered.
- [ ] The file-disjointness that decides parallelisability counts TEST files as coupling, not only source - this run's one merge conflict came from excluding them, and two agents editing the same test file conflict exactly as two editing the same module do.
- [ ] The decision is deterministic: the same batch and repo state offer the same choice every time, computed from the shared-file clusters and dependency waves sprint plan already derives, not from agent judgement.
- [ ] The chosen mode is recorded on the run state and stated in the plan output, so a reader can see which mode a run used and why the alternative was or was not available.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | Darren Benson | Raised |
