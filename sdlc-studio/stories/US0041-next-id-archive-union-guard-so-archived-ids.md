# US0041: next_id archive-union guard so archived ids are never reallocated (CR0125)

> **Status:** Ready
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new
> **Epic:** EP0010
> **Persona:** Dani (Engineering)
> **Depends on:** US0040

## User Story

**As** the Engineering amigo
**I want** `next_id` to union the archive sub-indexes in its id-from-index guard
**So that** an id whose row has been archived is never reallocated.

## Context

### Persona Reference

**Dani (Engineering)** - the engineering amigo: owns the skill's Python helpers and the deterministic id-allocation path, and guards against silent id reuse.
[Full persona details](../personas.md#dani-engineering)

### Background

This story implements part of CR0125. CR0125 tiers the derived `_index.md`: a writer
(US0040) relocates terminal rows out of the live `<type>/_index.md` into
`<type>/archive/_index-{period}.md` sub-indexes, while the artefact files stay put. The
reconcile read path already unions those sub-indexes (`parse_index`), so an archived row is
still seen as in the index.

`next_id` keeps its own belt-and-braces guard against id reuse: it reads the live index rows
so an id whose file was deleted but whose row remains is never re-issued
(`index_row_ids`, next_id.py:67-79; consumed by `allocate_number`, next_id.py:82-92). Today
that guard reads only the live `<type>/_index.md`. Once terminal rows move into
`<type>/archive/**/*.md`, an id whose row has been relocated would drop out of the guard's
view. The files do not move, so the file scan still catches it in practice - but the
id-from-index check must mirror `parse_index`'s archive union so the guard is not quietly
weakened. This story adds that union and nothing else; the relocating writer is US0040.

---

## Inherited Constraints

> See Epic for full constraint chain. Key constraints for this story:

| Source | Type        | Constraint                                                                   | AC Implication                                    |
| ------ | ----------- | ---------------------------------------------------------------------------- | ------------------------------------------------- |
| Epic   | Correctness | An allocated id must never collide with any id ever issued, live or archived | The guard must see archived index rows (AC1, AC2) |
| PRD    | Performance | Not applicable - skill-internal change                                       | None                                              |
| PRD    | Security    | Not applicable - skill-internal change                                       | None                                              |

---

## Acceptance Criteria

### AC1: next_id unions archive sub-index rows in its id-from-index guard

- **Given** terminal rows have been relocated into `<type>/archive/**/*.md` sub-indexes
- **When** `next_id` builds its id-from-index guard for that type
- **Then** it unions the archive sub-index rows with the live `_index.md` rows, mirroring `parse_index`, so every archived id is counted by the guard
- **Verify:** pytest -k test_next_id_unions_archive
- **Verification target:** functional
- **Verified:** no

### AC2: an archived id is never reallocated even if its artefact file is gone

- **Given** an id whose row sits in an archive sub-index and whose artefact `.md` file has been removed
- **When** `next_id` allocates the next id for that type
- **Then** the archived id is excluded from the candidate set and is never re-issued
- **Verify:** pytest -k test_next_id_archived_id_not_reused
- **Verification target:** functional
- **Verified:** no

---

## Scope

### In Scope

- The archive union in `next_id`'s id-from-index guard only: read `<type>/archive/**/*.md` sub-index rows and union them with the live `_index.md` rows, mirroring `parse_index`.

### Out of Scope

- The writer verb that relocates terminal rows into the archive sub-indexes (US0040).

---

## Technical Notes

Touches `.claude/skills/sdlc-studio/scripts/next_id.py`. `index_row_ids` (next_id.py:67-79)
currently reads a single live `<type>/_index.md` and extracts row ids via
`reconcile._index_row_ids`. Extend it to also glob `<type>/archive/**/*.md`, parse each
sub-index's rows the same way, and return the union of ids. Reuse the existing reconcile
helper rather than re-implementing row parsing, so the guard stays in lockstep with
`parse_index`'s archive union (reconcile.py:225-247). `allocate_number` already folds
`index_row_ids` into its `max(...)` base, so no caller change is needed once the union is in
place. META_TYPES (no derived index) keep returning an empty list.

### API Contracts

No external API. `index_row_ids(type_, repo_root) -> list[int]` keeps its signature; only its
result set widens to include archived rows.

### Data Requirements

Reads `<type>/_index.md` and `<type>/archive/**/*.md` sub-indexes. No writes.

---

## Edge Cases & Error Handling

| Scenario                                                              | Expected Behaviour                                                    |
| --------------------------------------------------------------------- | --------------------------------------------------------------------- |
| No `<type>/archive/` directory exists yet (pre-US0040 repos)          | Union degrades to the live index alone; no error, behaviour unchanged |
| Same id appears in both the live index and an archive sub-index       | Deduplicated by the set union; counted once                           |
| Multiple archive sub-indexes (`_index-2026Q1.md`, `_index-2026Q2.md`) | All matched by the glob and unioned                                   |
| Archive sub-index file present but empty or header-only               | Contributes zero ids; no error                                        |

---

## Test Scenarios

- [ ] `test_next_id_unions_archive`: seed a live index plus an archive sub-index carrying a distinct id; assert `index_row_ids` returns the union of both.
- [ ] `test_next_id_archived_id_not_reused`: archive an id and delete its artefact file; assert `allocate_number` returns an id strictly greater than the archived id.

---

## Dependencies

### Story Dependencies

| Story                                                                   | Type     | What's Needed                                                                                             | Status |
| ----------------------------------------------------------------------- | -------- | --------------------------------------------------------------------------------------------------------- | ------ |
| [US0040](US0040-index-archive-writer-terminal-status-vocab-flag-dry.md) | blocking | The archive sub-index writer must exist so there are `<type>/archive/**/*.md` rows for the guard to union | Ready  |

### External Dependencies

| Dependency | Type | Status |
| ---------- | ---- | ------ |
| None       | -    | -      |

---

## Estimation

**Story Points:** 2
**Complexity:** Low

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

</content>
</invoke>
