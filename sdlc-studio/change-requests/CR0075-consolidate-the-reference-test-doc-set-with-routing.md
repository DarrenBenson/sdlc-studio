# CR-0075: consolidate the reference-test doc set with routing maps (review WS B2a)

> **Status:** Complete
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

World-class review WS B2a. The 5 `reference-test-*.md` (~2,393 lines) cross-reference heavily (~35% overlap between best-practices and validation), forcing multi-file loads. Consolidate to reduce sprawl + token cost, preserving all content.

## Acceptance Criteria

- [~] **physical merge DEFERRED** - on inspection the 5 test refs have distinct scopes (brownfield-validation / E2E / best-practices / spec / automation, per their Load-when markers); folding validation into the already-at-ceiling best-practices would make a ~980-line file for a marginal net token gain and real churn. The coherence win is captured by the routing map below instead.
- [x] a 'which test doc do I read' routing map added to `help/references.md` (the 5 files mapped to their task)
- [x] no file removed, so inbound references + budgets are unchanged; links resolve

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
