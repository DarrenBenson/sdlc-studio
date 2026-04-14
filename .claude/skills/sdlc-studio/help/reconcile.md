<!--
Load: On /sdlc-studio reconcile or /sdlc-studio reconcile help
Dependencies: SKILL.md (always loaded first)
Related: reference-reconcile.md (deep workflow), reference-outputs.md (cascade checklists)
-->

# /sdlc-studio reconcile - Status Reconciliation

## Quick Reference

```text
/sdlc-studio reconcile                   # Detect and fix all status drift
/sdlc-studio reconcile --dry-run         # Preview fixes without applying
/sdlc-studio reconcile --scope epics     # Reconcile epics only
/sdlc-studio reconcile --scope stories   # Reconcile stories only
/sdlc-studio reconcile --scope prd       # Reconcile PRD only
```

## Prerequisites

- At least one artifact type must exist (stories, epics, or PRD)
- Run after implementation sessions, interrupted workflows, or manual status changes

## What It Does

Three-phase workflow: **collect ground truth** from artifact files, **detect drift** by comparing against indexes and cross-references, **apply fixes** for all mechanical discrepancies.

### What It Fixes (mechanical bookkeeping)

| Artifact | Fixes Applied |
| --- | --- |
| `stories/_index.md` | Status entries matching story file statuses, summary counts |
| `epics/_index.md` | Status entries matching epic file statuses, summary counts |
| Epic dependency tables | Referenced epic statuses updated to match actual status |
| Epic AC checkboxes | Ticked for criteria verified against the codebase |
| Epic story breakdown | Checkboxes matching story file statuses |
| PRD feature statuses | Updated to match epic completion (Complete, Partial, Not Started) |
| PRD feature AC checkboxes | Ticked for criteria matching verified implementation |
| `plans/_index.md` | Status entries matching plan file statuses, summary counts |
| `test-specs/_index.md` | Status entries matching test-spec file statuses, summary counts |
| Metadata dates | `**Last Updated:**` on modified files set to today |
| Changelogs | Revision history entry added to modified files |

### What It Does NOT Fix (requires judgment)

- Content accuracy (stale descriptions, outdated architecture claims)
- Spec-to-code naming drift (e.g. interface names in TRD vs code)
- TSD test tree vs actual test files (use `tsd review` for this)
- Status transitions to Done (always a user decision -- reconcile only propagates existing Done statuses)
- Test coverage gaps

## Arguments

| Flag | Effect | Default |
| --- | --- | --- |
| `--dry-run` | Preview all changes without applying | false |
| `--scope epics` | Only reconcile epic-related artifacts | all |
| `--scope stories` | Only reconcile story-related artifacts | all |
| `--scope prd` | Only reconcile PRD feature statuses | all |
| `--scope crs` | Only reconcile change request index drift (report-only for completion cascade) | all |
| `--scope indexes` | Only reconcile index files and counts | all |

## Output

### Dry-run mode

```text
══════════════════════════════════════════════════════════
                    RECONCILE (dry run)
══════════════════════════════════════════════════════════

📋 DRIFT DETECTED: 12 fixes needed

  stories/_index.md
  ├─ US0001: Draft → Done (matches story file)
  ├─ US0002: Draft → Done (matches story file)
  └─ Summary: Draft 44→29, Done 13→28

  epics/_index.md
  └─ EP0004: Draft → Done (matches epic file)

  EP0006 dependency table
  └─ EP0003: Draft → Done

  prd.md
  ├─ Config File Loader: Not Started → Complete
  └─ [x] Config loads from ~/.agent-bridge/config.json

  ▶️ Run without --dry-run to apply all 12 fixes.
══════════════════════════════════════════════════════════
```

### Apply mode

```text
══════════════════════════════════════════════════════════
                    RECONCILE COMPLETE
══════════════════════════════════════════════════════════

  12 fixes applied across 8 files
  ├─ 15 index entries updated
  ├─ 4 summary counts recalculated
  ├─ 6 dependency table references corrected
  ├─ 23 checkboxes ticked
  ├─ 3 PRD feature statuses updated
  └─ 8 Last Updated dates refreshed

  Zero drift remaining.
══════════════════════════════════════════════════════════
```

## Examples

```bash
# After completing several stories manually across sessions
/sdlc-studio reconcile

# Preview what would change before applying
/sdlc-studio reconcile --dry-run

# Only fix PRD feature statuses after epic completion
/sdlc-studio reconcile --scope prd

# Only fix index files and summary counts
/sdlc-studio reconcile --scope indexes
```

## When to Use

- After implementation sessions that didn't use `story implement` or `epic implement` workflows
- After interrupted workflows (crash, timeout, context limit)
- After manual status changes to story or epic files
- Before a milestone review to ensure all artifacts are consistent
- As a safety net after any session where you suspect drift

## See Also

**REQUIRED for this workflow:**

- `reference-reconcile.md` -- Step-by-step reconcile procedure

**Related:**

- `reference-outputs.md` → Story Completion Cascade, Epic Completion Cascade
- `/sdlc-studio status --full` -- Detects drift but doesn't fix it
- `/sdlc-studio review` -- Reviews documents with auto-fix for mechanical issues
