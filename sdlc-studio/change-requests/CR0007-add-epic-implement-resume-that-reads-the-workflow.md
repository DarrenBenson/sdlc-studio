# CR-0007: Add epic implement --resume that reads the workflow execution table and restarts at the first non-Done story

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Requester:** Adversarial Audit
> **Date:** 2026-06-20
> **Affects:** reference-epic.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

epic implement is the heaviest autonomous workflow (auto-flips each story to Done) yet has no --resume; on mid-batch failure the only recovery is manual --story restart, unlike --resume which already exists for epic review and project implement, and unlike Spec Kit's workflow resume <run_id>.

## Problem

epic implement runs a sequential loop that auto-sets each story to Done as it completes (reference-epic.md:846) and on failure only 'Pause[s] epic workflow, report[s] error' (reference-epic.md:632-680). The documented recovery is to re-run 'epic implement --epic EP0004 --story US0024' by hand. There is no 'epic implement --resume', though --resume exists for epic review (help/epic.md:58) and project implement (help/project.md:16). A WF{NNNN}.md workflow file is created and a 'resume point' mentioned (reference-epic.md:636-639) but no flag wires deterministic resumption to it, so the operator must read the status table and reconstruct the starting story. Spec Kit persists run state and offers resume <run_id> from the exact interruption point.

## Proposed Changes

### Item 1: Add epic implement --resume that reads the workflow execution table and restarts at the first non-Done story

**Priority:** High **Effort:** TBD

Add 'epic implement --resume' that reads the WF{NNNN}.md execution table, skips stories already in Done, and restarts at the first non-Done story (mirroring project implement --resume). Persist a compact JSON run-state (current wave/story index, per-story status) under .local/ so resumption is deterministic rather than reconstructed from prose.

## Impact Assessment

### Existing Functionality

On a mid-batch failure of a 5+ story epic the operator must manually identify the failed story and re-issue --story, risking double-execution of already-Done stories or skipping a Blocked one. SDLC Studio's flagship autonomous command is the one workflow that cannot resume from the interruption point. Quality risk high; bounded change mirroring an existing flag.

## Acceptance Criteria

- [ ] Change implemented and verified; lint and tests green.

## Out of Scope

- Implementation is downstream; this CR records the audit finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Adversarial Audit | Filed from the 2026-06-20 audit (lens: external-benchmark; evidence: reference-epic.md:846 (auto-Done) and :632-680 ('On failure: Pause epic workflow, report error') vs help/epic.md:58 + help/project.md:16 (--resume exists only for review/project, not epic implement)) |
