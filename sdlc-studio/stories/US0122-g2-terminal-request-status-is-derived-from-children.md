# US0122: G2 terminal request status is derived from children, never asserted

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py
> **Epic:** EP0033
> **Points:** 3

## User Story

**As an** operator closing work
**I want** a request's terminal status DERIVED from its children, never asserted
**So that** a CR marked Complete is provably complete - every unit it produced is Done - rather than a claim gated on prose.

## Acceptance Criteria

### AC1: a CR cannot reach Complete while a child is unfinished

- **Given** a CR with a child epic/story that is not yet Done
- **When** `transition set --id <CR> --status Complete` runs
- **Then** it is refused, naming the unfinished child; the CR stays non-terminal
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::DerivedStatusTests
- **Verified:** yes (2026-07-15)

### AC2: a childless request cannot be terminal

- **Given** a CR or RFC with no children (nothing names it as Parent)
- **When** a transition to a terminal status (Complete / Accepted) runs
- **Then** it is refused - a request that produced nothing delivered nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::DerivedStatusTests
- **Verified:** yes (2026-07-15)

### AC3: a request whose children are all done may close

- **Given** a CR all of whose child epics/stories are Done (an RFC all of whose child CRs are Complete)
- **When** the terminal transition runs
- **Then** it is allowed - the derived condition is met
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::DerivedStatusTests
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
