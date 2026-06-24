# SDLC Studio Reference - Reconcile

> **Count blocks: one canonical summary per index.** `reconcile --apply` recomputes the counts of the **global** summary only - the `| Status | Count |` table that carries a `**Total**` row, or the sole summary in the file. Scoped per-epic/per-section `Status | Count` tables (no `Total`) are left to the author; do **not** add a `Total` row to a scoped count table or reconcile will treat it as the global summary.

Detailed workflow for the reconcile command that detects and fixes status drift across all artifacts.

<!-- Load when: running /sdlc-studio reconcile -->

---

> **Deterministic helper - do the census with the script, not by hand.**
> `python3 "$CLAUDE_SKILL_DIR/scripts/reconcile.py" detect [--scope <scope>] --format json`
> builds the file census and returns the drift list (`status-mismatch`,
> `missing-row`, `orphan-row`, `count-mismatch`, `missing-index`). Consume that
> JSON, then apply the fixes and the judgement calls the script does not make
> (checkbox / dependency / PRD-feature drift, CR completion cascades, the
> changelog). AC verification still runs via `verify_ac.py` (`--scope verify`).
> The manual walk below is the fallback when the script is unavailable.

## /sdlc-studio reconcile - Step by Step {#reconcile-workflow}

### 1. Parse Arguments

| Flag | Effect | Default |
| --- | --- | --- |
| `--dry-run` | Preview changes, don't apply | false |
| `--scope` | Limit to: `epics`, `stories`, `prd`, `indexes`, `crs`, `rfcs`, `verify`, `docs` | all |
| `--fix-counts` | When `--scope docs` (or no scope) finds drifted numeric claims, auto-fix them. Off by default because a prose numeric claim may be intentionally historical. | false |

### 2. Phase 1: Collect Ground Truth

Read all artifact files and extract their authoritative statuses. The file itself is the source of truth -- indexes are derived.

```text
a) Stories:
   - Glob sdlc-studio/stories/US*.md
   - For each: extract > **Status:** value
   - Build map: { US0001: "Done", US0002: "Done", ... }

b) Epics:
   - Glob sdlc-studio/epics/EP*.md
   - For each: extract > **Status:** value
   - For each: extract dependency table entries (epic ID + status)
   - For each: extract AC checkboxes (checked/unchecked)
   - For each: extract story breakdown checkboxes
   - Build map: { EP0001: { status: "Done", deps: [...], ac: [...], stories: [...] } }

c) PRD:
   - Read sdlc-studio/prd.md
   - Extract Feature Inventory table (feature name → epic mapping)
   - Extract each feature detail block: Status value, AC checkboxes
   - Build map: { "Config File Loader": { epic: "EP0001", status: "Not Started", ac: [...] } }

d) Plans and Test Specs:
   - Glob sdlc-studio/plans/PL*.md, extract statuses
   - Glob sdlc-studio/test-specs/TS*.md, extract statuses

e) RFCs (if sdlc-studio/rfcs/ exists):
   - Glob sdlc-studio/rfcs/RFC*.md
   - For each: extract > **Status:** value + the "Spawned CRs" links (for Accepted RFCs)
   - Build map: { RFC0001: { status: "Accepted", spawnedCRs: [...] }, ... }
```

### 3. Phase 2: Detect Drift

Compare ground truth against indexes and cross-references. Collect all discrepancies into a change list.

> **Census, not just compare (see [[LL0001]] – applies to EVERY indexed type: stories, epics, plans, test-specs, bugs, CRs, RFCs).** Rebuild each index from the on-disk file census and detect **three** drift classes, not just status mismatches:
> 1. **Status mismatch** – file `> **Status:**` ≠ the index-table row.
> 2. **Missing row** – a file exists on disk with **no** index-table row (a silent under-count; e.g. CR/bug files numbered past the last table row). Add the row.
> 3. **Orphan row** – an index row with no backing file on disk. Flag (and remove if confirmed).
>
> Recompute every Summary count **from the file census**, never by incrementing the existing (possibly-drifted) totals. A "count looks right" check is insufficient – enumerate the files.

