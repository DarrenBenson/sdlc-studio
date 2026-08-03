# EP0181: reconcile's sweeps read the corpus once per run, not once per unit

> **Status:** Done
> **Derived Point Total:** 11
> **Parent:** CR0465
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0465. Delivers the work CR0465 requested.

## Story Breakdown

- [x] [US0531: The sweep detectors read the artefact corpus once per run and share it, so the cost is paid once rather than per unit](../stories/US0531-the-sweep-detectors-read-the-artefact-corpus-once.md)
- [x] [US0532: The corpus read is measured by a test that fails if it grows back to per-unit, so the fix cannot silently regress](../stories/US0532-the-corpus-read-is-measured-by-a-test.md)
- [x] [US0533: The gate attributes its seconds per lane, so a lane that becomes the dominant cost is visible without profiling it by hand](../stories/US0533-the-gate-attributes-its-seconds-per-lane-so.md)

## Acceptance Criteria (Epic Level)

- [ ] The behaviour in the summary is corrected and pinned by a test.
- [ ] The fix derives its coverage rather than enumerating it, so a new instance of the same class is caught.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
