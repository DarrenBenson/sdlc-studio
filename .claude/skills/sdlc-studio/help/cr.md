<!--
Load: On /sdlc-studio cr or /sdlc-studio cr help
Dependencies: SKILL.md (always loaded first)
Related: reference-cr.md (deep workflow), templates/core/cr.md
-->

# /sdlc-studio cr - Change Requests

> **Source of truth:** `reference-cr.md` - Detailed workflow steps

## Quick Reference

```text
/sdlc-studio cr                        # Ask what to do (interactive)
/sdlc-studio cr create                 # Create new change request
/sdlc-studio cr list                   # List all change requests
/sdlc-studio cr list --status proposed # List proposed CRs
/sdlc-studio cr list --priority P1     # List P1 change requests
/sdlc-studio cr action --cr CR-0001    # Turn CR into epics and stories
/sdlc-studio cr review                 # Review CR statuses
/sdlc-studio cr close --cr CR-0001     # Complete, reject, or defer a CR
```

## Prerequisites

- PRD should exist at `sdlc-studio/prd.md` (for feature inventory linking)
- For `action`: Epics directory should exist at `sdlc-studio/epics/`
- For `close --outcome complete`: Linked epics should be Done

## Actions

### (default)

Ask what to do: create, list, action, review, close, or help.

### create

Create a new change request with full traceability.

**What happens:**

1. Prompts for CR details (title, type, priority, requester)
2. Captures problem statement
3. Captures proposed changes (supports multi-item CRs)
4. Assesses impact on existing features
5. Defines acceptance criteria
6. Records risks and dependencies
7. Creates CR file using `templates/core/cr.md`
8. Updates `sdlc-studio/change-requests/_index.md`

**Interactive prompts:**

- Title (short imperative description)
- Type (feature-request, production-feedback, spec-gap, retrospective, design-change)
- Priority (P1/P2/P3/P4)
- Requester name
- Problem statement
- Proposed changes (one or more items)
- Affected modules
- Acceptance criteria

### list

List change requests with optional filtering.

**Filters:**

| Filter | Description |
| --- | --- |
| `--status proposed` | Proposed CRs only |
| `--status in-progress` | CRs being implemented |
| `--status complete` | Completed CRs |
| `--priority P1` | P1 priority only |
| `--type feature-request` | Feature requests only |
| `--affects module` | CRs affecting a specific module |

**Output:**

```text
## Change Requests (3 of 10)

| ID | Title | Priority | Status | Type | Date |
|----|-------|----------|--------|------|------|
| CR-0008 | Email sender filtering | P1 | In Progress | feature-request | 2026-04-06 |
| CR-0009 | Sender trust classification | P1 | In Progress | feature-request | 2026-04-06 |
```

### action

Turn a change request into epics and stories. **This is the key workflow.**

**What happens:**

1. Reads the CR and validates status (must be Proposed or Approved)
2. Checks CR dependencies
3. Analyses each change item for epic mapping
4. Presents action plan (new epics vs existing epics) for confirmation
5. Generates epics with CR Reference metadata
6. Generates stories from CR items
7. Updates PRD Feature Inventory with CR references
8. Marks CR as In Progress with linked epic references
9. Reports what was created

**Usage:**

```text
/sdlc-studio cr action --cr CR-0001
```

**Action plan output:**

```text
CR-0001: Agent Lifecycle Endpoints

| # | CR Item | Target | Action |
|---|---------|--------|--------|
| 1 | Quiesce agent | New EP0013 | Create epic + stories |
| 2 | Resume agent | EP0013 (same) | Add to same epic |
| 3 | Workspace info | EP0013 (same) | Add to same epic |

Estimated: 1 new epic, 3 stories
Proceed? [Y/n/edit]
```

### review

Review CR statuses against implementation state.

**What happens:**

1. Checks In Progress CRs: all linked epics Done? Suggest closing.
2. Checks Proposed CRs: older than 14 days? Flag as stale.
3. Checks dependencies: any blocked chains?
4. Reports with suggested actions.

**Output:**

