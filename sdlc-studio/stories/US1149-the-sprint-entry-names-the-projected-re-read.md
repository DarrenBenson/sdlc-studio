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

- Evidence for the threshold, 2026-11-10: a consuming project delivering with Grok 4.7 through Cursor ran a whole sprint in one agent, and requests over 200k tokens made up about 58% of its bill. A fresh agent every five or so units, from one short handoff file, with one blocking CI watch in place of polling (CR0697), brought it to about $2.58 a unit by its first estimate (the measured figures are in the next note). Groom the warning's threshold and its default against this, and against the 200k price step some models charge above (xAI's long-context rate; BG1331).
- A consuming project's measured cost, delivering with Grok 4.7 through Cursor and priced at xAI's API rates (double for a prompt of 200k tokens or more), from its usage exports of 6 to 10 November 2026 (supplied by the operator, 2026-11-10). One agent running the whole sprint: $282.09 over 2,181 requests for 79 points ($3.57 a point). Prompts of 200k tokens or more were 29% of its requests and 57% of its cost, and $157.11 (56%) could not be tied to any unit, because the export stamped whole runs with one time until 9 November. A fresh agent per batch: batch A cost $25.72 for 8 points ($3.22 a point; 32% of the cost in long prompts). Batch B cost $23.08 for 5 points ($4.62 a point) counting the run that prepared its units, or $12.98 ($2.60 a point) for its delivery run alone, where long prompts were still 72% of the cost. Coordinator usage ($82.54 across all batches) is outside these figures, and batch C waits on an export past 11:41 GMT on 2026-11-10. The samples are small (8 and 5 points).

The data is in `sdlc-studio/change-requests/evidence/consumer-sprint-cost-2026-11-10.tar.gz`: per-request and per-unit CSVs, batch summaries, and the time windows and script that built them (the script imports a pricing module the bundle does not include). It is a scrubbed copy of the bundle supplied (SHA-256 fc960de33f14a39f; the copy 1d814234b30c426f): the project's repository name, two other project names, the operator's name and two local paths were replaced, and every figure is unchanged.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-10 | Darren Benson (operator) | Planning note: a consuming project's cost evidence for the session budget |
| 2026-11-10 | Darren Benson (operator) | Evidence: a consuming project's batch cost figures |
