# US0137: Issue joins the discovery vocab: is_discovery, plan and status treat it as discovery

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
> **Epic:** EP0038
> **Points:** 3

## User Story

**As an** operator running the two-backlog workflow
**I want** an Issue treated as a Discovery item by the planner and status
**So that** it is never mistaken for deliverable work and always shows on the Discovery side.

## Acceptance Criteria

### AC1: is_discovery covers RFC/CR/Issue; is_request stays the narrow RFC/CR set

- **Given** the vocabulary in `lib/sdlc_md.py`
- **When** `is_discovery` and `is_request` are evaluated per type
- **Then** `is_discovery` is true for rfc/cr/issue and false for story/bug/epic, while `is_request` stays true only for rfc/cr (an Issue is triaged, not refined)
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_issue_triage.DiscoveryVocabTests
- **Verified:** yes (2026-07-15)

### AC2: plan refuses an Issue and status buckets it under Discovery

- **Given** an enforced project with an Issue
- **When** `sprint plan` is asked to plan it, and `status backlog` is rendered
- **Then** the plan is refused (G1, exit 2) and the Issue appears under the Discovery backlog, never Delivery
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_issue_triage.IssueGateTests.test_plan_refuses_an_issue_when_enforced tests.test_issue_triage.IssueGateTests.test_status_backlog_buckets_issue_under_discovery
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
