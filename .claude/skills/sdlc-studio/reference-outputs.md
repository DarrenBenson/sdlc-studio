# SDLC Studio Output Reference

Single source of truth for all output formats, file locations, status values, and transitions.

## Output Formats {#output-formats}

| Type | Location | Naming | Status Values |
|------|----------|--------|---------------|
| PRD | `sdlc-studio/prd.md` | Fixed | Feature status markers |
| TRD | `sdlc-studio/trd.md` | Fixed | Draft/Approved |
| Persona | `sdlc-studio/personas.md` | Fixed | - |
| TSD | `sdlc-studio/tsd.md` | Fixed | - |
| Epic | `sdlc-studio/epics/EP{NNNN}-*.md` | EP0001, EP0002, EP0003... | Draft/Ready/Approved/In Progress/Done |
| Story | `sdlc-studio/stories/US{NNNN}-*.md` | US0001, US0002, US0003... | Draft/Ready/Planned/In Progress/Review/Done |
| Plan | `sdlc-studio/plans/PL{NNNN}-*.md` | PL0001, PL0002, PL0003... | Draft/In Progress/Complete |
| Bug | `sdlc-studio/bugs/BG{NNNN}-*.md` | BG0001, BG0002, BG0003... | Open/In Progress/Fixed/Verified/Closed/Won't Fix |
| Test Spec | `sdlc-studio/test-specs/TS{NNNN}-*.md` | TS0001, TS0002, TS0003... | Draft/Ready/In Progress/Complete |
| Workflow | `sdlc-studio/workflows/WF{NNNN}-*.md` | WF0001, WF0002, WF0003... | Created/Planning/Testing/Implementing/Verifying/Reviewing/Checking/Done/Paused |
| Test Code | `tests/` | Framework-dependent | - |

## Status Transitions {#status-transitions}

### Epic Status Flow {#epic-status-flow}

```text

Draft → Ready → Approved → In Progress → Done
  ↑                           ↓
  └──────── (revision) ───────┘
```

**Transition criteria:**

- **Draft → Ready:** All User Stories created and Ready
- **Ready → Approved:** Stakeholder review complete
- **Approved → In Progress:** First Story moves to In Progress
- **In Progress → Done:** All Stories Done
- **Any → Draft:** Requirements change (revision)

### Story Status Flow {#story-status-flow}

```text

Draft → Ready → Planned → In Progress → Review → Done
  ↑                          ↓
  └────── (revision) ────────┘
```

**Transition criteria:**

- **Draft → Ready:** Acceptance criteria complete, edge cases identified, dependencies resolved
- **Ready → Planned:** Implementation plan created and approved
- **Planned → In Progress:** Development started
- **In Progress → Review:** Code complete, tests passing
- **Review → Done:** Code verified against acceptance criteria, quality checks passed
- **Any → Draft:** Requirements change (revision)

### Plan Status Flow {#plan-status-flow}

```text

Draft → In Progress → Complete
```

**Transition criteria:**

- **Draft → In Progress:** Implementation started
- **In Progress → Complete:** All phases implemented, tests passing

### Bug Status Flow {#bug-status-flow}

```text

Open → In Progress → Fixed → Verified → Closed
  ↓                                      ↑
  └───────────── Won't Fix ─────────────┘
```

**Transition criteria:**

- **Open → In Progress:** Developer assigned, fix started
- **In Progress → Fixed:** Fix complete, awaiting verification
- **Fixed → Verified:** Tests confirm bug resolved
- **Verified → Closed:** Verification accepted
- **Open → Won't Fix:** Decision not to fix (document reason)

### Test Spec Status Flow {#test-spec-status-flow}

```text

Draft → Ready → In Progress → Complete
```

**Transition criteria:**

- **Draft → Ready:** All test cases defined, fixtures identified
- **Ready → In Progress:** Test automation started
- **In Progress → Complete:** All tests automated and passing

### Workflow Status Flow {#workflow-status-flow}

```text

Created → Planning → Testing → Implementing → Verifying → Reviewing → Checking → Done
   ↓                                                                               ↑
   └──────────────────────────── Paused ────────────────────────────────────────┘
```

**Transition criteria:**

- **Created → Planning:** Code plan phase started
- **Planning → Testing:** Test spec phase started
- **Testing → Implementing:** Test automation/implementation phase started
- **Implementing → Verifying:** Code test phase started
- **Verifying → Reviewing:** Code verify phase started
- **Reviewing → Checking:** Code check phase started
- **Checking → Done:** All phases complete
- **Any → Paused:** Workflow suspended (user request or blocker)

