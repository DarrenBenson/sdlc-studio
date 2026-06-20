# RFC-0006: Reconsider the default autonomous execution model: phase-gating and per-story fresh-context isolation for sequential epic implement

> **Status:** Withdrawn
> **Priority:** Medium
> **Author:** Adversarial Audit
> **Date:** 2026-06-20
> **Spans:** sdlc-studio skill
> **Related:** RV0002 (audit run)
> **Supersedes / Superseded by:** --

## Summary

The default sequential epic implement runs each story inline in the same conversation (heavy reference files accrete) and the doctrine actively discourages mid-pipeline stops, so there is no human approval checkpoint between phases and no per-story context isolation - both contrary to Kiro/Spec Kit phase gates and BMAD's single-story sharding.

## Context & Problem

Two related autonomy-model gaps. (1) No human approval checkpoint between requirements/design/tasks phases: the pipeline spans 11 artifact types but reference-doctrine.md:83 says 'Don't stop mid-execution once a plan is approved'; the only structured gates (review, consult) are optional and post-hoc, not blocking transitions. No command refuses to generate a Story until its parent Epic is explicitly approved. Kiro requires explicit approval of requirements/design/tasks before each next phase; Spec Kit interposes clarify/analyze before implement. (2) No per-story fresh-context isolation in sequential epic implement: each story runs via an inline '/sdlc-studio story implement' call in the SAME conversation holding the epic plan, prior stories' output, and the workflow table (reference-epic.md:670), so heavy reference files (52-100KB per invocation) accrete across stories. Only the --agentic path gets worktree+fresh-agent isolation (reference-epic.md:691-693), so the default, most-used path violates the context-isolation principle BMAD was built around.

## Design Options

### Option A - act on the finding

Decide the default execution model. Option for phase-gating: an optional --require-approval mode where story create refuses unless the parent epic carries Approved status and epic implement refuses unless every story is Approved (not merely Ready). Option for context hygiene: let sequential epic implement dispatch each story to a fresh sub-agent (Agent tool, no worktree) so each story loads only its own scoped context, matching the agentic path's isolation without git-worktree machinery. RFC because both trade SDLC Studio's automation-first, inline-continuity doctrine against Kiro/Spec Kit human checkpoints and BMAD's sharding - an unsettled change to the default model.

### Option B - status quo

Keep the current behaviour and accept the trade-off described above.

## Recommendation

TBD - pending the Open Decision below.

## Open Decisions

| # | Decision | Options | Owner | How it resolves | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | Act on this finding or keep status quo | Option A / Option B | Operator | spike or operator call | Open |

## Evidence

reference-doctrine.md:83 ('Don't stop mid-execution once a plan is approved') and reference-epic.md:670 (sequential loop runs inline '/sdlc-studio story implement' in same context) vs reference-epic.md:691-693 (agentic path: worktree-isolated fresh agent)

## Impact

In autonomous runs an inaccurate PRD or design flaw propagates uninterrupted with no phase blocking on sign-off, and a 5-10 story sequential run accumulates tens of KB of stale context per story, degrading later-story quality and inflating tokens - the exact failure BMAD's sharding eliminates, present only in the path most operators use. Quality and token risk medium.

## Decision

**Outcome:** TBD
**Rationale:** TBD

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Adversarial Audit | Filed from the 2026-06-20 audit (lens: external-benchmark) |
| 2026-06-20 | Autosprint (backlog-closeout) | Withdrawn - RFC0001 (Accepted) settled the default autonomy model (D1: stop-after-triage then autonomous); reopening it is out of scope. |
