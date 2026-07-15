# US0123: G4 status reports the request backlog and the product backlog separately

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py
> **Epic:** EP0033
> **Points:** 2

## User Story

**As an** operator reading status
**I want** the Discovery backlog (RFCs, CRs - the options funnel) reported separately from the Delivery backlog (epics, stories, bugs - sized work)
**So that** intake is never counted as work in progress, and "what is ready to deliver" is not overstated by undecomposed requests.

## Acceptance Criteria

### AC1: status splits the two backlogs

- **Given** a mix of non-terminal requests and product units
- **When** `status backlog` runs
- **Then** it reports a DISCOVERY backlog (rfc, cr - the options funnel) and a DELIVERY backlog (epic, story, bug - sized work) as distinct groups, each counted on its own (dual-track agile / upstream Kanban)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::TwoBacklogStatusTests
- **Verified:** yes (2026-07-15)

### AC2: the split uses the shared taxonomy, not a local list

- **Given** the `is_request` predicate from `sdlc_md`
- **When** status assigns each type to a backlog
- **Then** the assignment is driven by `is_request`, so status and the planner agree on what a request is
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::TwoBacklogStatusTests
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-15 | sdlc-studio | Delivered; backlogs named Discovery/Delivery (dual-track agile / upstream Kanban) per operator decision, in place of Request/Product |
