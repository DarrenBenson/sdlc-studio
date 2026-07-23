# US0411: a refined story's AC block is labelled a grooming placeholder, not left as content, so the ungroomed count is machine-visible

> **Status:** Review
> **Delivers:** CR0412
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py,.claude/skills/sdlc-studio/scripts/conformance.py
> **Epic:** EP0155
> **Points:** 3

## User Story

**As a** reader of a refined backlog
**I want** an ungroomed story's criteria labelled as a placeholder, not left as content
**So that** I can tell a groomed story from an ungroomed one at a glance and count the
ungroomed units mechanically

## Acceptance Criteria

### AC1: a refined story's AC block is a labelled grooming placeholder

- **Given** a story minted by refine with no authored criteria
- **When** the story is written
- **Then** its acceptance-criteria block carries an explicit ungroomed marker rather than a
  bare double-brace placeholder that reads as real content
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::UngroomedMarkerTests::test_a_refined_story_carries_an_ungroomed_marker

### AC2: the ungroomed count is machine-visible

- **Given** a mix of groomed and ungroomed stories
- **When** conformance or a status pass counts them
- **Then** the ungroomed ones are counted by the marker, so an operator sees how much
  grooming a refined backlog still owes rather than discovering it at plan time
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::UngroomedMarkerTests::test_ungroomed_stories_are_counted_by_their_marker

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
