# US0222: persist verification-cap overflow as a durable carry-over worklist a scoped follow-up re-ingests

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-audit.md, .claude/skills/sdlc-studio/templates/automation/audit-finder.md
> **Epic:** EP0073
> **Points:** 3

## User Story

**As an** agent running a capped audit
**I want** the candidates the verification cap drops written to a durable carry-over file that a later run can verify directly
**So that** the unverified tail is carried work with a route back in, not a count in a session-local journal that dies with the session

## Acceptance Criteria

### AC1: Capped-out candidates are written, not just counted

- **Given** an audit surfaces more candidates than the verification budget will refute
- **When** the cap drops the overflow
- **Then** the budget section of `reference-audit.md` requires each dropped candidate to be written in full (title, file, claim, evidence, lens, severity) to a durable carry-over file such as `.local/audit-carryover-<date>.json`, in place of logging only how many were dropped
- **Verify:** grep "audit-carryover-" .claude/skills/sdlc-studio/reference-audit.md
- **Verified:** yes (2026-07-19)

### AC2: The close-out report routes the overflow back in

- **Given** a run that produced a carry-over file
- **When** it writes its close-out report
- **Then** the report names the carry-over file's path and gives the single scoped command that verifies just those candidates, skipping the find phase
- **Verify:** grep "audit --carryover" .claude/skills/sdlc-studio/reference-audit.md
- **Verified:** yes (2026-07-19)

### AC3: A follow-up run ingests the carry-over as its candidate pool

- **Given** a carry-over file from an earlier capped run
- **When** a follow-up audit is pointed at it
- **Then** the finder harness takes those records as the candidate pool and goes straight to the refute panels, running no finder lenses
- **Verify:** grep "carry-over candidate pool" .claude/skills/sdlc-studio/templates/automation/audit-finder.md
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
