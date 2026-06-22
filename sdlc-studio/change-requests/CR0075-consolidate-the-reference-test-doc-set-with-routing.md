# CR-0075: consolidate the reference-test doc set with routing maps (review WS B2a)

> **Status:** Proposed
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

World-class review WS B2a. The 5 `reference-test-*.md` (~2,393 lines) cross-reference heavily (~35% overlap between best-practices and validation), forcing multi-file loads. Consolidate to reduce sprawl + token cost, preserving all content.

## Acceptance Criteria

- [ ] fold `reference-test-validation.md` into `reference-test-best-practices.md` (dedup the overlap), preserving all unique guidance
- [ ] add a one-line 'which test doc do I read' routing map atop the remaining test references
- [ ] update every inbound reference (help/references.md, SKILL.md, cross-links) + the check_budgets allowlist; links resolve

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
