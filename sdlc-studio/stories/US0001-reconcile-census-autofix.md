<!--
Template: User Story (Streamlined)
File: sdlc-studio/stories/US0001-reconcile-census-autofix.md
Status values: See reference-outputs.md
Related: help/story.md, reference-story.md
-->
# US0001: Census-based reconcile with scoped auto-fix

> **Status:** Ready
> **Epic:** [EP0005: Quality & Drift Control](../epics/EP0005-quality-drift.md)
> **Owner:** Darren Benson
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** Orchestrator / Operator
**I want** a deterministic census of artifact files compared against their `_index.md` tables, with the mechanical fixes spelled out and the judgement calls left to me
**So that** index drift is detected reproducibly without a script ever silently re-transitioning a story or epic

## Context

### Persona Reference

**Orchestrator / Operator** - runs reconcile and review at cadence boundaries; needs trustworthy state, not guesswork.
[Full persona details](../personas.md#orchestrator--operator)

### Background

Through the manual era, reconcile re-read every artifact in-context and trusted "the count looks right". `scripts/reconcile.py detect` replaces that with a file census: the artifact files on disk are truth, `_index.md` tables are derived. The script is read-only - it emits a JSON drift report with a human-readable `fix` string per item; Claude (or a separately reviewed apply step) does the editing. This is the worked example of doctrine rule 3 (file is truth, index is derived).

---

## Inherited Constraints

> See Epic for full constraint chain. Key constraints for this story:

| Source | Type | Constraint | AC Implication |
| --- | --- | --- | --- |
| Epic | Architecture | Pure stdlib, read-only over the workspace, unit-tested | No third-party imports; the script never writes an artifact file |
| Epic | Behaviour | Fixes mechanical drift without auto-transitioning judgement calls | Done is never auto-assigned; the script reports, it does not apply |
| PRD | Determinism | Running reconcile twice yields the same result | Output depends only on disk state, not run order |

---

## Acceptance Criteria

### AC1: Census built from disk, indexes treated as derived

- **Given** a workspace with `sdlc-studio/stories/US0001-login.md` carrying `> **Status:** Done` and a `sdlc-studio/stories/_index.md` row showing the same story as `Draft`
- **When** I run `python3 scripts/reconcile.py detect --scope stories --root . --format json`
- **Then** the report `types.story.census_total` counts the on-disk file, and the `drift` array contains an item with `"kind": "status-mismatch"`, `"id": "US0001"`, `"file_status": "Done"`, `"index_status": "Draft"`, and `"fix": "set index status of US0001 to Done"`
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/reconcile.py detect --scope stories --format json | python3 -c "import json,sys; d=json.load(sys.stdin); assert 'story' in d.get('types', {})"
- **Verification target:** functional
- **Verified:** no

### AC2: Four drift classes plus summary-count drift

- **Given** a story type whose index has a row with no backing file (active status), a file with no index row, a file whose status differs from its row, and a summary table whose totals disagree with the row tally
- **When** I run `detect`
- **Then** the `drift` array uses exactly these `kind` values - `status-mismatch`, `missing-row`, `orphan-row`, `count-mismatch`, and `missing-index` (when the whole index file is absent) - and `summary.by_kind` tallies each
- **And** a row in a non-file-implying status (`Proposed`, `Draft`, `Deferred`, `Superseded`, `Withdrawn`, `Rejected`, `Won't Implement`, `Won't Fix`) or a non-vocabulary status with no file is treated as an intentional reservation, not flagged as `orphan-row`
- **Verify:** grep "orphan-row" .claude/skills/sdlc-studio/scripts/reconcile.py
- **Verification target:** functional
- **Verified:** no

### AC3: `--scope` limits the types examined

- **Given** I want to reconcile only one artifact family
- **When** I pass `--scope stories` (choices: `stories`, `epics`, `crs`, `rfcs`, `plans`, `test-specs`, `indexes`)
- **Then** only that scope's types are censused - `report.scope` echoes the value, `indexes` expands to all six index-driven types (`story`, `epic`, `cr`, `rfc`, `plan`, `test-spec`), and omitting `--scope` defaults to all six with `report.scope == "all"`
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/reconcile.py detect --scope epics --format json | python3 -c "import json,sys; assert json.load(sys.stdin).get('scope')=='epics'"
- **Verification target:** functional
- **Verified:** no

### AC4: Mechanical auto-fix versus judgement-call reporting

- **Given** the script has detected drift
- **When** the report is consumed
- **Then** each drift item carries a mechanical `fix` string (e.g. `add US0007 (Ready) to the index`, `recompute the summary counts from the index rows`) that Claude applies, while judgement calls - checkbox / dependency / PRD-feature drift, CR completion cascades, the changelog - are NOT in the report and stay the operator's call per `reference-reconcile.md`
- **And** the script itself writes no artifact file; a `status-mismatch` never propagates a status TO `Done` (Done is only ever copied from a file that already declares it)
- **Verify:** grep "read-only" .claude/skills/sdlc-studio/scripts/reconcile.py
- **Verification target:** functional
- **Verified:** no

### AC5: JSON report shape, dry-run default, and `--write-report`

- **Given** a `detect` run
- **When** I read the output
- **Then** the top-level object has keys `generated_at` (ISO-8601 Z), `scope`, `types` (per-type: `census_total`, `census_counts`, `row_counts`, `index_exists`, `index_summary`, `drift`), `drift` (flattened), and `summary` (`drift_items`, `by_kind`)
- **And** detection is read-only by default; passing `--write-report` also writes `sdlc-studio/.local/reconcile-report.json`
- **And** the process exits `1` when any drift exists and `0` when clean
- **Verify:** shell test "$(python3 .claude/skills/sdlc-studio/scripts/reconcile.py detect --scope rfcs --format json >/dev/null; echo $?)" = 0 -o "$?" = 1
- **Verification target:** functional
- **Verified:** no

> **Verification target tiers:** `functional` (single round-trip – default) | `conversational` (multi-turn / multi-step session continuity) | `soak` (live traffic over a window) | `live` (operator-confirmed in production). End-to-end ACs default to `conversational`; production-affecting ACs default to `soak`; ACs shipping behind a flag awaiting promotion default to `live`. See `reference-test-best-practices.md#verification-depth-tiers`.

---

## Scope

### In Scope

- `scripts/reconcile.py detect`: census, four drift classes plus count-mismatch and missing-index, `--scope`, `--root`, `--format`, `--write-report`.
- The read-only contract: emit drift `fix` strings, never edit artifacts.

### Out of Scope

- Applying the fixes (Claude does this from the report).
- `--verify` AC execution: a reconcile-command concern that delegates to `verify_ac.py` (US0002); the `detect` subcommand has no `verify` scope.
- Judgement calls: checkbox/dependency/PRD-feature drift, CR cascades, changelog, numeric-claim drift in prose docs.

---

## Technical Notes

`file_census` maps normalised ID -> `(display id, raw Status)`; a file with a recognised status wins over a status-less namesake sharing the ID. `parse_index` is column-order-resilient (first ID cell, first valid-status cell) and reads the `| Status | Count |` summary. Matching tolerances (from `lib/sdlc_md.py`): IDs compare case- and punctuation-insensitively (`cr0001.md` == `CR-0001`); decorated statuses (`Done (v2.83.0) · …`) canonicalise to their vocabulary token; `*-consultations.md` files are excluded.

### API Contracts

```text
python3 scripts/reconcile.py detect [--scope {crs,epics,indexes,plans,rfcs,stories,test-specs}]
                                    [--root ROOT] [--format {text,json}] [--write-report]

JSON: { "generated_at", "scope", "types": { <type>: { "census_total", "census_counts",
        "row_counts", "index_exists", "index_summary", "drift": [...] } },
        "drift": [ { "type", "id", "kind", "file_status", "index_status", "fix" } ],
        "summary": { "drift_items", "by_kind": { <kind>: int } } }
```

### Data Requirements

Reads `<type-dir>/*.md` artifact files and `<type-dir>/_index.md`. Optional write target: `sdlc-studio/.local/reconcile-report.json`.

---

## Edge Cases & Error Handling

| Scenario | Expected Behaviour |
| --- | --- |
| Index file absent but files exist on disk | One `missing-index` drift item with `fix` to create the index from the N files |
| File has no `> **Status:**` line | Asserts nothing; not compared, never status-mismatches (count reconciled against index rows for such types, e.g. CRs) |
| Index row status is non-vocabulary (e.g. `Retired`) with no file | Treated as intentional reservation; not an `orphan-row` |
| `cr0001.md` on disk, `CR-0001` in index | Same record via `norm_id`; never double-counted as both missing-row and orphan-row |
| Two files share an ID, one status-less | Recognised-status file wins; status-less namesake does not clobber it |
| Decorated status `Done (v2.83.0) · **CR:** CR-0088` vs index `Done` | Canonicalises to `Done`; no mismatch |
| `--write-report` and `.local/` does not exist | Directory created (`parents=True, exist_ok=True`) before write |
| KeyboardInterrupt during run | Exit code 130 |
| Any unexpected exception | `error: <msg>` on stderr, exit code 1 |

> **Minimum edge cases:** 8 for API stories, 5 for others

---

## Test Scenarios

- [ ] Status-mismatch detected when file `Done` and index `Draft`
- [ ] Missing-row detected for a file with no index row
- [ ] Orphan-row detected only for active/terminal index rows with no file
- [ ] Reserved/retired/non-vocabulary index rows are not flagged as orphans
- [ ] Count-mismatch detected when summary totals disagree with row tally
- [ ] Missing-index detected when index absent but files present
- [ ] `--scope indexes` expands to all six index-driven types
- [ ] Exit code 1 when drift present, 0 when clean
- [ ] `--write-report` writes valid JSON to `.local/reconcile-report.json`
- [ ] Two runs over unchanged disk produce identical reports (idempotent)

> **Minimum test scenarios:** 8 for API stories, 6 for UI

---

## Dependencies

### Story Dependencies

| Story | Type | What's Needed | Status |
| --- | --- | --- | --- |
| [US0002](US0002-verify-ac-gate.md) | Related | `reconcile --verify` delegates AC execution to verify_ac | Ready |

### External Dependencies

| Dependency | Type | Status |
| --- | --- | --- |
| Python 3.10+ | Runtime | Available |

---

## Estimation

**Story Points:** 5
**Complexity:** Medium

---

## Rollback Envelope

> Required when `affects_production_runtime: true`; optional otherwise. See `reference-story.md#rollback-envelope`.

**Affects production runtime:** false

Not applicable – story does not change runtime behaviour. The script is read-only over the workspace.

---

## Open Questions

- [ ] None - behaviour fully extracted from `scripts/reconcile.py`. - Owner: Darren Benson

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Story extracted (brownfield) from scripts/reconcile.py |
