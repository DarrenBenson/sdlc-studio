# EP0180: Tooling gaps that block the work they are meant to serve

> **Status:** Done
> **Parent:** CR0457
> **Parent:** CR0456
> **Derived Point Total:** 15
> **Parent:** CR0460
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0460. Delivers the work CR0460 requested.

## Story Breakdown

- [x] [US0525: The conformance lane reads recorded waivers and reports a waived unit as waived, naming the decision](../stories/US0525-the-conformance-lane-reads-recorded-waivers-and-reports.md)
- [x] [US0526: A waiver naming no reason or an unknown rule is refused at record time rather than silently doing nothing](../stories/US0526-a-waiver-naming-no-reason-or-an-unknown.md)
- [x] [US0527: validate can be pointed at one artefact, so checking a story does not read the whole workspace](../stories/US0527-validate-can-be-pointed-at-one-artefact-so.md)
- [x] [US0528: A Draft story declaring a file it will create is not warned as unresolvable, since that is the normal case](../stories/US0528-a-draft-story-declaring-a-file-it-will.md)
- [x] [US0529: init creates the issues directory and its index, so the issue type is usable on a new project](../stories/US0529-init-creates-the-issues-directory-and-its-index.md)
- [x] [US0530: The artefact tree init creates is derived from the shipped type list, so a new type is never silently omitted](../stories/US0530-the-artefact-tree-init-creates-is-derived-from.md)

## Acceptance Criteria (Epic Level)

- [ ] conformance reads the recorded waivers and reports a waived unit as waived rather than non-conformant, naming the decision that waived it.
- [ ] A waiver that names no reason, or names a rule that does not exist, is refused at record time rather than silently doing nothing.
- [ ] The gate's remedy text and the behaviour agree: if it recommends a waiver, a waiver must clear the lane.

### From CR0456

- [ ] The behaviour described in the summary is corrected and pinned by a test.
- [ ] The fix derives its coverage rather than enumerating it, so a new instance of the same class is caught.

### From CR0457

- [ ] The behaviour described in the summary is corrected and pinned by a test.
- [ ] The fix derives its coverage rather than enumerating it, so a new instance of the same class is caught.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
