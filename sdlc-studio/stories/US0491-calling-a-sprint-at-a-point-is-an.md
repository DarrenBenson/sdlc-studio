# US0491: Calling a sprint at a point is an honest close: the unstarted remainder is descoped with a reason and returns to the backlog

> **Status:** Ready
> **Delivers:** RFC0057
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/help/sprint.md
> **Epic:** EP0176
> **Points:** 5

## User Story

**As a** operator whose sprint met reality two thirds of the way through
**I want** to call the sprint at that point and have the close record what was achieved
**So that** a sprint that delivered most of its batch records that, instead of being abandoned as though it delivered nothing

## Acceptance Criteria

### AC1: calling the sprint closes it honestly against the goal

- **Given** an open run with delivered and unstarted units
- **When** the sprint is called at that point
- **Then** the close records what was delivered against the Sprint Goal and completes the close paperwork, rather than abandoning the run as stop does
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CallItHereTests::test_call_reaches_the_SHIPPED_ENTRY_POINT
- **Verified:** yes (2026-08-04)

### AC2: the descoped remainder carries a reason

- **Given** unstarted units in the batch
- **When** the sprint is called with no reason given
- **Then** it is refused until a reason is supplied, matching the reason batch drop already requires, so a descope is never unexplained
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CallItHereTests::test_a_descope_without_a_reason_is_refused
- **Verified:** yes (2026-08-04)

### AC3: descoped units return to the backlog rather than being carried

- **Given** a called sprint with a descoped remainder
- **When** the close completes
- **Then** each descoped unit is back in the backlog at its prior status and none is attached to a following charter, so no coupling between sprints is created
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CallItHereTests::test_descoped_units_return_to_the_backlog_uncoupled
- **Verified:** yes (2026-08-04)

## Verification evidence

Functional. Three mutants executed, `__pycache__` purged and each child run under `python3 -B`,
anchors asserted unique, source restored byte-identical:

| Mutant | Result |
| --- | --- |
| drop the reason requirement | killed |
| leave the descoped remainder in the approved batch | killed |
| treat every unit as delivered | killed |

**The design decision inside AC3, stated so it is not reversed later.** The remainder goes
BACKWARD to the backlog, never forward to the next charter. Attaching it forward would make the
next run inherit a batch it never approved - the thing the single-slot rule and the approved-batch
record exist to prevent - and would couple two sprints that should be independent. Back in the
backlog, the next charter's scope query reaches the unit if it still matches and does not if it
no longer does, which is the same late-materialising rule the whole queue is built on, applied
to the tail of a run. A test asserts the following charter's file does not name the descoped
unit at all.

Each descoped unit keeps its own status untouched, because `drop_from_batch` judges THIS BATCH
rather than the work: a unit that was Open is still Open, and nothing marks it as having failed.

**One defect in this unit's own test, found by running it.** AC3's first draft asserted the
descoped unit was available by calling `materialise_next`, which correctly REFUSED because the
run was still open - so the assertion was about starting a second run rather than about the
unit's availability. It now asserts against the same selector a charter would use.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed against the D0072 rulings |
