# US1265: The commit's selection includes a test that runs other test modules by path when one of those modules is staged

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0713
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py, tools/tests/test_lean_release_notes.py
> **Epic:** EP0353
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The commit's selection includes a test that runs other test modules by path when one of those modules is staged
**So that** CR0713 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The code path each recorded hit names (its finding is under Hits above) is fixed, so the failure

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: The code path each recorded hit names (its finding is under Hits above) is fixed, so the failure LC-019 describes cannot recur there: RUN-01M7GEHM on BG1395; RUN-01M7HA6R on US1170.

### AC2: Any check this CR proposes names the lane, refusal, baseline or pin it retires, and ships only in

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: Any check this CR proposes names the lane, refusal, baseline or pin it retires, and ships only in exchange for it; a check that retires nothing is not added.

### AC3: Once the path is fixed and this CR closes Complete, LC-019 reads `graduated` in

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: Once the path is fixed and this CR closes Complete, LC-019 reads `graduated` in sdlc-studio/lessons.jsonl; a class that no longer describes a live failure is Rejected here instead, and the close then retires it until it recurs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
