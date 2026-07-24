# US0383: census the 62 --root scripts and fix or refile the unanchored writers, next_id first

> **Status:** Draft
> **Delivers:** CR0383
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0140
> **Points:** 8
> **Affects:** .claude/skills/sdlc-studio/scripts/next_id.py, .claude/skills/sdlc-studio/scripts/tests/test_next_id.py, .claude/skills/sdlc-studio/scripts/tests/test_root_census.py, .claude/skills/sdlc-studio/reference-scripts.md, sdlc-studio/reviews/root-census.md

## User Story

**As an** operator whose agents run skill scripts from wherever they happen to be
**I want** every `--root`-declaring script classified as anchored, unanchored or a deliberate non-root surface, with the worst writer fixed and the rest named
**So that** a silent fail-open write into a stray workspace is a known, tracked list rather than a defect found one instance at a time

## Acceptance Criteria

### AC1: every --root-declaring script is classified, with a reason, and none is left out

- **Given** the script family, whose `--root`-declaring members the CLI sweep already enumerates from their parsers
- **When** the census runs over that enumeration and is compared with the recorded classification
- **Then** every enumerated script carries exactly one classification - anchored, unanchored, or a deliberate non-root surface with its reason stated - and a script present in the family but absent from the record fails the check, so a newly added script cannot join unclassified
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_root_census.py::RootCensusTests::test_every_root_declaring_script_is_classified_with_a_reason

### AC2: next_id allocates against the real workspace when run from a subdirectory

- **Given** a project root holding artefacts up to `US0383`, and a cwd inside `.claude/skills/sdlc-studio/scripts/`
- **When** `next_id allocate --type story` is run there with no `--root`
- **Then** it resolves upward to the real workspace and returns the next free id above the existing ones, rather than reading an empty tree and minting an id that already exists - the collision case is the reason this script goes first
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_next_id.py::RootAnchoringTests::test_allocation_from_a_subdirectory_sees_the_real_workspace

### AC3: an unanchored script is either fixed or named by a filed follow-up

- **Given** the census classification with its unanchored entries
- **When** the check evaluates each unanchored entry
- **Then** it passes only where the script now resolves through the shared resolver, or the entry names a filed follow-up artefact that exists on disk, and it fails on an entry that is neither - silence is not a classification
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_root_census.py::RootCensusTests::test_an_unanchored_entry_needs_a_fix_or_a_filed_follow_up

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
| 2026-07-24 | sdlc-studio | Built: census record + measured sweep guard, `next_id` anchored, remainder filed as BG0282 |
