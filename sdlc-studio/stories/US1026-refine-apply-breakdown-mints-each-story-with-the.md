# US1026: refine apply --breakdown mints each story with the persona, user story and criteria its entry carries

> **Status:** Draft
> **Delivers:** CR0628
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_refine_breakdown_fields.py, .claude/skills/sdlc-studio/help/refine.md, .claude/skills/sdlc-studio/reference-scripts-create.md, changelog.d/US1026.md
> **Epic:** EP0283
> **Points:** 3
> **Depends on:** US1025
> **Persona:** Maya Okafor

## User Story

**As** the operator who reviews a breakdown before it is minted
**I want** each breakdown entry's persona, user story and criteria with their Verify selectors to land on the story refine mints, rendered as `artifact.py new` renders them
**So that** a breakdown groomed and reviewed before minting is minted groomed, instead of being re-typed into every story by hand

## Acceptance Criteria

- **AC1:** Given a two-story breakdown whose entries carry `persona`, `role`, `capability`, `benefit` and `acs` with `verify`, when `refine.py apply --breakdown` runs, then each minted story's Persona line, User Story block and Acceptance Criteria section are identical to what `artifact.py new --type story --fields-file` renders for the same fields.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_breakdown_fields.py::BreakdownFieldsTests::test_each_entry_is_rendered_as_artifact_new_renders_it
- **AC2:** Given a one-story breakdown that carries its own `acs`, for a request whose criteria carry Verify lines, when it is refined both by `--epic-title` and `--into`, then the story carries the breakdown's criteria and none of the request's seed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_breakdown_fields.py::BreakdownFieldsTests::test_a_breakdowns_criteria_win_over_the_request_seed
- **AC3:** Given an entry that supplies `acs` and no user-story fields, and another that writes its user story as `as`, `i_want` and `so_that`, when refine mints them, then the first story's User Story block is filled from its title and request as today, and the second's carries the given text.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_breakdown_fields.py::BreakdownFieldsTests::test_user_story_fields_are_filled_or_kept
- **AC4:** Given help/refine.md and the refine entry in reference-scripts-create.md, when the test reads the breakdown keys they list and refines a breakdown carrying each one, then every listed key is accepted and lands on the minted story.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_breakdown_fields.py::BreakdownFieldsTests::test_the_documented_breakdown_keys_are_the_accepted_ones

## Notes

- Release: 6.2 (D0355 breakdown G9, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: refine rendering the criteria with a second writer of its own, or `_mark_ungroomed` running after `artifact.new` and replacing the rendered criteria (refine.py:300-307, :388-393)
- AC2 must fail on: `_seed_acs` still running after `artifact.new` on a one-story refine, so the request's seed overwrites the reviewed breakdown
- AC3 must fail on: `_fill_user_story` skipped whenever an entry supplies any field, or the CR's spellings refused as unknown keys
- AC4 must fail on: the docs still naming only title, points and affects, or listing a key refine refuses
- Checked at HEAD: a breakdown entry carrying `persona` and `acs` is refused with 'unknown key(s) acs, persona - allowed: affects, points, title' (fixture probe; `_BREAKDOWN_STORY_KEYS`, refine.py:416).
- The entry's story fields pass straight to `artifact.new(root, 'story', title, fields)`, which already renders persona, role, capability, benefit, acs and verify. Refine then skips `_seed_acs` and `_mark_ungroomed` for an entry that supplied `acs`, and keeps `_fill_user_story` for whatever the entry left unsupplied. The breakdown wins over the request's seed (panel).
- The story writer's keys are named once in artifact.py, as a story subset of `FIELDS_FILE_KEYS`, and refine reads that set: one list, never a second copy. CR0628 AC1 names `as`, `i_want` and `so_that`, the D0355 drafts' spelling, so refine accepts them as aliases of `role`, `capability` and `benefit` and refuses an entry that gives both spellings of one field.
- Shares the pre-mint helper and the precedence rule with the CR0618 story, so it builds after it (panel's order: BG0995, CR0618, then CR0628).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G9 after the refine panel's review |
