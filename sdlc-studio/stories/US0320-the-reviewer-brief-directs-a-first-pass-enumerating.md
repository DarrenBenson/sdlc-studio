# US0320: The reviewer brief directs a first pass enumerating every assertion in Resolutions, docstrings, comments and CHANGELOG entries, marked TRUE, FALSE or UNVERIFIABLE

> **Status:** Done
> **Delivers:** CR0393
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-review.md
> **Epic:** EP0109
> **Points:** 3

## User Story

**As an** adversarial reviewer
**I want** to inventory every assertion the diff's prose makes before I read its logic
**So that** the cheapest thing in the diff to check, and the likeliest to be wrong, is not
the last thing I get to

## Acceptance Criteria

### AC1: the brief directs an enumerated claim pass over all four prose surfaces

- **Given** a review brief for a diff
- **When** it is parsed
- **Then** it directs a first pass enumerating assertions in Resolutions, docstrings,
  comments and CHANGELOG entries - all four named, since a pass that omits one exempts it,
  and a Resolution is the artefact no test can fail
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ClaimInventoryTests::test_the_brief_names_all_four_prose_surfaces
- **Verified:** yes (2026-07-23)

### AC2: every enumerated claim carries a ruling

- **Given** a claim inventory listing six assertions with five rulings
- **When** it is recorded
- **Then** it is refused and names the unruled claim, each ruling being TRUE, FALSE or
  UNVERIFIABLE
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ClaimInventoryTests::test_a_claim_left_unruled_is_refused
- **Verified:** yes (2026-07-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
