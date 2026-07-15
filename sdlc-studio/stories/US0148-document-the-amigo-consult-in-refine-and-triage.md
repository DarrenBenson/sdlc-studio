# US0148: Document the amigo consult in refine and triage

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-workflow-personas.md
> **Epic:** EP0040
> **Points:** 3

## User Story

**As an** operator learning the ceremonies
**I want** the amigo consult documented where refine/triage are
**So that** I know questions go to named seats and are recorded, without reading the code.

## Acceptance Criteria

### AC1: the consult is documented across the reference, help, and CHANGELOG, and all links + style pass

- **Given** the amigo-consult documentation
- **When** the docs are checked
- **Then** `reference-workflow-personas.md` (the refine/triage rows + subsection), the `persona_resolve`/`refine`/`triage` script entries, `help/issue.md`/`help/triage.md`, and the CHANGELOG cover the consult; all markdown links resolve and style/budget pass
- **Verify:** shell python3 tools/check_links.py && bash tools/lint-style.sh && python3 tools/check_budgets.py
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