```text
CR Review

In Progress (1):
  CR-0001: Agent Lifecycle -- all epics Done ✅ suggest close

Proposed (2):
  CR-0009: Trust Classification -- 8 days old, blocked by CR-0008
  CR-0010: Outbound Email -- 2 days old

Stale (> 14 days): 0
```

### close

Mark a CR as complete, rejected, or deferred.

**What happens:**

1. Prompts for outcome: Complete, Rejected, or Deferred
2. For Complete: verifies linked epics are Done, ticks AC checkboxes
3. Records close reason
4. Updates CR file and index

**Usage:**

```text
/sdlc-studio cr close --cr CR-0001
```

## CR Types

| Type | When to Use | Example |
| --- | --- | --- |
| `feature-request` | New capability needed | "Add sender trust classification" |
| `production-feedback` | Issues found after deploy | "Inbox API bypasses sender filter" |
| `spec-gap` | Missing specification | "No TRD section for security module" |
| `retrospective` | Post-implementation learnings | "Hotfix changes need formal tracking" |
| `design-change` | Architecture modification | "Replace polling with webhooks" |

## Priority Guide

| Priority | Description | Action Timeline |
| --- | --- | --- |
| P1 | Critical gap, blocks users or security risk | This sprint |
| P2 | Important improvement, noticeable impact | Next sprint |
| P3 | Desirable enhancement | This release |
| P4 | Nice to have, low impact | When capacity allows |

## Output

### CR File

**Location:** `sdlc-studio/change-requests/CR{NNNN}-{slug}.md`

**Sections:**

- Summary and metadata (status, priority, type, requester, affects, depends on)
- Problem statement
- Proposed changes (multi-item with per-item priority)
- Impact assessment (affected modules, breaking changes)
- Acceptance criteria
- Risks
- Dependencies (CR and external)
- Linked epics (populated on action)
- Out of scope
- Open questions
- Close reason (populated on close)

### CR Index

**Location:** `sdlc-studio/change-requests/_index.md`

**Contents:**

- Summary counts by status
- Counts by priority
- All CRs registry table
- Dependencies table

## Integration

### Epic Integration

When a CR is actioned:

- Epic gets `> **Change Request:**` metadata linking to the CR
- Epic summary references the CR as its origin
- Epic revision history notes "Created from CR-NNNN"

### PRD Integration

When a CR adds new features:

- PRD Feature Inventory gets new rows with `(CR-NNNN)` annotation
- Existing features modified by CR get CR reference added to description

### Status Integration

`/sdlc-studio status` shows:

```text
📋 REQUIREMENTS
   ...
   📝 CRs: 2 Proposed, 1 In Progress, 7 Complete
```

`/sdlc-studio hint` suggests:

```text
## Next Step
**Action:** Review change requests
**Run:** `/sdlc-studio cr review`
**Why:** CR-0008 proposed 15 days ago (stale)
```

### Reconcile Integration

`/sdlc-studio reconcile --scope crs` checks:

- CR index entries match file statuses
- Summary counts are correct
- In Progress CRs with all epics Done flagged for closure (report only)

## CR Lifecycle

```text
     Proposed
        │
    [approve]
        │
        ▼
     Approved ──[reject]──▶ Rejected
        │
     [action]
        │
        ▼
   In Progress ──[defer]───▶ Deferred
        │
  [all epics Done]
        │
      [close]
        │
        ▼
     Complete
```

## Examples

```text
# Create a change request interactively
/sdlc-studio cr create

# List all proposed CRs
/sdlc-studio cr list --status proposed

# List P1 change requests
/sdlc-studio cr list --priority P1

# Turn a CR into epics and stories
/sdlc-studio cr action --cr CR-0001

# Review all CR statuses
/sdlc-studio cr review

# Close a completed CR
/sdlc-studio cr close --cr CR-0001

# List CRs affecting a specific module
/sdlc-studio cr list --affects email
```

## See Also

**REQUIRED for this workflow:**

- `reference-cr.md` - Change request workflow details

**Recommended:**

- `/sdlc-studio epic help` - Epic generation (used by `cr action`)
- `/sdlc-studio prd help` - PRD management (features linked to CRs)

**Optional (deep dives):**

- `reference-outputs.md` - Output formats reference
