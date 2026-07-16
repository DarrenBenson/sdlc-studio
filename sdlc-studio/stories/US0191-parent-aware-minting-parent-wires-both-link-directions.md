# US0191: parent-aware minting (--parent wires both link directions atomically) and rfc resolve for decision-row surgery

> **Status:** Draft
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/rfc.py, .claude/skills/sdlc-studio/scripts/tests/test_rfc.py
> **Epic:** EP0061
> **Depends on:** BG0177
> **Points:** 3

## User Story

**As** Maya Okafor (solo founder-engineer, the Primary)
**I want** the RFC triage's paperwork tool-carried: parent-aware minting and decision-row surgery
**So that** a spawned child can never be born with asymmetric links and a resolved decision is a command, not regex surgery

## Acceptance Criteria

### AC1: --parent wires both directions atomically

- **Given** file_finding/artifact minting with --parent RFCxxxx
- **When** the child is created
- **Then** the child carries Parent and the parent's Decomposed-into gains the child, validated before any write; reconcile shows no asymmetry
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_rfc.py -k ParentMint

### AC2: rfc resolve edits exactly one row

- **Given** an RFC with a decision table
- **When** rfc resolve --rfc X --decision D2 --resolution '...' --refs CRxxxx runs
- **Then** that row becomes Resolved with text+refs, a revision row is appended, other rows are byte-identical; unknown RFC/decision refused
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_rfc.py -k Resolve

### AC3: Triage ceremony documented

- **Given** a reader of the RFC reference
- **When** they run a triage
- **Then** reference-rfc.md documents decide -> resolve -> spawn
- **Verify:** grep "resolve" .claude/skills/sdlc-studio/reference-rfc.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
