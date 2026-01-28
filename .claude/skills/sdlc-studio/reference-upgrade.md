# SDLC Studio Upgrade Reference

Workflows for upgrading projects between schema versions and detecting version mismatches.

## Schema Versions

| Version | Format | Key Characteristics |
|---------|--------|---------------------|
| 1 | Legacy | Verbose templates, embedded validation, copied constraints |
| 2 | Modular | Core + modules, progressive disclosure, reference-based constraints |

---

## Version Check (hint and status only)

Version checks run on `/sdlc-studio hint` and `/sdlc-studio status` commands only. See `help/hint.md` and `help/status.md` for the pre-flight workflow.

### Dismissal File

Location: `sdlc-studio/.local/upgrade-dismissed.json`

```json
{
  "dismissed": true,
  "dismissed_at": "2026-01-27T10:30:00Z",
  "schema_version_at_dismissal": 1
}
```

Create the `.local/` directory if it doesn't exist.

---

## Version Detection

### On Any Command

```text
1. Check for sdlc-studio/.version
2. If missing → assume v1 (legacy)
3. Read schema_version from file
4. If schema_version < current skill version:
   - Display upgrade suggestion
   - Continue with command (don't block)
```

### Upgrade Suggestion Output

```text
⚠️ Project uses schema v1 (current: v2)
   Consider upgrading: /sdlc-studio upgrade --dry-run
```

---

## /sdlc-studio upgrade - Step by Step {#upgrade-workflow}

### 1. Parse Arguments

| Flag | Effect |
|------|--------|
| (none) | Interactive upgrade with confirmation |
| `--dry-run` | Preview changes without applying |
| `--force` | Upgrade without confirmation |

### 2. Detect Current Version

```text
a) Read sdlc-studio/.version
   - If exists: use schema_version
   - If missing: assume v1

b) Compare to skill's current schema version
   - If already current: "Project is already at latest version"
   - If newer: "Project was created with newer skill version"
```

### 3. Inventory Existing Artifacts

```text
Scan sdlc-studio/ for all artifacts:
- prd.md, trd.md, tsd.md, personas.md
- epics/EP*.md
- stories/US*.md
- plans/PL*.md
- bugs/BG*.md
- test-specs/TS*.md
- reviews/RV*.md

Record for each:
- ID (from filename or frontmatter)
- Filename
- Content hash (for change detection)
```

### 4. Transform Each Artifact

For each artifact type, apply version-specific transformations:

#### PRD (v1 → v2)

| Section | Action |
|---------|--------|
| Appendix A (File Tree) | Remove (generate on demand) |
| Appendix B (Dependencies) | Remove (generate on demand) |
| Appendix C (Env Reference) | Merge into §9 Configuration |
| Appendix D (API Catalogue) | Move to TRD or remove |
| Appendix E (Changelog) | Keep at end |
| Confidence/Status Legends | Remove (→ reference-outputs.md) |

#### TRD (v1 → v2)

| Section | Action |
|---------|--------|
| §2.5 C4 Diagrams | Keep if populated, else reference module |
| §9.5 Architecture Checklist | Remove (→ reference-trd.md) |
| §9.6 Container Design | Keep if populated, else reference module |

#### TSD (v1 → v2)

| Section | Action |
|---------|--------|
| Multi-language code examples | Remove inline, add reference link |
| Test Anti-Patterns details | Remove inline (→ reference-test-best-practices.md) |
| Coverage rationale paragraph | Shorten, add reference link |

#### Epic (v1 → v2)

| Section | Action |
|---------|--------|
| Inherited Constraints table | Simplify to key items only |
| Perspective Views | Keep only if populated |
| Test Plan table | Simplify to single Test Spec reference |

#### Story (v1 → v2)

| Section | Action |
|---------|--------|
| Quality Checklist | Remove (→ reference-story.md) |
| Ready Status Gate | Remove (→ reference-decisions.md) |
| Inherited Constraints | Simplify to key items |
| Test Cases table | Keep only if has entries |
| Feature File reference | Keep only if exists |

