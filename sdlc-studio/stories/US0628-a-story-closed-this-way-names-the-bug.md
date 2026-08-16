# US0628: a story closed this way names the bug in its own record

> **Status:** Ready
> **Delivers:** CR0526
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0206
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** later reader of a closed story
**I want** a story closed over a REJECT to name the filed bug in its own record
**So that** the discharge is visible on the artefact rather than only in a verdict ledger nobody opens

## Acceptance Criteria

### AC1: the closed story names the artefact that discharged it

- **Given** a story closed over a REJECT by filing BGxxxx
- **When** the story is read back
- **Then** its own record names BGxxxx - a discharge recorded only in the verdict ledger is invisible to the person reading the story
- **Mutant:** record the id in the ledger alone - the story reads as cleanly closed and the reader never learns why
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ClosedOverRejectNamesTheBugTests::test_the_story_names_the_filed_artefact

### AC2: a story closed by a stop-ship ruling names the ruling

- **Given** a story closed over a REJECT by an explicit ruling rather than a filed id
- **When** the story is read back
- **Then** its record names the ruling and who made it, on the same terms
- **Mutant:** name the ruling without its author - a judgement nobody owns is one nobody can question
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ClosedOverRejectNamesTheBugTests::test_a_ruling_is_named_with_its_author

### AC3: an ordinary close writes no such line

- **Given** a story closed with no REJECT against it
- **When** the story is read back
- **Then** it carries no discharge line - a marker that appears on every close is one no reader looks at
- **Mutant:** write the line unconditionally - it stops meaning anything
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::ClosedOverRejectNamesTheBugTests::test_an_ordinary_close_writes_no_discharge_line

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
