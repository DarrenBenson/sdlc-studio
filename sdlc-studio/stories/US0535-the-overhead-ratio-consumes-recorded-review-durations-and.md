# US0535: The overhead ratio consumes recorded review durations, and states it is a lower bound only while a component is genuinely unmeasured

> **Status:** Done
> **Delivers:** CR0466
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0182
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an operator judging where sprint time goes
**I want** the overhead ratio to consume recorded review durations
**So that** the headline figure stops excluding the largest overhead component of the last two sprints

## Acceptance Criteria

### AC1: the ratio consumes recorded review durations

- **Given** a run whose review rounds carry durations
- **When** the overhead ratio is computed
- **Then** the review and repair component is measured from those durations rather than reported unmeasured
- **Verify:** manual - retired by BG0783: no record the run writes times a review since US0918 deleted the close-review round's writer, so the overhead's review component reads NOT CAPTURED and the round-duration read is deleted
- **Verified:** manual (2026-09-27) - retired, superseded by BG0783

### AC2: the lower-bound caveat is stated only while a component is genuinely unmeasured

- **Given** a run in which every overhead component is measured
- **When** the ratio is rendered
- **Then** it is not described as a floor, and a run with any unmeasured component still is
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::OverheadRatioTests::test_the_two_qualifiers_come_from_one_decision
- **Verified:** yes (2026-09-27)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
| 2026-09-27 | BG0783 | AC2 re-pointed at `OverheadRatioTests::test_the_two_qualifiers_come_from_one_decision`: the floor caveat still follows the ratio's bound, and that test pins both qualifiers from one `bound` (an exact bound drops them, a lower one states them); since no record times a review, a real run is always the lower case. AC1 retired in the D0259 pattern: no record the run writes times a review since US0918 deleted the close-review round's writer, so the overhead's review component reads NOT CAPTURED and the round-duration read is deleted |
