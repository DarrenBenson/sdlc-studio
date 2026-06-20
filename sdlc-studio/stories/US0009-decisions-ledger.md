# US0009: Persisted decisions ledger

> **Status:** Ready
> **Epic:** [EP0007: Agentic Orchestration](../epics/EP0007-orchestration.md)
> **Owner:** Autosprint (CR0020, by hand)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** autosprint loop
**I want** to persist decisions to a committed append-only ledger
**So that** rulings survive context compaction and resume, instead of being
re-litigated after a reset (RFC0001 D4/WS5).

## Context

Implements RFC0001 WS5 (D4: a committed, append-only per-tranche ledger).
`sdlc-studio/decisions/<tranche>.md` holds a table of rulings. Append-only: open in
append mode, write a header on first touch, never read-modify-truncate (the footgun
that emptied US0006). Pure stdlib; reuses `lib/sdlc_md` (`now_iso8601`, `slug`).

## Acceptance Criteria

### AC1: Append a ruling

- **Given** a tranche `CR0020` and a clean decisions dir
- **When** `append_decision(root, "CR0020", "drop PL files", "evidence: 0.27%")` runs
- **Then** `sdlc-studio/decisions/CR0020.md` exists with a header and one row carrying the timestamp, decision and rationale
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ledger.py::AppendTests::test_creates_and_appends
- **Verified:** pending

### AC2: Append-only (no truncation)

- **Given** a ledger with two existing rulings
- **When** a third is appended
- **Then** all three rows are present in order (earlier rulings are never lost)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ledger.py::AppendTests::test_append_only_preserves
- **Verified:** pending

### AC3: Read the ledger back

- **Given** a tranche ledger with rulings
- **When** `read_ledger(root, "CR0020")` runs
- **Then** it returns the rulings as a list of dicts (decision, rationale, at)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ledger.py::ReadTests::test_reads_rows
- **Verified:** pending

### AC4: CLI record + show

- **Given** the CLI
- **When** `ledger.py record --tranche CR0020 --decision d --rationale r` then `ledger.py show --tranche CR0020`
- **Then** record exits 0 and show prints the ruling
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ledger.py::CliTests::test_record_then_show
- **Verified:** pending

## Implementation

`scripts/ledger.py`: `append_decision(root, tranche, decision, rationale)`,
`read_ledger(root, tranche)`, `record`/`show` subcommands (model: `next_id.py`).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0020) | Decomposed from CR0020 / RFC0001 WS5 |
