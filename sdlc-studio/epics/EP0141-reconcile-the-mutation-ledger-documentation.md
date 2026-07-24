# EP0141: Reconcile the mutation-ledger documentation

> **Status:** Done
> **Derived Point Total:** 4
> **Parent:** CR0385
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0385. Delivers the work CR0385 requested.

## Story Breakdown

- [x] [US0384: rewrite help/mutation.md and reference-scripts-verify.md for the ledger, content-hash key, coverage verdict and advisory lane](../stories/US0384-rewrite-help-mutation-md-and-reference-scripts-verify.md)
- [x] [US0385: reconcile trd.md and tsd.md and record the findings](../stories/US0385-reconcile-trd-md-and-tsd-md-and-record.md)

## Acceptance Criteria (Epic Level)

- [ ] help/mutation.md describes the ledger, its content-hash key, its 200-entry bound and its dropped count
- [ ] reference-scripts-verify.md describes the coverage verdict (covered / stale / uncovered) and the degraded whole-blob fallback
- [ ] trd.md and tsd.md are reconciled with the shipped behaviour, and the reconcile pass records what was found rather than only what was changed
- [ ] The docs state that the lane is advisory and never blocks, so the RFC0048 D3 decision is readable from the docs and not only from the RFC
- [ ] A reader can determine from the docs alone what makes a file's evidence stale, without reading gate.py

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
