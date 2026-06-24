# CR-0106: sprint plan should scope a story batch by epic, not only by status

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-24
> **Created-by:** sdlc-studio file

## Summary

sprint plan filters only by status (--stories Draft), so planning the next tranche for specific epics (EP0002+EP0003) pulls ALL Draft stories across every epic. A field agent planning the next sprint hit this: --stories Draft grabbed 25 stories, forcing it to hand-scope and hand-build the waves instead of using plan --write for the real scope. Add --epic EPxxxx (repeatable) so a sprint can be planned for one or more epics.

## Acceptance Criteria

- [x] sprint plan --stories <status> --epic EPxxxx [--epic EPyyyy] restricts the batch to stories whose Epic field is in the given set
- [x] --epic is repeatable (union); --epic with --crs/--bugs errors clearly (epic-scoping is story-only)
- [x] the dependency ordering, --write artifact, and WSJF all operate on the scoped batch; unit test covers single + multi epic scoping
- [x] documented in reference-sprint.md + help/sprint.md; CHANGELOG entry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | audit | Raised |
