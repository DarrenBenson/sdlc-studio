# US0142: refine show accepts an already-decomposed request and lists its existing epics, staying read-only

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py
> **Epic:** EP0039
> **Points:** 2

## User Story

**As an** operator planning the next slice of a part-refined request
**I want** `refine show` to accept an already-decomposed request and list its epics
**So that** I can inform a `refine add` without the command refusing me.

## Acceptance Criteria

### AC1: show accepts a decomposed request and lists its epics; apply stays strict; non-request still refused

- **Given** an already-decomposed request
- **When** `refine show` is run (read-only), and `refine apply` is attempted
- **Then** show lists the existing `Decomposed-into:` epics and steers to `add`, while apply still refuses a decomposed request and show still refuses a non-request
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_issue_triage.RefineShowDecomposedTests
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