#### Index Files (v1 → v2)

| Section | Action |
|---------|--------|
| "By Status" sections | Remove (redundant with main table) |
| Dependency Graph | Remove (complex to maintain) |
| Estimation Summary | Remove from story index |

### 5. Preserve During Transform

**Always preserved:**
- Artifact ID (EP0001, US0001, etc.)
- Title
- Status
- Relationships (Epic → Story, Story → Plan)
- User-written content (descriptions, AC, notes)
- Revision History

**Never lose data:**
- Content from removed sections goes to archive if valuable
- Links are updated to new locations
- No orphaned references

### 6. Update Index Files

```text
a) Regenerate each index in new format
b) Preserve all artifact references
c) Remove deprecated sections (By Status, etc.)
d) Update file paths if templates moved
```

### 7. Write Version File

Create or update `sdlc-studio/.version`:

```yaml
schema_version: 2
upgraded_from: 1
upgraded_at: 2026-01-27T10:30:00Z
skill_version: "1.3.0"
created_at: <preserved or now>
```

### 8. Generate Report

```text
══════════════════════════════════════════════════════════
                    UPGRADE COMPLETE
══════════════════════════════════════════════════════════

📋 ARTIFACTS UPGRADED
   PRD: 14 sections → 11 sections
   TRD: 454 lines → 270 lines
   TSD: 424 lines → 250 lines
   Epics: 3 files updated
   Stories: 12 files updated
   Indexes: 6 files regenerated

🗑️ SECTIONS REMOVED (content preserved in reference docs)
   - PRD Appendices A-D
   - Story Quality Checklists
   - Inline code examples

📝 MANUAL REVIEW NEEDED
   - EP0001: Perspective view has user content
   - US0003: Custom Quality Checklist items

📁 VERSION FILE
   Created: sdlc-studio/.version
   Schema: 1 → 2

▶️ NEXT: Review changed files, then /sdlc-studio status
══════════════════════════════════════════════════════════
```

---

## Dry Run Output

When `--dry-run` is specified:

```text
══════════════════════════════════════════════════════════
                  UPGRADE PREVIEW (DRY RUN)
══════════════════════════════════════════════════════════

📋 ARTIFACTS TO UPGRADE
   PRD: sdlc-studio/prd.md (14 → 11 sections)
   TRD: sdlc-studio/trd.md (454 → 270 lines)
   TSD: sdlc-studio/tsd.md (424 → 250 lines)
   Epics: 3 files
   Stories: 12 files
   Indexes: 6 files

🗑️ SECTIONS TO REMOVE
   - PRD Appendices A-D (generate on demand)
   - Story Quality Checklists (→ reference-story.md)
   - TRD Architecture Checklist (→ reference-trd.md)

⚠️ ITEMS NEEDING REVIEW
   - EP0001: Has custom Perspective View content
   - US0003: Has custom Quality Checklist items

▶️ Run without --dry-run to apply changes
══════════════════════════════════════════════════════════
```

---

## Backward Compatibility

### v2 Skill Reading v1 Artifacts

The v2 skill can read v1 artifacts without upgrade:

1. Detect missing `.version` file → assume v1
2. Apply v1 parsing rules
3. Ignore v2-only sections if missing
4. Suggest upgrade on first command

### Upgrade Is Optional

- Upgrade is recommended but not required
- All v1 functionality continues to work
- New v2 features require upgrade
- No functionality loss, only verbosity reduction

---

## Configuration Upgrade

When upgrading, also check for new config options:

1. Load existing `sdlc-studio/.config.yaml` if present
2. Compare against current `config-defaults.yaml`
3. Report new options available
4. Do not auto-add (user must opt-in)

---

## Rollback

No automatic rollback is provided. To revert:

1. Use git to revert changed files
2. Delete `.version` file to return to v1 detection
3. Old templates continue to work

---

## See Also

- `reference-config.md` - Configuration options
- `help/upgrade.md` - Command quick reference
- `templates/version.yaml` - Version file template
