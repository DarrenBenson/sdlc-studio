# US0435: a growing outstanding set across close attempts offers the bounded exit, not just the diagnosis

> **Status:** Done
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

### AC1: a growing set with deferrable debt offers the bounded exit

- **Given** an open run whose outstanding count rose across consecutive close attempts, with at
  least one DEFERRABLE (ceremony) blocker among the outstanding items
- **When** the close reports the attempt trend
- **Then** it does not only print "growing - chasing a moving target"; it names the bounded exit
  (`--file-and-close --retro <id>`) as the way to file the deferrable item(s) as follow-ups, and
  says plainly that any remaining hard correctness blocker(s) must be cleared first
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseAttemptTrendTests::test_a_growing_deferrable_set_offers_the_bounded_exit
- **Verified:** yes (2026-07-26)

### AC2: a growing set of only hard blockers is not sent to a dead end

- **Given** a growing outstanding set whose items are ALL hard correctness blockers (which
  `--file-and-close` refuses)
- **When** the trend is reported
- **Then** it does not dangle the file-and-close exit; it says the lanes must be cleared, naming that
  a growing set of correctness lanes is what the batch-scoped conformance and record-based currency
  checks exist to stop
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseAttemptTrendTests::test_a_growing_hard_set_is_told_to_clear_the_lanes_not_sent_to_a_dead_end
- **Verified:** yes (2026-07-26)

### AC3: a shrinking or first-attempt set makes no offer

- **Given** a first close attempt, or one whose outstanding count fell since the previous attempt
- **When** the trend is reported
- **Then** no exit is named - reserved for genuine divergence, so it does not train operators to reach
  for file-and-close on a converging close
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseAttemptTrendTests::test_a_converging_or_first_attempt_makes_no_offer
- **Verified:** yes (2026-07-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Created via `new` (deterministic) |
