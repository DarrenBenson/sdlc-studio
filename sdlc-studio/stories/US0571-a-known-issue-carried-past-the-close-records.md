# US0571: a known issue carried past the close records its stop-ship ruling and who made it

> **Status:** Done
> **Delivers:** CR0505
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0192
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an operator deciding whether to ship
**I want** every carried known issue to name its stop-ship ruling and who made it
**So that** an issue somebody judged is distinguishable from one nobody looked at

## Acceptance Criteria

### AC1: a carried known issue records its stop-ship ruling and who made it

- **Given** a closed run carrying open findings that were not fixed
- **When** the close records them as known issues
- **Then** each carries the stop-ship ruling, who made it and the date, so a reader can tell an issue somebody judged from one nobody looked at - this sprint carried eleven and the ruling existed only in conversation until it was written by hand
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistKnownIssueTests::test_a_carried_issue_records_its_ruling_and_who_made_it
- **Verified:** yes (2026-07-30)

### AC2: a carried issue with NO ruling is reported, not carried silently

- **Given** a closed run carrying a finding nobody has ruled on
- **When** the close runs
- **Then** it is reported as unruled rather than listed among the accepted ones - 'carried' and 'nobody looked' must not read the same, which is the distinction the whole record exists for
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistKnownIssueTests::test_an_unruled_carried_issue_is_reported_as_unruled
- **Verified:** yes (2026-07-30)

### AC3: a ruling of STOP-SHIP holds the close

- **Given** a closed run carrying a finding ruled stop-ship
- **When** the close runs
- **Then** it refuses, naming the finding - a ruling that changes nothing is a note, and the ruling that matters most is the one that must be able to stop something
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistKnownIssueTests::test_a_stop_ship_ruling_holds_the_close
- **Verified:** yes (2026-07-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | sdlc-studio | Created via `new` (deterministic) |
