# US0628: a unit closed over a REJECT names, in its own record, the artefact its findings were filed to

> **Status:** Ready
> **Delivers:** CR0526
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0206
> **Points:** 2
> **Depends on:** US0627
> **Persona:** Maya Okafor

## User Story

**As a** later reader of a closed story
**I want** a story or bug closed over a REJECT to name the filed artefact in its own record
**So that** the discharge is visible on the artefact rather than only in a verdict ledger nobody opens

## Acceptance Criteria

### AC1: a story closed over a REJECT names the filed artefact

- **Given** a story closed over a REJECT by filing BGxxxx
- **When** the story is read back
- **Then** its own record names BGxxxx
- **Mutant:** record the id in the verdict ledger alone
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ClosedOverRejectNamesTheBugTests::test_the_story_names_the_filed_artefact

### AC2: a bug closed the same way names it too

- **Given** a bug set to Fixed over a REJECT discharged by filing
- **When** the bug is read back
- **Then** its record names the filed artefact on the same terms
- **Mutant:** name it on stories only
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ClosedOverRejectNamesTheBugTests::test_a_bug_names_the_filed_artefact

### AC3: an ordinary close writes no such line

- **Given** a unit closed with no REJECT against it
- **When** it is read back
- **Then** it carries no discharge line - a marker on every close is one no reader looks at
- **Mutant:** write the line unconditionally
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ClosedOverRejectNamesTheBugTests::test_an_ordinary_close_writes_no_discharge_line

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-15 | sdlc-studio | Retitled: was 'a story closed this way names the bug in its own record' |
| 2026-09-15 | sprint planning 2026-09-15 | Re-groomed at the sprint goal review (round 1: all three seats refused a goal carrying CR0526) against D0193 (an unfinished unit feeds the close's stop-ship step, not a third gate) and D0194 (one stop-ship store, the retro's carried table). A bug closed over a REJECT names its filed artefact too; the stop-ship-ruling criterion is gone with D0194. |
