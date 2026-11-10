# US1149: The sprint entry names the projected re-read cost when the orchestrating session holds more than 80k tokens, under sprint.fresh_session warn or block, and the cost anatomy flags a run whose orchestrator averages over 150k a call

> **Status:** Draft
> **Delivers:** CR0670
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py, changelog.d/US1149.md
> **Epic:** EP0302
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: {{define}}

- **Given** {{context}}
- **When** {{action}}
- **Then** {{outcome}}
- **Verify:** {{executable check}}

## Summary

CR0670's AC4 and AC5, deferred from run nine's first slice (D0435): the fresh-session warning at the sprint entry, and the before/after cost check measured on the next sprint. Delivers: CR0670.

## Planning notes

- Evidence for the threshold, 2026-11-10: a consuming project delivering with Grok 4.7 through Cursor ran a whole sprint in one agent, and requests over 200k tokens made up 58% of its bill. A fresh agent every five or so units, from one short handoff file, with one blocking CI watch in place of polling (CR0697), brought it to about $2.58 a unit. Groom the warning's threshold and its default against this, and against the 200k price step some models charge above (xAI's long-context rate; BG1331).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-10 | Darren Benson (operator) | Planning note: a consuming project's cost evidence for the session budget |
