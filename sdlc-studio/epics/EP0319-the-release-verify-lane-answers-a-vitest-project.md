# EP0319: The release verify lane answers a vitest project's criteria from one batched vitest run

> **Status:** Draft
> **Derived Point Total:** 6
> **Parent:** CR0638
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0638. Delivers the work CR0638 requested.

## Story Breakdown

- [ ] [US1179: verify_ac resolves file-scoped vitest criteria from one batched vitest JSON run, with vitest stubbed in the test](../stories/US1179-verify-ac-resolves-file-scoped-vitest-criteria-from.md)
- [ ] [US1180: The release verify lane reads the vitest batch, falls back per criterion where it cannot answer, and the two agree](../stories/US1180-the-release-verify-lane-reads-the-vitest-batch.md)

## Acceptance Criteria (Epic Level)

- [ ] In a vitest project the release verify lane resolves file-scoped vitest criteria from one batched vitest JSON run, falls back per criterion only where the batch cannot answer, and a fixture corpus shows the batch and the per-criterion answers agree. The stories refine writes carry the executable checks.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
