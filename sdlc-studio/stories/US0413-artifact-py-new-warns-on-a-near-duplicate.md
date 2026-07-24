# US0413: artifact.py new warns on a near-duplicate title before minting, naming the existing id

> **Status:** Ready
> **Delivers:** CR0413
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Epic:** EP0156
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: a near-duplicate title is reported with the existing id before anything is minted

- **Given** a backlog already carrying a defect with a closely-matching title
- **When** `artifact.py new` is invoked with that title
- **Then** it reports the existing id BEFORE minting - the re-filing CR0413 recorded happened because nothing looked, and an id minted first cannot be un-minted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::DuplicateCheckTests::test_a_near_duplicate_is_reported_with_the_existing_id

### AC2: a genuinely new title is not obstructed

- **Given** a title sharing common words with existing artefacts but describing different work
- **When** `new` is invoked
- **Then** it mints without a duplicate report - a check that fires on ordinary vocabulary would be turned off within a week
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::DuplicateCheckTests::test_an_ordinary_new_title_is_not_flagged

### AC3: the check reads terminal artefacts too

- **Given** a defect already filed and CLOSED
- **When** the same title is filed again
- **Then** it is still reported - re-filing something already fixed is the case that wastes the most time, and scoping the check to open artefacts would miss it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::DuplicateCheckTests::test_a_closed_artefact_still_counts_as_a_duplicate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
