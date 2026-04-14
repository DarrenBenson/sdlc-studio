# SDLC Studio Reference - Reconcile

Detailed workflow for the reconcile command that detects and fixes status drift across all artifacts.

<!-- Load when: running /sdlc-studio reconcile -->

---

## /sdlc-studio reconcile - Step by Step {#reconcile-workflow}

### 1. Parse Arguments

| Flag | Effect | Default |
| --- | --- | --- |
| `--dry-run` | Preview changes, don't apply | false |
| `--scope` | Limit to: `epics`, `stories`, `prd`, `indexes` | all |

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
```

### 3. Phase 2: Detect Drift

Compare ground truth against indexes and cross-references. Collect all discrepancies into a change list.

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

h) CR status drift (if sdlc-studio/change-requests/ exists):
   For each CR file:
     - Compare file status vs index entry status → mismatch?
   For each CR with status "In Progress":
     - Find linked epics from "Linked Epics" section
     - Look up each epic's actual status from truth map
     - If ALL linked epics Done but CR still In Progress:
       add to change list as SUGGESTED FIX (never auto-apply -- requires user confirmation)
   Recalculate CR index summary counts from truth map:
     - Compare against _index.md Summary table → drift?
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

### 5. Scope Filtering

When `--scope` is specified, only run the relevant subset of Phase 2 and Phase 3:

| Scope | Phase 2 checks | Phase 3 fixes |
| --- | --- | --- |
| `stories` | Story index drift + story dependency table drift | stories/_index.md + story files |
| `epics` | Epic index + dependency + checkbox drift | epics/_index.md + epic files |
| `prd` | PRD feature status + AC drift | prd.md |
| `crs` | CR index drift + CR status cascade (report-only for completion) | change-requests/_index.md |
| `indexes` | All index drift (no file-level fixes) | All _index.md files |
| (none) | All checks | All fixes |

---

## Principles

1. **File is truth, index is derived.** If a story file says Done but the index says Draft, the index is wrong.
2. **Done is never auto-assigned.** Reconcile propagates existing Done statuses to indexes, dependency tables, and PRD. It never changes a story or epic status TO Done.
3. **Mechanical only.** Reconcile fixes bookkeeping (counts, checkboxes, cross-references). It does not evaluate content accuracy, test coverage, or architecture alignment.
4. **Idempotent.** Running reconcile twice produces the same result. Zero drift after first run means zero changes on second run.

---

## See Also

- `help/reconcile.md` -- Quick reference and examples
- `reference-outputs.md` → Story Completion Cascade, Epic Completion Cascade
- `reference-review.md` → Unified review with auto-fix
