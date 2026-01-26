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

## See Also

- `SKILL.md` - Main skill entry point
- `help/*.md` - Type-specific command help
- `templates/*.md` - Output templates for each artifact type
