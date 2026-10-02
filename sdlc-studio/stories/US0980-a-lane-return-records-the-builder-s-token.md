# US0980: A lane return records the builder's token and minute totals

> **Status:** Ready
> **Delivers:** CR0606
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_delegated_tokens.py, changelog.d/CR0606.md
> **Epic:** EP0271
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A lane return records the builder's token and minute totals
**So that** CR0606 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A lane return records agent totals and the ratio is withheld without them

- **Given** a run whose batch holds unit X
- **When** `sprint lane return --units X --tokens 250000 --minutes 40` passes and the page is derived, and separately a run where no delegated total is supplied is derived
- **Then** X's tokens and minutes read 250,000 and 40 tagged as agent totals and the run's delegated total includes them, and with no delegated total supplied the Estimates tokens ratio cell reads withheld rather than a number. Fails on: the current code has no --tokens on lane return and prints 0.2x
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_delegated_tokens.py::LaneDelegatedTokensTests::test_a_lane_return_records_agent_totals_and_the_ratio_is_withheld_without_them

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-02 | engineering seat (orchestrator) | Groomed from the request's criterion; premise: RPT0014 reads NOT MEASURED / 0.2x |
