# US1279: A decision rules the high-risk trigger, and US1034, US1035, EP0284 and CR0622 are reconciled with it

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0721
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/decisions.md, sdlc-studio/stories/US1034-critic-py-seats-adds-a-second-different-seat.md, sdlc-studio/stories/US1035-the-sprint-report-names-a-high-risk-unit.md, sdlc-studio/epics/EP0284-review-seats-chosen-by-what-a-change-touches.md, sdlc-studio/change-requests/CR0622-a-second-different-seat-on-high-risk-units.md
> **Epic:** EP0359
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A decision rules the high-risk trigger, and US1034, US1035, EP0284 and CR0622 are reconciled with it
**So that** CR0721 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A decision row rules which trigger defines a high-risk unit

- **Given** `sdlc-studio/decisions.md`
- **When** the newest rows are read
- **Then** one accepted row states which trigger defines a high-risk unit (the `Risk-class` derived from `risk.components`, the points and paths thresholds, or a named combination), cites CR0622 and CR0696, and says what becomes of the trigger it does not keep. Fails on: a row that cites one side only, or reconciled stories with no ruling behind them
- **Verify:** manual read the records the criterion names and confirm each reads as stated; paperwork only, no test can pin it

### AC2: US1034 no longer specifies a second derivation of the seat

- **Given** US1034 and the decision row
- **When** the story is read
- **Then** it is either closed as Superseded naming US1152 to US1154, moved by the transition tool, or rewritten so that no criterion names `critic.py seats` or a `review.second_seat` key unless the decision keeps them; its 2026-10-21 triage items are each resolved or struck with the reason. Fails on: a Draft US1034 that would still add a second config surface if built as written
- **Verify:** manual read the records the criterion names and confirm each reads as stated; paperwork only, no test can pin it

### AC3: US1035's criteria are written against the delivered Risk-class

- **Given** US1035 and the delivered stories US1152 to US1154
- **When** its acceptance criteria are read
- **Then** each names the delivered `Risk-class` and the seat `sprint plan` names, none names `review.second_seat`, and the criterion for a high-class unit reviewed by one seat carries a `pytest` Verify line whose test file is in the story's Affects. Fails on: a criterion whose Verify names a verb or key that does not exist at HEAD
- **Verify:** manual read the records the criterion names and confirm each reads as stated; paperwork only, no test can pin it

### AC4: CR0622 and EP0284 point at what was delivered

- **Given** CR0622 and EP0284
- **When** each is read
- **Then** each names CR0696 and US1152 to US1154 as the delivered design and names the decision row, so a reader of either side finds the other. Fails on: either page still presenting the points and paths thresholds as the only design
- **Verify:** manual read the records the criterion names and confirm each reads as stated; paperwork only, no test can pin it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
