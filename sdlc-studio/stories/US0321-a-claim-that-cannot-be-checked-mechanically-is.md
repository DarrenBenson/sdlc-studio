# US0321: A claim that cannot be checked mechanically is reported UNVERIFIABLE rather than assumed true, so the reader sees how much prose rests on trust

> **Status:** Draft
> **Delivers:** CR0393
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py
> **Epic:** EP0109
> **Points:** 2

## User Story

**As an** operator weighing a review
**I want** an unprovable claim reported as UNVERIFIABLE rather than assumed true
**So that** I can see how much of the prose rests on trust instead of on evidence

## Acceptance Criteria

### AC1: an unverifiable claim is its own category, never folded into TRUE

- **Given** a claim inventory holding one claim no command can settle
- **When** the pass is summarised
- **Then** it is reported UNVERIFIABLE and counted separately, and the summary states how
  many claims rest on trust - a claim silently ruled TRUE because nothing contradicted it is
  the failure this pass exists to surface
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ClaimInventoryTests::test_an_unverifiable_claim_is_counted_separately_from_true

### AC2: a round of only unverifiable claims is not reported as a clean round

- **Given** a claim pass whose every ruling is UNVERIFIABLE
- **When** the round's outcome is rendered
- **Then** it does not read as verified, because nothing was checked - a pass with no FALSE
  rulings and no evidence is indistinguishable from one that looked and found nothing, and
  the two must not print the same
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ClaimInventoryTests::test_an_all_unverifiable_pass_does_not_render_as_verified

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
