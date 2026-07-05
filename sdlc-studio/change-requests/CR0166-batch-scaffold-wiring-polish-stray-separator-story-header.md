# CR-0166: batch scaffold wiring polish: stray separator, story header format, empty by-epic table

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-07-05
> **Created-by:** sdlc-studio file

## Summary

Three cosmetic tool-wiring edges from the v3.5.0 eval run (scenario 02 worker + grader, fresh greenfield chain): (1) artifact.py batch epic wiring inserts story links directly after the 'To be generated' placeholder, leaving a stray --- an agent tidies by hand; (2) the full-template story scaffold header emits a bare 'Epic: EP0001' line and a raw persona placeholder where templates/core/story.md uses a linked epic and persona name; (3) artifact.py batch creates a Stories by Epic table with a header but no rows while All Stories is populated. None cause drift (validate 0, reconcile 0) - pure scaffold polish.

## Acceptance Criteria

- [ ] batch epic wiring replaces the placeholder line instead of appending after it (no stray separator)
- [ ] the full-template story header matches templates/core/story.md (linked epic, persona)
- [ ] batch either populates Stories by Epic or omits the empty table; regression tests on a two-epic four-story batch fixture

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-05 | audit | Raised |
