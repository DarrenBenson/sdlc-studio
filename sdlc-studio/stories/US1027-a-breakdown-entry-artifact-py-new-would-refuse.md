# US1027: A breakdown entry artifact.py new would refuse is refused before anything is minted, naming the story

> **Status:** Draft
> **Delivers:** CR0628
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine_breakdown_refusals.py, changelog.d/US1027.md
> **Epic:** EP0283
> **Points:** 2
> **Depends on:** US1026
> **Persona:** Maya Okafor

## User Story

**As** the operator applying a reviewed breakdown
**I want** every entry checked as `artifact.py new` would check it before the first story is minted, with the refusal naming the story
**So that** a bad selector in the ninth story never leaves eight minted stories, or their index rows, behind

## Acceptance Criteria

- **AC1:** Given a three-story breakdown whose third entry carries a `verify` selector that is a near miss of a test the fixture holds, when `refine.py apply --breakdown` runs, then it refuses, naming the third story and the selector, and afterwards no epic or story file exists and the story and epic indexes are byte-identical to before.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_breakdown_refusals.py::BreakdownRefusalTests::test_a_bad_entry_is_refused_before_anything_is_minted
- **AC2:** Given an entry carrying a key neither refine nor `artifact.py new` accepts, when refine runs, then it refuses before anything is minted, naming the story and the key, and the keys it lists as allowed are exactly refine's own plus the story writer's.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_breakdown_refusals.py::BreakdownRefusalTests::test_the_allowed_keys_are_the_story_writers_and_refines_own

## Notes

- Release: 6.2 (D0355 breakdown G9, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: leaving the checks to `artifact.new` inside the mint loop, where the rollback unlinks the minted files (refine.py:313-319, :403-409) but leaves the index rows `artifact.new` appended
- AC2 must fail on: a hand-kept key list in refine that drifts from the story writer's set
- Each entry is validated by `artifact.new(..., dry_run=True)` before the first mint. Its checks (`check_user_story_fields`, `check_prose_acs`, `check_affects_resolvable`, `check_verify_selectors`) all run before its dry-run return (artifact.py:1090-1105, :1185), so refine asks the one authority rather than restating it. This extends the CR0618 story's pre-mint helper (panel: build it once).
- The epic is not minted during the check, so the dry run validates each entry without its epic link.
- This is CR0628 AC2.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G9 after the refine panel's review |
