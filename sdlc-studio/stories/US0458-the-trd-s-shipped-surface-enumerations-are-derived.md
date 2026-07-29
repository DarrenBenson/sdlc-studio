# US0458: The TRD's shipped-surface enumerations are derived from the code and the router, and the stale CR0132 caveat is refused by name

> **Status:** Review
> **Delivers:** CR0430
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, tools/tests/test_trd_surface_derivation.py
> **Epic:** EP0168
> **Points:** 3

## User Story

**As a** someone using the TRD as a migration blueprint for another harness
**I want** the command types, gate lanes and drift kinds to match the shipped router and the shipped constants, and the closed-work caveat gone
**So that** a rebuild is not planned against a surface that is three enumerations behind, and the document does not describe finished work as outstanding

## Acceptance Criteria

### AC1: the TRD type list equals the router's type table

- **Given** the Type Reference table in .claude/skills/sdlc-studio/SKILL.md (39 rows, lines 214-252) as the shipped router surface the TRD describes
- **When** the guard parses that table and the TRD section 5 Command surface list (30 entries, trd.md:217-227) and compares them as sets
- **Then** they are equal, so a type in one and not the other fails in either direction - which also resolves section 6's contradiction that SKILL.md's table lists `migrate` while section 5 omits it - and a renamed heading on either side fails naming it rather than comparing an empty set
- **Verify:** pytest tools/tests/test_trd_surface_derivation.py::ShippedSurfaceIsDerived::test_the_trd_type_list_equals_the_router_type_table
- **Verified:** yes (2026-07-29)

### AC2: the default sweep lane list equals the gate's registry

- **Given** gate.DEFAULT_CHECKS, whose 17 keys are the shipped default lane registry
- **When** the guard imports it and compares its keys against the lanes the TRD gate-tier passage enumerates (trd.md:166-178, currently 14)
- **Then** they are equal, so a lane added to or removed from the registry without a TRD edit reddens the guard, and window, batch-size and changelog-fragments stop being absent from the document
- **Verify:** pytest tools/tests/test_trd_surface_derivation.py::ShippedSurfaceIsDerived::test_the_default_sweep_lane_list_equals_gate_default_checks
- **Verified:** yes (2026-07-29)

### AC3: both drift-kind passages equal the shipped vocabulary

- **Given** reconcile.DRIFT_KINDS (14 entries) and the two TRD passages that enumerate drift kinds - the Error/report format paragraph (trd.md:280-281) and ADR-003's Decision (trd.md:691-692) - each currently listing the same stale five
- **When** the guard extracts each passage by its own heading boundary and compares both against the tuple
- **Then** both equal the shipped set and therefore each other, so the document cannot answer one question two ways, and a passage the guard cannot locate fails rather than silently comparing nothing
- **Verify:** pytest tools/tests/test_trd_surface_derivation.py::ShippedSurfaceIsDerived::test_both_drift_kind_passages_equal_reconcile_drift_kinds
- **Verified:** yes (2026-07-29)

### AC4: the CR0132 caveat is refused by name and its premise is checked against the backlog

- **Given** the sentence 'The `count-mismatch` finding does not yet meet this bar; closing it is CR0132' at trd.md:292-293, and CR0132's status resolved from the workspace
- **When** the guard extracts the Error/report format block and applies a denylist holding that sentence, then resolves CR0132's status
- **Then** the sentence is absent from the block and CR0132 resolves Complete, so the denylist is justified by the backlog rather than asserted; reintroducing the sentence reddens, and an id that resolves nowhere fails loud with the id named instead of being skipped as clean
- **Verify:** pytest tools/tests/test_trd_surface_derivation.py::ClosedWorkIsNotDescribedAsOutstanding::test_the_cr0132_caveat_is_absent_and_cr0132_resolves_complete
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
