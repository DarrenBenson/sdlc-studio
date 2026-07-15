# US0140: triage gates: reconcile flags an untriaged Issue and an Issue's terminal status derives from its children

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py
> **Epic:** EP0038
> **Points:** 3

## User Story

**As an** operator
**I want** an accepted-but-untriaged Issue flagged, and its Resolved derived from its bugs
**So that** an Issue cannot rot in the intake queue or be closed while its work is unfinished.

## Acceptance Criteria

### AC1: reconcile flags an accepted childless Issue (but not an Open one), naming triage

- **Given** an enforced project
- **When** an Issue is Open (intake) versus Triaging (accepted) with no children
- **Then** the Open Issue is not flagged, the Triaging one is flagged `undecomposed` with a fix that names `triage`
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_issue_triage.IssueGateTests.test_open_issue_not_flagged_triaging_childless_is
- **Verified:** yes (2026-07-15)

### AC2: an Issue reaches Resolved only by derivation from its bugs (G2)

- **Given** a triaged Issue
- **When** its Resolved is attempted while a bug is unresolved, then again once all bugs are terminal
- **Then** the first attempt is blocked, the second passes; a childless Issue cannot be Resolved by assertion but can be closed Won't Fix
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_issue_triage.IssueGateTests.test_issue_resolved_is_derived_from_children tests.test_issue_triage.IssueGateTests.test_childless_issue_cannot_be_resolved_by_assertion
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