#### Matching tolerances {#matching-tolerances}

`reconcile.py` normalises real-world artefact conventions before comparing, so the following are **not** flagged as drift (they were a recurring false-positive class fixed in v1.9.1):

- **ID format / case.** A lower-case filename matches an upper-case, punctuated index row. IDs compare case- and punctuation-insensitively (`norm_id`), so the same artefact is never double-counted as both a missing row and an orphan row.
- **Decorated statuses.** A status line such as `Done (v2.83.0) · **Points:** 8`, carrying trailing metadata, canonicalises to its leading vocabulary token (`Done`) before comparison. The decoration is informational and does not register as a mismatch.
- **Metadata without a blockquote.** Both `> **Status:** Done` and a plain `**Status:** Done` are read as the status field.
- **Status-less files assert nothing.** A file with no `> **Status:**` line (legacy docs, and most CRs) is not compared against its index row, so it never status-mismatches every run. The summary count is reconciled against the **index rows** for these types, not the file census.
- **`*-consultations.md` are not artefacts.** Supplementary notes filed under an artefact's ID (e.g. `EP0025-consultations.md`) are excluded from the census, so they do not clobber the real artefact's status or inflate counts.
- **Reserved / retired rows are not orphans.** An index row in a non-file-implying state (`Proposed`, `Draft`, `Deferred`, `Superseded`, …) or a custom non-vocabulary state (`Retired`, `Reserved`) with no backing file is treated as an intentional reservation, not an orphan. Only an active/terminal status (`Done`, `In Progress`, `Complete`, …) with no file is a real orphan.

```text
a) Story index drift:
   For each story in truth map:
     - Find row in stories/_index.md per-epic table → compare status
     - Find row in stories/_index.md All Stories table → compare status
     - If mismatch: add to change list

   Recalculate expected summary counts from truth map:
     - Count stories by status
     - Compare against stories/_index.md Summary table
     - If mismatch: add count corrections to change list

b) Epic index drift:
   For each epic in truth map:
     - Find row in epics/_index.md → compare status
     - If mismatch: add to change list

   Recalculate expected summary counts:
     - If mismatch: add count corrections

c) Dependency table drift:
   For each epic in truth map:
     - For each dependency table entry:
       - Look up the referenced epic's actual status from truth map
       - If dependency table shows different status: add to change list

d) Epic checkbox drift:
   For each epic in truth map:
     - For each story in story breakdown:
       - Look up story's actual status from truth map
       - If story is Done but checkbox unchecked: add to change list
     - For each AC checkbox:
       - If epic is Done, all AC should be checked
       - Quick codebase verification for each unchecked AC item
       - If verified but unchecked: add to change list

e) PRD feature status drift:
   For each PRD feature in truth map:
     - Look up the mapped epic's status
     - If epic is Done but feature status is not Complete: add to change list
     - If epic is Done, verify feature AC items against codebase
     - If verified but unchecked: add to change list

f) Plan/test-spec index drift:
   Same pattern as story index: compare file statuses vs index entries

g) Story dependency table drift:
   For each story in truth map:
     - Parse the `## Dependencies` → `### Story Dependencies` table
     - For each row: look up the referenced story's actual status from truth map
     - If dependency table shows different status: add to change list

