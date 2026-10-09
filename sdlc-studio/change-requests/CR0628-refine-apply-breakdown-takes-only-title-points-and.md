# CR-0628: refine apply --breakdown takes only title, points and affects, so every story's persona, criteria and Verify lines are re-typed by hand after minting

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine_breakdown_fields.py, .claude/skills/sdlc-studio/help/refine.md, .claude/skills/sdlc-studio/scripts/tests/test_refine.py
> **Evidence:** D0355 breakdown, 2026-10-09: twelve groups drafted as JSON with per-story persona, user story, criteria and Verify selectors; refine.py:416 `_BREAKDOWN_STORY_KEYS = {"title", "points", "affects"}` refuses every other key, while `artifact.py new --type story` already accepts `persona`, `acs` and `verify`. EP0274's six stories were groomed by hand the same way on 2026-10-06. Raised by the G9 drafter.
> **Date:** 2026-10-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-09T08:11:25Z

## Summary

`refine apply --breakdown FILE` validates each story against `_BREAKDOWN_STORY_KEYS = {title, points, affects}` and refuses any other key, so a breakdown that was groomed before minting (persona, As/I want/So that, criteria with Verify selectors, depends-on, notes) must be minted bare and then groomed again by hand in every story file. `artifact.py new --type story --fields-file` already accepts `persona`, `acs` and `verify` and renders them; refine should take the same story fields, through the same renderer, so a groomed breakdown is minted groomed.

## Impact

Every refinement re-types its grooming by hand, story by story, with room for transcription drift between the reviewed breakdown and the minted stories.

## Acceptance Criteria

- [ ] `refine apply --breakdown` accepts, per story, the fields `artifact.py new --type story` accepts (at least persona, as/`i_want`/`so_that`, acs with verify, `depends_on`, notes) and mints each story with them rendered as `artifact new` renders them
- [ ] A story field `artifact new` would refuse is refused by refine before anything is minted, naming the story

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | Claude Opus 5.5 | Raised |
