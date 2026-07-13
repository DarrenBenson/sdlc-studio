# CR-0239: Commit-id convention for per-id file attribution in the engagement floor

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Dani Okafor; persona; 4.0.0

## Summary

The engagement floor's git cross-check (git log --grep=<id>) cannot attribute a file to one id when a commit names several judged ids, so it skips such batch commits to avoid over-firing. As a result, understatement (a unit declares one file in Affects but the change touched more) escapes the floor whenever the unit shares its commit with another judged id - the norm in real sprints. git log alone lacks the information to apportion files per id.

## Impact

The engagement-floor lane does not catch Affects understatement for a unit committed alongside another judged id. Pure omission and solo-id-commit understatement are already caught; this closes the shared-commit understatement gap. No runtime code path - a commit-message discipline plus a commit-msg hook and a reader that maps a commit to a single id.

**Effort:** M

## Acceptance Criteria

- [ ] A per-commit id association exists (a Refs: <id> trailer or a one-id-per-commit rule) that maps each commit to exactly one judged id
- [ ] The engagement floor reads that association so a change's files attribute to the declaring unit even in a shared batch, catching understatement in a shared commit
- [ ] A commit-msg hook (advisory off the skill repo) nudges the convention; absence degrades gracefully to today's solo-id behaviour

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | Dani Okafor | Raised |
