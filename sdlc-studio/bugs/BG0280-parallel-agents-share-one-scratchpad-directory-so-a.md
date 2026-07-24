# BG0280: parallel agents share one scratchpad directory, so a commit-message file written by one can be overwritten by another between write and commit: a commit landed carrying a different agent's subject

> **Status:** Open
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-delivery.md,.claude/skills/sdlc-studio/scripts/sprint.py
> **Severity:** Medium
> **Points:** 2

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Detail

Reported by a build agent during the Sprint 2 parallel fan-out, and it actually happened rather
than being theorised:

> The shared scratchpad path is being written by a parallel agent - my message file was
> overwritten between write and commit, and the first commit landed with *another agent's*
> subject.

The agent recovered by amending with a session-unique filename, but the wrong-subject commit
existed first, and a less careful run would have shipped it.

**Why nothing caught it.** The delivery-mode disjointness analysis reasons entirely about files
IN THE REPOSITORY, derived from each unit's `Affects` and its `Verify:` targets. Agents running in
isolated git worktrees are genuinely disjoint in the repo - and then all write to ONE shared
scratchpad directory outside it. Isolation of the tree is not isolation of the workspace.

This is a sibling of the build-tooling coupling already filed: both are shared state the analysis
does not model because it is not a repo file. Here the shared thing is a temp directory; there it
is the gate. A merge conflict is the failure mode the analysis was designed for, and neither of
these produces one.

## Impact

Any parallel fan-out. The damage is silent and mis-attributing: a commit message describes work it
does not contain, so `git log` - which the engagement floor and every later reader trust - becomes
wrong. Recovery needs an amend, which is itself awkward once the commit is pushed.

## Acceptance Criteria

### AC1: a per-agent scratchpad path, not one shared directory

- **Given** two or more agents delivering the same batch in parallel
- **When** each writes a temporary file (a commit message, a fields-file, a worklist)
- **Then** their paths cannot collide, because each is namespaced per agent or per run
- **Verify:** manual

### AC2: the parallel-delivery contract names workspace isolation, not just file disjointness

- **Given** a reader of the delivery-mode documentation
- **Then** it states that a worktree isolates the TREE and not the scratchpad, and that any shared temp path must be namespaced - so the next fan-out does not rediscover this
- **Verify:** manual

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Fixed: the contract is stated in reference-delivery.md and the agent-prompt template, where a delegating agent meets it |
