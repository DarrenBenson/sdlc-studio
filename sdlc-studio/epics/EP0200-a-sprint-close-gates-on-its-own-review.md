# EP0200: A sprint close gates on its own review coverage, not on an unrelated periodic ceremony

> **Status:** Done
> **Derived Point Total:** 8
> **Parent:** CR0522
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0522. Delivers the work CR0522 requested.

## Story Breakdown

- [x] [US0608: A stale repo-wide unified review no longer hard-blocks a sprint close whose own units are all covered, and is reported as cadence debt instead](../stories/US0608-a-stale-repo-wide-unified-review-no-longer.md)
- [x] [US0609: file-and-close accepts a stale periodic review as ceremony debt and files it as a real artefact linked to the run](../stories/US0609-file-and-close-accepts-a-stale-periodic-review.md)

## Acceptance Criteria (Epic Level)

- [ ] A sprint whose own units all carry independent review coverage and sign-off can close while the repo-wide unified review is stale.
- [ ] The staleness is REPORTED at close - in the close output, the retro and the close-owed ledger - never silently dropped.
- [ ] `--file-and-close` accepts a stale periodic review as ceremony debt and files it as a real artefact linked to the run.
- [ ] A sprint whose own review coverage is INCOMPLETE still blocks - the positive control, so this does not become a way to close an unreviewed batch.
- [ ] If a threshold is adopted, it is declared in config and the close states which side of it the current staleness falls on.
- [ ] A test pins that a fully-covered batch closes with a stale unified review, and that an uncovered one still refuses - the mutant is a change that makes both pass.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