## File Naming Conventions {#file-naming}

### ID Formats {#id-formats}

Each numbered artifact type uses a 4-digit zero-padded ID:

| Type | Format | Example |
|------|--------|---------|
| Epic | `EP{NNNN}` | EP0001, EP0024, EP0100 |
| Story | `US{NNNN}` | US0001, US0042, US0500 |
| Plan | `PL{NNNN}` | PL0001, PL0015, PL0200 |
| Bug | `BG{NNNN}` | BG0001, BG0007, BG0050 |
| Test Spec | `TS{NNNN}` | TS0001, TS0018, TS0300 |
| Workflow | `WF{NNNN}` | WF0001, WF0009, WF0150 |

### Filename Patterns {#filename-patterns}

IDs are followed by a slug derived from the title:

```text

{TYPE}{NNNN}-{slug-from-title}.md
```

**Examples:**

- `EP0001-user-authentication.md`
- `US0042-login-form-validation.md`
- `PL0015-implement-oauth-flow.md`
- `BG0007-session-timeout-error.md`
- `TS0018-auth-integration-tests.md`
- `WF0009-story-us0042.md`

**Slug rules:**

- Lowercase
- Hyphens separate words
- No special characters
- Max 50 characters
- Derived from title, not manually set

## Index Files {#index-files}

Each numbered type maintains an `_index.md` registry file in its directory.

### Index File Location {#index-location}

| Type | Index Location |
|------|----------------|
| Epic | `sdlc-studio/epics/_index.md` |
| Story | `sdlc-studio/stories/_index.md` |
| Plan | `sdlc-studio/plans/_index.md` |
| Bug | `sdlc-studio/bugs/_index.md` |
| Test Spec | `sdlc-studio/test-specs/_index.md` |
| Workflow | `sdlc-studio/workflows/_index.md` |

### Index File Structure {#index-structure}

Index files track all artifacts with basic metadata:

```markdown
# {Type} Index

| ID | Title | Status | Epic | Story | Created | Updated |
|----|-------|--------|------|-------|---------|---------|
| {TYPE}0001 | Title | Status | EP0001 | US0001 | 2025-01-15 | 2025-01-20 |
```

**Field descriptions:**

- **ID:** Artifact identifier
- **Title:** Brief description
- **Status:** Current status (see Status Transitions)
- **Epic:** Related Epic (for Stories, Plans, Bugs, Test Specs, Workflows)
- **Story:** Related Story (for Plans, Bugs, Test Specs, Workflows)
- **Created:** ISO date when artifact created
- **Updated:** ISO date when last modified

### Index File Maintenance {#index-maintenance}

**When to update:**

- New artifact created → Add row
- Status changes → Update Status column
- Title changes → Update Title column
- Any file update → Update Updated column

**Sorting:**

- Always sort by ID ascending
- IDs never change once assigned
- No gaps in sequence (auto-increment from highest)

## Frontmatter Standards {#frontmatter}

All artifacts use YAML frontmatter for metadata:

```yaml
---
id: {TYPE}{NNNN}
title: Brief title
status: {Status Value}
epic: EP0001          # For Stories, Plans, Bugs, Test Specs, Workflows
story: US0001         # For Plans, Bugs, Test Specs, Workflows
created: 2025-01-15
updated: 2025-01-20
---
```

## Traceability {#traceability}

Artifacts link hierarchically for full traceability:

```text

PRD
 ├─ Epic (EP0001)
 │   ├─ Story (US0001)
 │   │   ├─ Plan (PL0001)
 │   │   ├─ Test Spec (TS0001)
 │   │   ├─ Workflow (WF0001)
 │   │   └─ Bug (BG0001)
 │   └─ Story (US0002)
 │       ├─ Plan (PL0002)
 │       └─ Test Spec (TS0002)
 └─ Epic (EP0002)
     └─ Story (US0003)
         └─ Plan (PL0003)

TRD
 └─ [Links to Epics as needed for technical constraints]
```

**Link fields in frontmatter:**

- **Epic:** Required in Story, Plan, Bug, Test Spec, Workflow
- **Story:** Required in Plan, Bug, Test Spec, Workflow
- **Plan:** Referenced in Workflow
- **Test Spec:** Referenced in Workflow

