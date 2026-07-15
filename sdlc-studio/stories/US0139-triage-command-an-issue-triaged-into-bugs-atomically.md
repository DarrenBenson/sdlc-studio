# US0139: triage command: an Issue triaged into bugs, atomically wired

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/triage.py
> **Epic:** EP0038
> **Points:** 5

## User Story

**As a** team member working the Discovery backlog
**I want** to triage an Issue into bugs with one atomic command
**So that** a raw report becomes reproducible delivery units with the links wired, or fails empty.

## Acceptance Criteria

### AC1: triage mints bugs, wires both link sides, and moves the Issue to Triaged

- **Given** an enforced project with an Issue
- **When** `triage apply --issue <id> --bug ...` runs
- **Then** each bug is created carrying `Parent:` the Issue, the Issue's `Decomposed-into:` lists them, and the Issue moves to Triaged; `triage show` surfaces the report
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_issue_triage.TriageTests.test_triage_mints_bugs_and_wires_both_sides
- **Verified:** yes (2026-07-15)

### AC2: triage is atomic and refuses a bad breakdown (non-issue, already-triaged, empty, off-scale, unresolvable Affects)

- **Given** a breakdown with any invalid bug, or an invalid target
- **When** `triage apply` is invoked
- **Then** nothing is minted (no orphan bug file, Issue untouched) and the command refuses; a v3 Low-severity bug mints an individual bug, never a consolidation CR
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_issue_triage.TriageTests
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
