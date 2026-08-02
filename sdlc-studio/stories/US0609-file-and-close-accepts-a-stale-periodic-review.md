# US0609: file-and-close accepts a stale periodic review as ceremony debt and files it as a real artefact linked to the run

> **Status:** Review
> **Delivers:** CR0522
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0200
> **Points:** 3

## User Story

**As a** operator facing a blocked close
**I want** the bounded exit able to file a stale periodic review as ceremony debt
**So that** the documented escape hatch works on the case it was written for

## Acceptance Criteria

### AC1: file-and-close accepts a stale periodic review

- **Given** a close blocked only by a stale repo-wide review
- **When** `--file-and-close` runs
- **Then** it files the staleness as a real artefact linked to the run and closes `closed-outstanding`, because a periodic ceremony being overdue is ceremony debt by definition
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::FileAndCloseTests::test_a_stale_periodic_review_is_filed_as_debt
- **Verified:** yes (2026-08-02)

### AC2: a real correctness blocker is still refused

- **Given** a close carrying a red correctness lane
- **When** `--file-and-close` runs
- **Then** it still refuses, so this does not become a way to file away a failing gate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::FileAndCloseTests::test_a_correctness_blocker_is_still_refused
- **Verified:** yes (2026-08-02)

### AC3: the classification is read from the lane, not a second list

- **Given** the bounded exit deciding what it may file
- **When** the classifier is read
- **Then** it reads the lane's own declaration rather than naming lanes here, because a second list drifts from the first and silently classes a new lane as correctness
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::FileAndCloseTests::test_the_classification_is_read_from_the_lane_not_a_second_list
- **Verified:** yes (2026-08-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
