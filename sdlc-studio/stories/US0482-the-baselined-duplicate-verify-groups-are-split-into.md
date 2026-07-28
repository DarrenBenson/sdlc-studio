# US0482: The baselined duplicate Verify groups are split into discriminating selectors

> **Status:** Draft
> **Delivers:** CR0445
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/stories, sdlc-studio/bugs, sdlc-studio/.verify-lint-baseline.json, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Epic:** EP0174
> **Points:** 8

## User Story

**As a** reader taking a Done story's evidence as proof of the criterion beside it
**I want** each acceptance criterion to name a selector that distinguishes it from its neighbours
**So that** a green stamp means that criterion was checked, not that some criterion in the story was

## Notes

**Scope is stories AND bugs**, matching the ratchet in US0461 (AC1), whose scan covers
`sdlc-studio/bugs` precisely so a shared selector cannot be parked in a bug where
`duplicate_verifiers` never looked. A stories-only burn-down would leave the bug-side
groups baselined for good. Measured at grooming with
`verify_ac.duplicate_verifiers`: stories alone give 19 groups, 13 of them confined to a
single record; stories and bugs together give 31 groups, 20 intra-record, seven of those
seven living in bugs.

Those figures are context for the size, not the pass condition. Every criterion below is
satisfied by running the resolver over the workspace and finding nothing left, so a group
added or paid down between grooming and delivery does not make the story wrong.

## Acceptance Criteria

### AC1: no intra-record duplicate group remains, over stories and bugs

- **Given** the duplicate groups confined within a single record, in `sdlc-studio/stories` and `sdlc-studio/bugs` alike
- **When** `verify_ac.py lint --ratchet --bugs` runs over the workspace
- **Then** it reports no intra-record duplicate group in either directory, each having been split into per-criterion selectors, so a bug's shared selector is burned down on the same terms as a story's rather than surviving the sweep
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DuplicateBurndownTests::test_no_intra_record_duplicate_group_remains_in_stories_or_bugs

### AC2: the groups no collection can answer are named individually, identified by the resolver

- **Given** the duplicate groups whose selector `verify_ac.selector_resolves` answers `None` for - unanswerable because the verb is outside `_COLLECTABLE`, so the staleness sweep is blind to them (LL0047)
- **When** the lint runs
- **Then** the set is derived by calling the resolver at lint time, never from a count recorded in prose, and each member is reported individually with the verb that makes it unanswerable and every AC claiming it, so the report names which groups are exempt rather than absorbing them into a total
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DuplicateBurndownTests::test_unanswerable_groups_are_derived_from_the_resolver_and_named

### AC3: the baseline shrinks to empty and the ratchet still refuses a new duplicate

- **Given** `sdlc-studio/.verify-lint-baseline.json` emptied of the burned-down groups
- **When** a story and a bug each introducing a fresh duplicate group are added
- **Then** the ratchet refuses each, proving the burn-down emptied the baseline without disarming the guard that protects it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DuplicateBurndownTests::test_the_emptied_baseline_still_refuses_a_new_duplicate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: acceptance criteria authored against the slice |
| 2026-07-28 | Claude Opus 5 (BG0346) | Regroomed: scope widened to stories and bugs to match the ratchet, baseline file declared, resized 5 to 8, and the invented four unanswerable groups replaced by a resolver-derived criterion |
