# US0980: A lane return records the builder's token and minute totals

> **Status:** Done
> **Depends on:** US0979
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
- **Verified:** yes (2026-10-02)

### AC2: A partial delegated total withholds the ratio

- **Given** a run of two delivered units where only one lane return supplied --tokens
- **When** the page is derived
- **Then** the Estimates tokens ratio reads withheld - delegated spend not measured for every unit, never a number. Fails on: a fix that computes the ratio from the units that supplied totals
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_delegated_tokens.py::LaneDelegatedTokensTests::test_a_partial_delegated_total_withholds_the_ratio
- **Verified:** yes (2026-10-02)

### AC3: Agent minutes take precedence over the lane span

- **Given** a unit X with a lane span and a lane return supplying --minutes 40
- **When** the page is derived
- **Then** X's minutes read 40 labelled agent minutes, and the lane span is used only when no agent total is supplied. Fails on: a fix that sums or silently picks one source
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_delegated_tokens.py::LaneDelegatedTokensTests::test_agent_minutes_take_precedence_over_the_lane_span
- **Verified:** yes (2026-10-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-02 | engineering seat (orchestrator) | Groomed from the request's criterion; premise: RPT0014 reads NOT MEASURED / 0.2x |
| 2026-10-02 | qa and engineering seats (goal review) | Controls added so the goal cannot go green on a fixture. US0980 depends on US0979. |
