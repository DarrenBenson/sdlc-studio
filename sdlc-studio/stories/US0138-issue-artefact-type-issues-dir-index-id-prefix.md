# US0138: Issue artefact type: issues dir, index, id prefix, artifact new --type issue

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py
> **Epic:** EP0038
> **Points:** 3

## User Story

**As an** operator
**I want** to create an Issue with `artifact.py new --type issue`
**So that** a raw defect report is a first-class, validated, indexed artefact.

## Acceptance Criteria

### AC1: an Issue creates with Size + Severity, no points, and validates + reconciles clean

- **Given** the `issue` type registered in `ARTIFACT_TYPES` (prefix `IS`), the id regex, and the status vocab
- **When** an Issue is created via `artifact.new`
- **Then** it is born `Open` with a T-shirt `Size` and a `Severity` but no Points, its id parses as `IS0001`, and it validates with zero errors and leaves the issue index census clean
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_issue_triage.IssueArtefactTests
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