h) Numeric-claim drift in prose docs {#numeric-claim-drift}:
   Project-level markdown docs (e.g. AGENTS.md, CLAUDE.md, README.md, docs/**)
   often embed numeric claims that drift silently across releases:
     - "vitest (N tests, M files)" / "N test cases" / "N lines of code"
     - "Version: X.Y.Z" footer strings
     - "N epics / M stories complete" status banners

   For each such claim, resolve it against a runnable source of truth:
     - Test counts: re-run the project's test command in count-only
       mode (vitest `--reporter=dot`, jest `--listTests | wc -l`,
       pytest `--collect-only -q | tail -1`) and compare.
     - Version strings: compare against package.json / pyproject.toml
       / Cargo.toml / etc.
     - Artifact counts ("N epics"): reuse the counts this phase
       already computed from the index files.

   If drifted:
     - Under --scope docs (or --scope all): add to change list.
     - Default behaviour: REPORT ONLY. Auto-fix requires explicit
       --fix-counts because a numeric claim in prose may be
       intentionally historical (e.g. "was 1732 at launch").
     - Prose drift (wording, not numbers) is NEVER auto-fixed – it
       requires human judgment.

   Scope keeper: only NUMERIC claims adjacent to the listed keywords
   are flagged. English prose drift stays out of this check.

i) CR status drift (if sdlc-studio/change-requests/ exists):
   For each CR file:
     - Compare file status vs index entry status → mismatch?
   For each CR with status "In Progress":
     - Find linked epics from "Linked Epics" section
     - Look up each epic's actual status from truth map
     - If ALL linked epics Done but CR still In Progress:
       add to change list as SUGGESTED FIX (never auto-apply -- requires user confirmation)
   Recalculate CR index summary counts from truth map:
     - Compare against _index.md Summary table → drift?

j) AC verification drift (when --verify or --scope verify):
   Delegate to scripts/verify_ac.py run for each story file in scope.
   The runner:
     - Parses - **Verify:** bullets under each AC
     - Runs the verifier expression via its DSL (pytest, jest, file,
       grep, http, shell, ...)
     - Passing + Verified missing or no/stale: upgrade to yes
     - Failing + Verified yes: downgrade to no (source of truth drift)
     - Missing Verify: manual, reconcile does not touch
   Writes sdlc-studio/.local/verify-report.json and returns non-zero
   exit if any AC failed. The dry-run flag propagates to verify_ac.py.
   Full DSL, report shape, and gated completion in reference-verify.md.
```

### 4. Phase 3: Report or Apply

#### Dry-run mode (`--dry-run`)

Print the change list as a structured report:

```text
══════════════════════════════════════════════════════════
                    RECONCILE (dry run)
══════════════════════════════════════════════════════════

📋 DRIFT DETECTED: {N} fixes needed

  {file path}
  ├─ {description of fix}
  └─ {description of fix}

  ...

  ▶️ Run without --dry-run to apply all {N} fixes.
══════════════════════════════════════════════════════════
```

#### Apply mode (default)

> **Deterministic apply.** The two index-level mechanical fixes are
> now done by the script: `reconcile apply [--scope] [--dry-run]` rewrites each
> drifted index row's Status cell (positionally, by the table header) to the file's
> status and recomputes the summary counts. It is **idempotent** (a second run
> writes nothing) and `--dry-run` reports without writing. Structural classes
> (missing-row / orphan-row / missing-index) and the judgement calls below
> (CR-completion, PRD prose, breakdown/AC checkboxes) remain Claude-orchestrated.

Apply all mechanical fixes in dependency order:

```text
1. Stories first: update stories/_index.md entries and counts
2. Epics next: update epics/_index.md entries and counts
3. Epic files: tick story breakdown checkboxes, AC checkboxes, dependency tables
3b. Story files: update dependency table statuses
4. PRD: update feature statuses and AC checkboxes
5. Plans/test-specs: update index entries and counts
```

After applying:

```text
6. For each modified file:
   a) Update **Last Updated:** date to today
   b) Add changelog/revision entry: "| {date} | Claude | Reconcile: {summary} |"

7. Print summary:
   ══════════════════════════════════════════════════════════
                       RECONCILE COMPLETE
   ══════════════════════════════════════════════════════════

     {N} fixes applied across {M} files
     ├─ {X} index entries updated
     ├─ {Y} summary counts recalculated
     ├─ {Z} dependency table references corrected
     ├─ {W} checkboxes ticked
     ├─ {V} PRD feature statuses updated
     └─ {U} Last Updated dates refreshed

     Zero drift remaining.
   ══════════════════════════════════════════════════════════
```

### 5. Scope Filtering {#verify-scope}

When `--scope` is specified, only run the relevant subset of Phase 2 and Phase 3:

| Scope | Phase 2 checks | Phase 3 fixes |
| --- | --- | --- |
| `stories` | Story index drift + story dependency table drift | stories/_index.md + story files |
| `epics` | Epic index + dependency + checkbox drift | epics/_index.md + epic files |
| `prd` | PRD feature status + AC drift | prd.md |
| `crs` | CR index drift + CR status cascade (report-only for completion) | change-requests/_index.md |
| `verify` | Run AC verifiers via scripts/verify_ac.py | story Verified: lines + verify-report.json |
| `docs` | Numeric-claim drift in prose docs (AGENTS.md / CLAUDE.md / README.md / docs/**) | REPORT ONLY unless `--fix-counts` |
| `indexes` | All index drift (no file-level fixes) | All _index.md files |
| (none) | All checks | All fixes |

---

## Principles

1. **File is truth, index is derived.** If a story file says Done but the index says Draft, the index is wrong.
2. **Done is never auto-assigned.** Reconcile propagates existing Done statuses to indexes, dependency tables, and PRD. It never changes a story or epic status TO Done.
3. **Mechanical only.** Reconcile fixes bookkeeping (counts, checkboxes, cross-references). It does not evaluate content accuracy, test coverage, or architecture alignment.
4. **Idempotent.** Running reconcile twice produces the same result. Zero drift after first run means zero changes on second run.

---

## Cadence Triggers {#cadence-triggers}

Drift is silent – by the time it shows up in a status dashboard or a review, it has usually accumulated through several un-reconciled events. These events are the **natural cadence triggers** that should prompt a reconcile pass:

| Trigger | Why |
| --- | --- |
| **Epic close** (`Status → Done`) | The epic-close moment is when story / dependency / index drift accumulates fastest. Always reconcile after closing an epic. |
| **Ship event** (tagged release / merge to main / deploy) | A ship is the highest-stakes drift moment – code on disk has just diverged from spec on disk. Reconcile after every ship. |
| **CR `action`** (CR → Epic+Stories generation) | CR action creates new epics and stories; the index update on the CR side and the epic / story side can fall out of sync. Reconcile after CR action. |
| **More than 7 days since last reconcile** | If no other trigger fired but the calendar has rolled forward, drift has compounded silently. Recommend reconcile. |

`/sdlc-studio status` reads `.local/reconcile-state.json` to detect when one of these triggers fired and emits a **"Reconcile recommended because…"** line. The line is advisory; the operator decides when to act. Reconcile itself is cheap – running it more often than needed is harmless. The cost of skipping a recommended reconcile is silent drift that surfaces later as a review finding or, worse, an inconsistent ship.

`reconcile-state.json` schema:

```json
{
  "last_reconcile": "2026-04-30T14:32:11Z",
  "last_epic_close": { "epic": "EP0042", "at": "2026-04-30T11:18:00Z" },
  "last_ship": { "tag": "v3.55.3", "at": "2026-04-30T16:05:41Z" },
  "last_cr_action": { "cr": "CR-0130", "at": "2026-04-30T08:14:00Z" }
}
```

After every reconcile, `last_reconcile` is updated. Triggers older than `last_reconcile` are cleared from the recommendation. Triggers newer than `last_reconcile` accumulate; the recommendation lists all of them.

---

## See Also

- `help/reconcile.md` -- Quick reference and examples
- `reference-outputs.md` → Story Completion Cascade, Epic Completion Cascade
- `reference-review.md` → Unified review with auto-fix
