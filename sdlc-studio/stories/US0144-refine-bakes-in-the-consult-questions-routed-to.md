# US0144: refine bakes in the consult: questions routed to the resolved seats by lens

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py
> **Epic:** EP0040
> **Points:** 3

## User Story

**As an** operator refining a request
**I want** my open questions directed at the actual named amigo seats
**So that** clarification is done by the engineering-led panel, not an anonymous role list.

## Acceptance Criteria

### AC1: refine resolves the engineering-led panel and carries it in the result; --skip-personas degrades to roles

- **Given** a refine with `--question`
- **When** `refine.refine(...)` runs (and again with skip_personas)
- **Then** the result's `consult` names the resolved seats engineering-led (lead = the engineering seat), and skip-personas gives role-label seats
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_amigo_consult.RefineTriageConsultTests.test_refine_result_carries_named_seats tests.test_amigo_consult.RefineTriageConsultTests.test_refine_skip_personas_degrades_to_roles
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
