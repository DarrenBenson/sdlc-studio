# RFC-0054: a major documentation overhaul for v5 - lead with the two-backlog model (discovery vs delivery) and sprint planning, the changes that most reshape how the skill is used

> **Status:** Superseded
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Summary

v5 is a semver-major release and the documentation has grown by accretion, one reference file per feature, with no single narrative an operator can read to understand how the pieces fit. The headline v5 changes - the two-backlog model (a request in the DISCOVERY backlog becomes DELIVERY work only by being refined into sized units) and the sprint-planning flow (breakdown gate, delivery-mode/lane partition, capacity/appetite, the goal-driven autosprint) - are the ones that most change how the skill is used, and they are currently explained only in scattered reference-*.md files and the doctrine. This RFC plans the overhaul: a top-down narrative that a new operator reads once, with the reference files demoted to the detail they already hold.

## Design Options

- **Option A** - the in-repo documentation overhaul this RFC was raised to plan. It was
  never elaborated: the RFC was superseded before its options were written out, and the
  paragraph below records what happened instead. Stated rather than left as a scaffold,
  because a design record with a blank option reads as an option nobody considered.

**Superseded by the sdlc-studio.com website.** The v5 documentation overhaul this RFC planned (a narrative two-backlog + sprint-planning guide, lifecycle overview, front-door rewrite) was delivered instead as the standalone site at sdlc-studio.com under the site-only-docs decision: getting-started, the two-backlog and sprint-planning concept pages, an end-to-end walkthrough, a comparison table and a multi-harness page all live there, canonical, rather than in the repo. Kept for the design record; the live artefact is the website.

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
