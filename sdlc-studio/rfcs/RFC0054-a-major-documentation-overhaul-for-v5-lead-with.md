# RFC-0054: a major documentation overhaul for v5 - lead with the two-backlog model (discovery vs delivery) and sprint planning, the changes that most reshape how the skill is used

> **Status:** Draft
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Summary

v5 is a semver-major release and the documentation has grown by accretion, one reference file per feature, with no single narrative an operator can read to understand how the pieces fit. The headline v5 changes - the two-backlog model (a request in the DISCOVERY backlog becomes DELIVERY work only by being refined into sized units) and the sprint-planning flow (breakdown gate, delivery-mode/lane partition, capacity/appetite, the goal-driven autosprint) - are the ones that most change how the skill is used, and they are currently explained only in scattered reference-*.md files and the doctrine. This RFC plans the overhaul: a top-down narrative that a new operator reads once, with the reference files demoted to the detail they already hold.

## Design Options

- **Option A** {{...}}

## Recommendation

C - ship the narrative two-backlog + sprint-planning guide for v5 (the release-blocking documentation gap), then restructure the reference tree as a follow-up. Decompose into: a two-backlog concept page, a sprint-planning walkthrough, a lifecycle overview, and a README/SKILL.md front-door rewrite that points at them.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | {{decision}} | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
