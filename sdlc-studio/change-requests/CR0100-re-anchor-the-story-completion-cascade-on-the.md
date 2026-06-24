# CR-0100: Re-anchor the Story Completion Cascade on the deterministic close (artifact.py close / transition.py)

> **Status:** Complete
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-06-24
> **Created-by:** sdlc-studio file

## Summary

reference-outputs.md#story-completion-cascade narrates hand-editing the story Status, the per-epic + All Stories index rows, the summary counts, and the parent-epic Story-Breakdown checkbox - exactly what transition.py / artifact.py close now do deterministically, contradicting the tool-first doctrine. Scoped narrowly: the model still owns the judgement residue (downstream dependency tables, epic-Done suggestion, terminal-reason, github_sync).

## Acceptance Criteria

- [x] The cascade leads with a single mechanical step naming artifact.py close --id US<NNNN> (or transition.py set) and tells the agent NOT to hand-edit the Status, index rows, summary counts, or epic checkbox
- [x] The remaining narrated steps are limited to work the scripts do not cover and are labelled as residue, not the primary mechanism
- [x] The #story-completion-cascade anchor is preserved and check_links.py still passes (referenced from reference-code.md/story.md/reconcile.md)
- [x] CHANGELOG [Unreleased] entry in the same commit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | audit | Raised |
