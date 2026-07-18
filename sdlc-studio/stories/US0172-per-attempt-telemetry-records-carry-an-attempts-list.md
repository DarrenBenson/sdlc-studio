# US0172: Per-attempt telemetry: records carry an attempts list of model and tokens, a legacy record reads as one attempt

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/telemetry.py
> **Epic:** EP0048
> **Points:** 5

## User Story

**As an** estimator that must stay falsifiable
**I want** telemetry to record model and tokens per attempt
**So that** an escalation shows its true summed cost instead of one flattering line

## Acceptance Criteria

### AC1: a record carries an attempts list; a legacy record reads as one attempt; nothing measured yields no fabricated attempt

- **Given** records with an attempts list, with only flat model/tokens, and with neither
- **When** `attempts_of` reads them
- **Then** the list is preserved in order, the legacy record reads as a single attempt, and a record with no measurement yields an empty list (no invented attempt)
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -B -m unittest tests.test_telemetry.AttemptsAndCostTests.test_legacy_record_reads_as_one_attempt tests.test_telemetry.AttemptsAndCostTests.test_attempts_list_is_preserved_in_order tests.test_telemetry.AttemptsAndCostTests.test_empty_attempts_falls_back_to_flat_fields tests.test_telemetry.AttemptsAndCostTests.test_no_measurement_yields_no_fabricated_attempt
- **Verified:** yes (2026-07-16)

### AC2: the writer path exists and records an escalation (not only the reader)

- **Given** the record CLI and the `transition set` close path
- **When** an escalation is recorded via `record --attempt MODEL:TOKENS` / `--attempts JSON`, or threaded through a terminal close
- **Then** the resulting record carries the ordered `attempts` list and `unit_cost` sums the true cost - so the reader is fed by a real writer, not only tests (BG0152)
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -B -m unittest tests.test_telemetry.TierFieldsTests.test_cli_record_accepts_attempts_writer tests.test_telemetry.TierFieldsTests.test_cli_record_accepts_attempts_json
- **Verified:** yes (2026-07-17)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-17 | sdlc-studio | AC2 added: writer path (record/transition `--attempt`) closes US0172's reader-only gap (BG0152) |
