# CR-0277: reconcile apply should create a missing index from the template, not just detect it

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py
> **Date:** 2026-07-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Dogfooded during the homelab audit: reconcile detect flags a missing-index drift (e.g. reviews/_index.md absent after the first dated review file), but reconcile apply won't create it - it only fixes counts/status/rows. The agent had to hand-author the index from the template to clear real drift, which is exactly the hand-work the deterministic tooling exists to remove. The machinery already exists (`file_finding.write_empty_index` / `ensure_index` / `_ensure_meta_index).`

## Impact

A detected-but-unfixable drift: reconcile reports missing-index but offers no mechanical fix, so an operator either hand-authors the index (error-prone, off-house-style) or leaves standing drift that fails the gate. reconcile apply should create a missing index from templates/indexes/<type>.md (and the meta indexes reviews/retros), the same `write_empty_index` path artifact.py already uses - so missing-index becomes a fixable, not just detectable, kind.

## Acceptance Criteria

- [ ] reconcile apply creates a missing pipeline or meta index from its template (`write_empty_index)`, clearing the missing-index drift
- [ ] the created index matches the house style (headers, zeroed counts) so a subsequent detect is clean
- [ ] a dry-run reports it would create the index without writing

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Raised |
