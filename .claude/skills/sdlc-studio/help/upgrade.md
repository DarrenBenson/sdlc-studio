<!--
Load: On /sdlc-studio upgrade or upgrade help
Dependencies: SKILL.md (always loaded first)
Related: reference-upgrade.md
-->

# /sdlc-studio upgrade - Schema Upgrade

Upgrade project artifacts from legacy (v1) to modular (v2) schema.

## Quick Reference

```bash
/sdlc-studio upgrade                   # Interactive upgrade
/sdlc-studio upgrade --dry-run         # Preview changes
/sdlc-studio upgrade --force           # Upgrade without confirmation
```

## What It Does

1. **Detects version** from `sdlc-studio/.version` (or assumes v1 if missing)
2. **Transforms artifacts** to streamlined format
3. **Removes redundant sections** (moves to reference docs)
4. **Updates indexes** to simplified format
5. **Creates version file** to track schema version

## Flags

| Flag | Description |
|------|-------------|
| `--dry-run` | Show what would change without applying |
| `--force` | Skip confirmation prompt |

## Schema Changes (v1 → v2)

| Artifact | Changes |
|----------|---------|
| PRD | Appendices A-E removed (generate on demand) |
| TRD | ~40% smaller, C4/containers become optional modules |
| TSD | Code examples removed (reference links added) |
| Epic | Perspective views optional, constraints simplified |
| Story | Quality Checklist removed (reference link added) |
| Indexes | "By Status" sections removed (single table only) |

## What's Preserved

- All artifact IDs (EP0001, US0001, etc.)
- All user-written content
- Status values
- Relationships between artifacts
- Revision history

## Example Output

```text
══════════════════════════════════════════════════════════
                    UPGRADE COMPLETE
══════════════════════════════════════════════════════════

📋 ARTIFACTS UPGRADED
   PRD: 14 sections → 11 sections
   Stories: 12 files updated

📝 MANUAL REVIEW NEEDED
   - US0003: Custom Quality Checklist items

📁 VERSION FILE
   Created: sdlc-studio/.version
   Schema: 1 → 2

▶️ NEXT: Review changed files, then /sdlc-studio status
══════════════════════════════════════════════════════════
```

## Version Detection

On any `/sdlc-studio` command, version is detected:

```text
⚠️ Project uses schema v1 (current: v2)
   Consider upgrading: /sdlc-studio upgrade --dry-run
```

Upgrade is suggested but never blocks commands.

## Rollback

To revert an upgrade:

```bash
git checkout -- sdlc-studio/   # Revert file changes
rm sdlc-studio/.version        # Remove version tracking
```

## Prerequisites

- Git repository recommended (for rollback)
- No active work in progress (commit first)

## See Also

- `reference-upgrade.md` - Detailed transformation rules
- `reference-config.md` - Configuration options
- `/sdlc-studio init` - Initialise new project
