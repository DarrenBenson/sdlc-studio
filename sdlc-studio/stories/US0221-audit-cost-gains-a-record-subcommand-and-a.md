# US0221: audit_cost gains a record subcommand and a committed evidence ledger; estimate from measured medians with a named fallback

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/audit_cost.py, .claude/skills/sdlc-studio/reference-audit.md
> **Epic:** EP0073
> **Points:** 5

## User Story

**As an** operator confirming an audit fan-out
**I want** each finished audit's actuals recorded against its estimate in a committed ledger, and future estimates derived from those measurements
**So that** the pre-flight number tracks what audits really cost instead of staying frozen at one 2026-07-15 reference run

## Acceptance Criteria

### AC1: Record actuals to a committed ledger

- **Given** an audit run has finished and its actual agents, tokens and wall minutes are known
- **When** the operator runs `audit_cost.py record` with the run's scope (lenses, rounds, votes), the estimate it was given, the measured actuals and optional notes
- **Then** a row carrying date, lenses, rounds, votes, estimated agents/tokens, actual agents/tokens/minutes and notes is appended to a committed evidence ledger, leaving earlier rows intact
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_audit_cost.py -k RecordSubcommandTests

### AC2: Estimate from measured medians, naming the basis

- **Given** the evidence ledger holds at least one recorded run
- **When** an estimate is requested
- **Then** candidates-per-lens and tokens-per-agent come from the median of the recorded runs rather than the shipped constants, the shipped constants are still used when the ledger is empty or unreadable, and the output states which of the two bases it used
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_audit_cost.py -k LedgerBasisTests

### AC3: Pre-flight step 4 instructs recording, not just reporting

- **Given** an agent following `reference-audit.md#audit-preflight`
- **When** it reaches step 4 after a run finishes
- **Then** the step tells it to record the actuals with the `record` subcommand, so the measurement lands in the ledger rather than only in chat
- **Verify:** grep "audit_cost.py record" .claude/skills/sdlc-studio/reference-audit.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
