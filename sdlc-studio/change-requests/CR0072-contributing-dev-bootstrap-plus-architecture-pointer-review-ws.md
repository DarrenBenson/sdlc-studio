# CR-0072: CONTRIBUTING dev bootstrap plus architecture pointer (review WS B3b)

> **Status:** Complete
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

World-class review WS B3b. CONTRIBUTING.md is sparse (style rules only). A new contributor lacks a dev bootstrap: the gating discipline, the bug->CR lifecycle, the regression-test obligation, and a pointer to the architecture.

## Acceptance Criteria

- [x] CONTRIBUTING.md gains a Development Workflow section: trunk-based + `npm run lint && npm test && gate` before every commit
- [x] documents the bug->CR lifecycle + numbering, the regression-test obligation (every Bug ships a test), and forward-port-to-install-targets
- [x] points to the architecture (best-practices/architecture.md) and AGENTS.md doctrine

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