## Review State Files {#review-state}

Review tracking uses JSON files for state management. These are runtime files, not templates.

### review-state.json {#review-state-json}

**Location:** `sdlc-studio/.local/review-state.json`

Tracks when each artifact was last reviewed and modified.

```json
{
  "version": 1,
  "artifacts": {
    "EP0001": {
      "type": "epic",
      "path": "sdlc-studio/epics/EP0001-user-auth.md",
      "last_reviewed": "2026-01-20T10:30:00Z",
      "last_modified": "2026-01-22T14:00:00Z",
      "review_findings_ref": "RV0001"
    },
    "US0001": {
      "type": "story",
      "path": "sdlc-studio/stories/US0001-login-form.md",
      "last_reviewed": "2026-01-21T09:00:00Z",
      "last_modified": "2026-01-21T09:00:00Z",
      "code_files": ["src/auth/login.ts"],
      "code_last_modified": "2026-01-23T16:00:00Z"
    }
  },
  "reviews": {
    "RV0001": {
      "artifact": "EP0001",
      "timestamp": "2026-01-20T10:30:00Z",
      "findings_file": "sdlc-studio/reviews/RV0001-EP0001-review.md",
      "summary": { "critical": 0, "important": 2, "suggestions": 5 }
    }
  }
}
```

**Field descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `version` | number | Schema version (currently 1) |
| `artifacts.{id}.type` | string | Artifact type (epic, story) |
| `artifacts.{id}.path` | string | Path to artifact file |
| `artifacts.{id}.last_reviewed` | ISO date | When last reviewed |
| `artifacts.{id}.last_modified` | ISO date | When artifact last modified |
| `artifacts.{id}.review_findings_ref` | string | Reference to RV file |
| `artifacts.{id}.code_files` | array | Code files implementing this artifact (stories only) |
| `artifacts.{id}.code_last_modified` | ISO date | Most recent code file modification |
| `reviews.{id}.artifact` | string | Artifact this review covers |
| `reviews.{id}.timestamp` | ISO date | When review was conducted |
| `reviews.{id}.findings_file` | string | Path to findings document |
| `reviews.{id}.summary` | object | Issue counts by severity |

### review-queue.json {#review-queue-json}

**Location:** `sdlc-studio/.local/review-queue.json`

Enables pause/resume for cascading reviews.

```json
{
  "id": "RQ0001",
  "epic": "EP0001",
  "created": "2026-01-27T10:00:00Z",
  "status": "in_progress",
  "queue": [
    { "type": "story_spec", "id": "US0001", "status": "done" },
    { "type": "story_code", "id": "US0001", "status": "in_progress" },
    { "type": "story_spec", "id": "US0002", "status": "pending" }
  ],
  "current_index": 1
}
```

**Field descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Queue identifier (RQ{NNNN}) |
| `epic` | string | Epic being reviewed |
| `created` | ISO date | When queue was created |
| `status` | string | pending, in_progress, done, paused |
| `queue[].type` | string | story_spec, story_code, epic |
| `queue[].id` | string | Artifact ID |
| `queue[].status` | string | pending, in_progress, done, skipped |
| `current_index` | number | Current position in queue |

### Modified-Since Detection {#modified-since-detection}

The review system detects when artifacts need re-review:

```text
needs_re_review(artifact):
  1. Load entry from review-state.json
  2. If no entry OR no last_reviewed: return TRUE
  3. Get last_modified via git log or file mtime
  4. If last_modified > last_reviewed: return TRUE
  5. return FALSE

code_changed_since_review(story):
  1. Get code_files list from story entry
  2. For each file: check git log timestamp
  3. If any file_modified > story.last_reviewed: return TRUE
  4. return FALSE
```

### Backward Compatibility {#review-backward-compatibility}

- Projects without `review-state.json`: all items marked "needs review"
- Review system is advisory only - never blocks any workflow
- Existing artifacts work without review history

## Local State Files {#local-state}

The `.local/` directory contains user-specific runtime state that should NOT be committed:

| File | Purpose | Why User-Local |
|------|---------|----------------|
| `review-state.json` | Review timestamps | Each developer's review history differs |
| `review-queue.json` | Pause/resume state | One user's paused review shouldn't affect others |
| `status-cache.json` | Cached lint/coverage | Machine-specific results |
| `upgrade-dismissed.json` | Upgrade prompt preference | User's choice to suppress upgrade prompts |

