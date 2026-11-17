# US1250: The plan forecasts dollars from measured dollars per point, naming its runs, with a stated fallback

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0703
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_dollar_rate_fit.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_cost_forecast.py
> **Epic:** EP0344
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The plan forecasts dollars from measured dollars per point, naming its runs, with a stated fallback
**So that** CR0703 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The plan's dollar forecast comes from measured dollars per point over the recent priced runs

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: The plan's dollar forecast comes from measured dollars per point over the recent priced runs, naming the runs it was fitted from, and falls back to priced times the input price only when fewer than three runs carry a dollar figure, saying so.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
