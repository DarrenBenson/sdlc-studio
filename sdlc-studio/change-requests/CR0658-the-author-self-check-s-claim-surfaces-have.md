# CR-0658: The author self-check's claim surfaces have no slot for a documentation prose file a unit ships, such as release notes

> **Status:** Superseded
> **Superseded by:** CR0652
> **Priority:** Low
> **Type:** Feature
> **Date:** 2026-11-02
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-02T09:14:44Z

## Summary

2026-11-02, US1110's builder. `critic.CLAIM_SURFACES` (critic.py:2577) is Resolutions, docstrings, comments and CHANGELOG. A unit whose deliverable is a prose document (docs/release-notes-v6.2.0.md) has no surface for that document's sentences, so the builder filed 49 release-notes claims under 'CHANGELOG' with a 'release notes:' prefix. The inventory still ran, but it was recorded under the wrong name, and a reviewer reading the record cannot tell the notes' claims from the fragment's.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Recommendation

Option 1: name the surface after what the claim is in, so the record says what was checked.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-02 | claude | Raised |
| 2026-11-14 | Claude Opus 5.5 (backlog triage, D0473) | Superseded by CR0652 at the backlog triage, as a duplicate: both ask the author self-check for a claim surface for a documentation unit's prose file; its example, a release-notes unit's 49 claims filed under CHANGELOG, is carried to CR0652 |