**Gitignore:** Add to your project's `.gitignore`:
```gitignore
# SDLC Studio user-local state
sdlc-studio/.local/
```

### upgrade-dismissed.json {#upgrade-dismissed-json}

**Location:** `sdlc-studio/.local/upgrade-dismissed.json`

Records user's preference to not be prompted about schema upgrades.

```json
{
  "dismissed_at": "2026-01-27T10:30:00Z",
  "schema_version_at_dismissal": 1,
  "reason": "user_choice"
}
```

**Field descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `dismissed_at` | ISO date | When user chose "don't ask again" |
| `schema_version_at_dismissal` | number | Schema version when dismissed (1 = legacy) |
| `reason` | string | Why dismissed: `user_choice` |

**Behaviour:**

- Created when user selects "No, don't ask again" on upgrade prompt
- If file exists, `/sdlc-studio status` and `/sdlc-studio hint` skip upgrade prompt
- Deleting this file re-enables upgrade prompts
- File is user-local (not committed to repo)

## Review Findings {#review-findings}

| Type | Location | Naming | Status Values |
|------|----------|--------|---------------|
| Review | `sdlc-studio/reviews/RV{NNNN}-*.md` | RV0001, RV0002... | N/A (immutable) |

Review findings are immutable records - once created, they are not modified. New reviews create new RV files.

---

## Validation Checklists {#validation-checklists}

Validation criteria extracted from templates for reference. Templates link here rather than embedding checklists.

### Story Ready Checklist {#story-ready-checklist}

A story can be marked **Ready** when:
- [ ] All critical Open Questions resolved
- [ ] Minimum edge case count met (API: {{config.story_quality.edge_cases.api}}, other: {{config.story_quality.edge_cases.other}})
- [ ] No "TBD" placeholders in acceptance criteria
- [ ] Error scenarios documented (not just happy path)
- [ ] Inherited constraints addressed in AC, Edge Cases, or Technical Notes

### Story Quality Checklist {#story-quality-checklist}

**API Stories (minimum requirements):**
- [ ] Edge cases: {{config.story_quality.edge_cases.api}} minimum documented
- [ ] Test scenarios: {{config.story_quality.test_scenarios.api}} minimum listed
- [ ] API contracts: Exact request/response JSON shapes documented
- [ ] Error codes: All error codes with exact messages specified

**All Stories:**
- [ ] No ambiguous language (avoid: "handles errors", "returns data", "works correctly")
- [ ] Given/When/Then uses concrete values, not placeholders
- [ ] Persona referenced with specific context

### Architecture Checklist {#architecture-checklist}

**Pattern Selection:**
- [ ] Project type identified and documented
- [ ] Default pattern evaluated against project needs
- [ ] Deviation from default documented as ADR (if applicable)

**Technology Decisions:**
- [ ] Language selection justified (not just "familiarity")
- [ ] Framework selection justified
- [ ] Database selection justified
- [ ] API style selection justified

**Standards Compliance:**
- [ ] OpenAPI documented (if REST)
- [ ] Error responses standardised
- [ ] Authentication approach documented
- [ ] Pagination approach documented (if applicable)

**Infrastructure:**
- [ ] Deployment target identified
- [ ] Scaling strategy documented
- [ ] Disaster recovery documented

---

## Version Schema {#version-schema}

The `.version` file tracks project schema version for upgrade compatibility.

```yaml
# sdlc-studio/.version
schema_version: 2          # Current template schema version
upgraded_from: 1           # Previous version (null for new projects)
upgraded_at: 2026-01-27T10:30:00Z  # When upgrade was performed
skill_version: "1.3.0"     # SDLC Studio version
created_at: 2026-01-15T09:00:00Z   # When project was initialised
```

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | number | 1=legacy, 2=modular |
| `upgraded_from` | number/null | Previous version (null if new) |
| `upgraded_at` | ISO date | Upgrade timestamp |
| `skill_version` | string | SDLC Studio version |
| `created_at` | ISO date | Project creation timestamp |

---

## See Also

- `SKILL.md` - Main skill entry point
- `help/*.md` - Type-specific command help
- `templates/core/*.md` - Core templates
- `templates/indexes/*.md` - Index templates
- `templates/modules/` - Optional modules
- `reference-config.md` - Configuration options
- `reference-upgrade.md` - Schema migration
