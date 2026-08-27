# EP0239: revert-check measures in an isolated copy, never in the live working tree

> **Status:** Draft
> **Derived Point Total:** 16
> **Parent:** CR0552
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0552. Delivers the work CR0552 requested.

## Story Breakdown

- [ ] [US0784: No tracked file in the live working tree changes at any point while the lane runs](../stories/US0784-no-tracked-file-in-the-live-working-tree.md)
- [ ] [US0785: The lane and the per-unit CLI reach the same verdict for the same reason - one measurement](../stories/US0785-the-lane-and-the-per-unit-cli-reach.md)
- [ ] [US0786: A file absent at the base ref is ABSENT from the isolated copy, not present and empty](../stories/US0786-a-file-absent-at-the-base-ref-is.md)
- [ ] [US0787: A verifier reads CURRENT tests against BASE production files, and writes nothing that escapes](../stories/US0787-a-verifier-reads-current-tests-against-base-production.md)
- [ ] [US0788: US0672's criteria are re-authored against what the new design actually promises](../stories/US0788-us0672-s-criteria-are-re-authored-against-what.md)

## Acceptance Criteria (Epic Level)

- [ ] Given the revert-check lane running at a push or release boundary, when it examines a unit, then no tracked file in the live working tree changes at any point during the run - asserted by hashing the tree continuously from a second process, not by inspecting it afterwards, because the defect is a window rather than an end state
- [ ] Given the lane and the per-unit CLI run over the same unit, when both report, then they reach the same verdict for the same reason - one measurement, not two paths that may drift
- [ ] Given a unit whose production file did not exist at the base ref, when the isolated copy is built, then that file is absent from it rather than present-and-empty, so the criterion is measured against the tree the base ref actually held
- [ ] Given the isolated copy, when a verifier runs against it, then it reads the unit's CURRENT test files and the BASE production files, and nothing it writes can reach the real repository
- [ ] Given US0672's criteria, which are written about restoring the live tree, when this lands, then they are re-authored against what the new design actually promises rather than left to pass vacuously on a tree nothing touches

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
