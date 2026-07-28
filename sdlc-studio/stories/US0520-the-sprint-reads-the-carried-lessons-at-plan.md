# US0520: The sprint reads the carried lessons at plan and puts them in every delivery lane's brief and the reviewers'

> **Status:** Review
> **Delivers:** CR0464
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0179
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** delivery lane about to repeat a mistake somebody already recorded
**I want** the carried lessons in my brief, not only in the operator's terminal
**So that** the learning reaches the agent doing the work and the reviewer checking it

## Acceptance Criteria

### AC1: the plan reads the carried set and puts it in every lane brief

- **Given** a plan with a carried-lessons set recorded
- **When** lanes are dispatched
- **Then** each brief carries the set, so it reaches the agent doing the work rather than scrolling past at plan time
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CarriedLessonsBriefTests::test_every_lane_brief_carries_the_set

### AC2: the reviewers receive it too

- **Given** a review dispatched for the batch
- **When** its brief is built
- **Then** it carries the same set, because the pass most likely to catch a repeat should know what has been repeating
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CarriedLessonsBriefTests::test_the_review_brief_carries_the_set

### AC3: an absent set is reported, never silently skipped

- **Given** a plan whose carried set is missing or unreadable
- **When** lanes are dispatched
- **Then** the absence is reported rather than the briefs silently going out without it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CarriedLessonsBriefTests::test_an_absent_set_is_reported

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
