# US0435: a growing outstanding set across close attempts offers the bounded exit, not just the diagnosis

> **Status:** Draft
> **Delivers:** CR0421
> **Created:** 2026-07-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0162
> **Points:** 2

## User Story

**As an** operator whose close keeps re-breaking one lane while fixing another
**I want** the close to offer the bounded `--file-and-close` exit once the outstanding set is growing
**So that** a close that is chasing a moving target has a way out it names, instead of only diagnosing
the divergence and leaving me to force a false Done or grandfather same-day work

## Acceptance Criteria

### AC1: a growing outstanding set offers the bounded exit

- **Given** an open run whose previous close attempt recorded an outstanding count, and a current
  attempt whose outstanding count is higher
- **When** the close reports the attempt trend
- **Then** it does not only print "growing - chasing a moving target"; it also names the bounded exit
  (`--file-and-close --retro <id>`) as the way to close with the remaining work honestly filed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseAttemptTrendTests::test_a_growing_outstanding_set_offers_the_bounded_exit

### AC2: a shrinking or first-attempt set does not offer the exit

- **Given** a first close attempt, or one whose outstanding count fell since the previous attempt
- **When** the trend is reported
- **Then** no bounded-exit offer is made - the offer is reserved for genuine divergence, so it does not
  train operators to reach for file-and-close on a converging close
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseAttemptTrendTests::test_a_converging_or_first_attempt_makes_no_offer

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
