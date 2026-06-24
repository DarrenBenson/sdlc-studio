# CR-0092: goal design assigns story points projected into the index

> **Status:** Proposed
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

**WS3 of RFC0019. Estimate: 2 points. Depends on CR0089.** The breakdown (`--goal design`)
**assigns a story-point estimate** to each story (`**Story Points:** N` in the file), so the
backlog is estimated and ready to work on (the operator's "ensure everything is ready ... and
give story point estimates"). The estimate uses the existing complexity signal (RFC0009) as a
starting point. `reconcile fields` (CR0082, already shipped) then projects the points into the
index - closing the hand-copy the field agent hit, end to end.

## Acceptance Criteria

- [ ] `--goal design` writes a `**Story Points:**` estimate into each story it produces (seeded
      from the complexity signal; the operator can override)
- [ ] `reconcile fields` projects those points into the index `Points` column (verified end to
      end against a generated backlog) - zero hand-copying
- [ ] a story left unestimated is reported, not silently zeroed
- [ ] unit tests cover point assignment + projection; CHANGELOG `[Unreleased]` entry (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
