# US0635: The thirteen story-side duplicate Verify groups are split into discriminating selectors

> **Status:** Ready
> **Delivers:** CR0445
> **Supersedes:** US0482
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/stories, sdlc-studio/.verify-lint-baseline.json, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Epic:** EP0174
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** reader taking a Done story's evidence as proof of the criterion beside it
**I want** each acceptance criterion in a story to name a selector no sibling criterion shares
**So that** a green stamp means that criterion was checked, not that some criterion in the story was

## Notes

Split from US0482, which was at the 8-point ceiling. This is the story-side half of the
burn-down; US0636 is the bug-side half and closes the baseline out; US0637 is the reporting
change that was US0482's AC2.

Measured at split time with `verify_ac.duplicate_verifiers` over the live tree: **13
intra-record groups across 13 story records** - US0025, US0111, US0113, US0114, US0123,
US0124, US0166, US0167, US0170, US0247, US0266, US0268, US0392. Nine are whole-file
selectors (`unittest discover -p test_x.py`, `pytest ... -k`), which is how one run comes to
stand as evidence for criteria it never separately exercised.

Those figures are context for the size, not the pass condition. Every criterion below is
satisfied by running the resolver over the workspace and finding nothing left, so a group
added or paid down between grooming and delivery does not make the story wrong.

Splitting a whole-file selector sometimes needs a named test that does not exist yet. Write
it rather than narrowing the selector to a `-k` expression that still matches several
criteria - a selector that discriminates by accident is the debt this pays down.

## Acceptance Criteria

### AC1: no intra-record duplicate group remains in a story

- **Given** the duplicate groups confined within a single record under `sdlc-studio/stories`
- **When** `verify_ac.py lint --ratchet` runs over the workspace, deriving the set from the
  resolver at lint time rather than from any count recorded in prose
- **Then** it reports no intra-record duplicate group in that directory, each having been
  split into a per-criterion selector
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DuplicateBurndownTests::test_no_intra_record_group_remains_in_stories

### AC2: the baseline no longer carries the story-side entries, and only shrank

- **Given** `sdlc-studio/.verify-lint-baseline.json`, which records the pre-existing groups so
  the ratchet can be enforced from there and whose set may only shrink
- **When** the burn-down lands
- **Then** no intra-record story-side group remains listed, and no entry has been added -
  compared against the file at this story's base ref, so the direction is proven rather than
  asserted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DuplicateBurndownTests::test_the_story_side_baseline_entries_are_gone_and_none_were_added

### AC3: emptying the story side did not disarm the guard

- **Given** a story introducing a fresh duplicate group, added after the burn-down
- **When** the ratchet runs
- **Then** it refuses, proving the entries were removed by splitting the selectors rather than
  by weakening the check that protects them
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DuplicateBurndownTests::test_a_fresh_duplicate_in_a_story_is_still_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | Claude Opus 5 | Split from US0482 (8 points, over the ceiling): the story-side burn-down, groomed against the resolver's measurement of the live tree |
