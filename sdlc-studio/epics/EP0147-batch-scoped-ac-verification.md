# EP0147: Batch-scoped AC verification

> **Status:** Draft
> **Derived Point Total:** 6
> **Parent:** CR0395
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0395. Delivers the work CR0395 requested.

## Story Breakdown

- [ ] [US0394: verify_ac run accepts an id list, a worklist or the run-state batch](../stories/US0394-verify-ac-run-accepts-an-id-list-a.md)
- [ ] [US0395: the scoped report merges rather than replaces, shared-story verdicts identical to the unscoped run](../stories/US0395-the-scoped-report-merges-rather-than-replaces-shared.md)

## Acceptance Criteria (Epic Level)

- [ ] `verify_ac run` accepts a batch: a list of ids, a worklist file, or the current run state's batch.
- [ ] The report it writes MERGES with the existing report rather than replacing it, so a scoped run does not blank the verdicts for stories outside the scope.
- [ ] The scoped and unscoped runs produce identical verdicts for the stories they share.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
