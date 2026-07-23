# US0410: refine requires or inherits an Affects per story so a minted story is plannable, refusing or seeding-for-confirmation where none is given

> **Status:** Done
> **Delivers:** CR0412
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py
> **Epic:** EP0155
> **Points:** 5

## User Story

**As an** operator refining a request into delivery work
**I want** every minted story to carry an Affects
**So that** the refined backlog is plannable the moment it exists, not a set of grooming tasks
that reads as ready work

## Acceptance Criteria

### AC1: a story minted with no Affects is refused, naming what to supply

- **Given** a `refine apply` breakdown whose story gives a title and points but no Affects, and
  a project on the default policy
- **When** refine runs
- **Then** it refuses before minting anything, naming the story and how to supply an Affects,
  in the grooming-refusal idiom - it does not silently mint an unplannable unit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::AffectsRequiredAtRefineTests::test_a_story_with_no_affects_is_refused_naming_the_fix
- **Verified:** yes (2026-07-23)

### AC2: a story inherits and narrows the parent request's Affects when asked

- **Given** a request whose Affects names three files and a breakdown that asks a story to
  inherit them
- **When** refine mints the story
- **Then** the story carries an Affects derived from the parent, and a story is plannable
  (`sprint plan` does not refuse it as lacking Affects)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::AffectsRequiredAtRefineTests::test_a_story_inherits_the_parent_affects_and_is_plannable
- **Verified:** yes (2026-07-23)

### AC3: the opt-out restores the lenient behaviour deliberately

- **Given** a project that records the lenient opt-out
- **When** refine mints a story with no Affects
- **Then** it is minted with a warning rather than refused, so the change does not break a
  project that wants the old behaviour
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::AffectsRequiredAtRefineTests::test_the_opt_out_warns_instead_of_refusing
- **Verified:** yes (2026-07-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
