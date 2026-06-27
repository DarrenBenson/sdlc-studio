# US0040: index-archive writer + terminal-status vocab flag + dry-run (CR0125)

> **Status:** Ready
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new
> **Epic:** EP0010
> **Persona:** Dani (Engineering)
> **Depends on:** -

## User Story

**As** the Engineering amigo
**I want** a deterministic writer that relocates terminal index rows into a derived archive sub-index
**So that** live `_index.md` files stay small without losing census or discoverability

## Context

### Persona Reference

**Dani (Engineering)** - the build-side amigo, accountable for the deterministic tooling under `scripts/` and for keeping the derived index honest against the file census.
[Full persona details](../personas.md#dani-engineering)

### Background

This story implements the writer half of CR0125. The read path (`reconcile.parse_index`) already unions live `_index.md` rows with any rows found in `<type>/archive/**/*.md` sub-indexes, so a relocated row is still seen as in the index. What is missing is the writer that pulls terminal rows out of the live table.

---

## Inherited Constraints

> See Epic for full constraint chain. Key constraints for this story:

| Source | Type        | Constraint                                                     | AC Implication                                     |
| ------ | ----------- | -------------------------------------------------------------- | -------------------------------------------------- |
| Epic   | Determinism | The index is derived from the file census, never hand-authored | AC4 proves census == unioned index after archiving |
| PRD    | Performance | Not applicable - skill-internal change                         | None                                               |
| PRD    | Security    | Not applicable - skill-internal change                         | None                                               |

---

## Acceptance Criteria

### AC1: writer relocates terminal rows, leaving active rows plus summary

- **Given** a live `<type>/_index.md` carrying both active and terminal rows plus the canonical summary count block
- **When** the archive writer verb runs
- **Then** rows whose status is terminal (vocab-derived) move to `<type>/archive/_index-{period}.md`, the live index keeps only active rows plus the canonical summary block, and a re-run moves nothing new (idempotent)
- **Verify:** pytest -k test_index_archive_writer
- **Verification target:** functional
- **Verified:** no

### AC2: terminal statuses come from the vocab, not a hardcoded list

- **Given** per-type status vocabs that differ (stories use Done/Won't Implement/Superseded, CRs add Built)
- **When** the writer classifies a row as terminal
- **Then** the terminal set is read from `status_vocab(type_, root)` via a vocab-metadata flag, not a literal list, and CR `Built` is classed active, not terminal
- **Verify:** pytest -k test_terminal_status_from_vocab
- **Verification target:** functional
- **Verified:** no

### AC3: dry-run previews and writes nothing; unclassifiable row fails loud

- **Given** a live index that may contain a row whose status is not in the vocab
- **When** the writer runs in dry-run mode, or encounters an unclassifiable row in a real run
- **Then** dry-run previews counts per status plus the target sub-index path and writes nothing; an unclassifiable row aborts with a non-zero exit and no partial write (fail loud, LL0008)
- **Verify:** pytest -k test_index_archive_dryrun_and_failloud
- **Verification target:** functional
- **Verified:** no

### AC4: reconcile stays clean and the summary still equals the full census

- **Given** an index that has just been archived
- **When** `reconcile detect` runs
- **Then** it reports drift 0 (census == unioned live + archive rows) and the live summary counts still equal the full census (archived rows still tallied)
- **Verify:** pytest -k test_index_archive_reconcile_clean
- **Verification target:** functional
- **Verified:** no

---

## Scope

### In Scope

- The archive writer verb (relocate terminal rows into the derived sub-index, idempotent)
- The vocab-metadata terminal flag read via `status_vocab(type_, root)`
- Dry-run preview mode
- Fail-loud behaviour on an unclassifiable or unplaceable row (LL0008)

### Out of Scope

- `next_id` archive-union changes - that is US0041
- The lessons summary - that is US0044
- Section-sharding the monolithic PRD/TRD/TSD documents (a separate RFC, per CR0125)

---

## Technical Notes

The writer lives in `.claude/skills/sdlc-studio/scripts/reconcile.py` (alongside `parse_index`, whose archive-union read path it mirrors). The terminal-status classifier and the vocab-metadata flag live in `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py`, beside `status_vocab`. The writer must leave the canonical summary count block intact in the live index, since that block already counts all states including archived rows.

### API Contracts

Not applicable - skill-internal Python helpers, no external interface.

### Data Requirements

Source: live `<type>/_index.md` rows and the per-type status vocab. Target: derived `<type>/archive/_index-{period}.md`. No new data store; both sides are derived from the file census.

---

## Edge Cases & Error Handling

| Scenario                                        | Expected Behaviour                                                                     |
| ----------------------------------------------- | -------------------------------------------------------------------------------------- |
| Live index has no terminal rows                 | No-op: nothing moved, no archive sub-index created, exit zero                          |
| A row carries a status not present in the vocab | Abort with non-zero exit, no partial write, no false "archived N rows" report (LL0008) |
| Writer re-run on an already-archived index      | Idempotent: no rows moved, summary unchanged                                           |

---

## Test Scenarios

- [ ] Archive a mixed index, assert terminal rows land in the sub-index and active rows plus the summary stay live, then re-run and assert nothing moves
- [ ] CR index with a `Built` row: assert `Built` stays in the live index (classed active) while `Complete` rows are archived
- [ ] Dry-run against a mixed index: assert per-status counts and the target path are reported and no file is written
- [ ] Inject a row with an unknown status: assert non-zero exit and the live index is untouched

---

## Dependencies

### Story Dependencies

None

### External Dependencies

| Dependency | Type                          | Status    |
| ---------- | ----------------------------- | --------- |
| pytest     | Test runner (already present) | Available |

---

## Estimation

**Story Points:** 5
**Complexity:** Medium

---

## Rollback Envelope

**Affects production runtime:** false

*Not applicable - story does not change runtime behaviour.*

---

## Open Questions

None

---

## Revision History

| Date       | Author | Change                                               |
| ---------- | ------ | ---------------------------------------------------- |
| 2026-06-27 | Dani   | Authored to Ready (design rung, breakdown of CR0125) |
