# SDLC Studio Reference - Change Requests

Detailed workflows for Change Request management. CRs are the formal mechanism for proposing changes after the initial PRD is written.

<!-- Load when: creating, listing, actioning, reviewing, or closing CRs -->

## Reading Guide

| Section | When to Read |
| --- | --- |
| CR Create | When creating a new change request |
| CR List | When listing or filtering change requests |
| CR Action | When turning a CR into epics and stories (key workflow) |
| CR Review | When checking CR staleness and status cascade |
| CR Close | When completing, rejecting, or deferring a CR |
| Integration | When wiring CRs into status, review, reconcile |

---

## /sdlc-studio cr - Step by Step {#cr-default}

When invoked without an action, ask the user what they want to do:

```text
Change Request Management

What would you like to do?
1. Create a new change request
2. List existing change requests
3. Action a CR (turn into epics/stories)
4. Review CR statuses
5. Close a CR
6. Help
```

---

## /sdlc-studio cr create - Step by Step {#cr-create-workflow}

1. **Check Prerequisites**
   - Create `sdlc-studio/change-requests/` directory if needed
   - Scan for existing CRs to determine next ID:
     - Glob `sdlc-studio/change-requests/CR*.md`
     - Parse highest number, increment by 1
     - Apply ID collision prevention per `reference-outputs.md#id-collision-prevention`

2. **Gather CR Details**
   Prompt the user for:
   - **Title:** Short imperative description (e.g. "Add sender trust classification")
   - **Type:** One of: `feature-request`, `production-feedback`, `spec-gap`, `retrospective`, `design-change`
   - **Requester:** Who raised this (name or role)
   - **Priority:** P1 (critical gap), P2 (important), P3 (desirable), P4 (nice to have)

3. **Capture Problem Statement**
   - What is broken, missing, or suboptimal?
   - What evidence supports this? (user feedback, production data, review findings)
   - What happens if we don't address this?

4. **Capture Proposed Changes**
   For each change item:
   - Item title and description
   - Per-item priority (optional, defaults to CR priority)
   - Per-item effort estimate (optional, in story points)
   - Affected modules or components

   Multi-item CRs are common. Each item becomes a `### Item N:` sub-section.

5. **Impact Assessment**
   - Which existing features are affected? (cross-check PRD if available)
   - Any breaking changes?
   - Which modules will be modified?
   - What new tests are needed?

6. **Acceptance Criteria**
   - Checkbox list of verifiable criteria
   - Each AC must be testable (no "handles errors" -- use exact behaviour)
   - One AC per checkbox

7. **Risks and Dependencies**
   - Dependencies on other CRs (prompt: "Does this depend on any existing CRs?")
   - External dependencies (libraries, services, APIs)
   - Risks with likelihood/impact/mitigation

8. **Write CR File**
   - Use `templates/core/cr.md`
   - Assign ID: `CR{NNNN}` (zero-padded 4 digits)
   - Create slug from title (kebab-case, max 50 chars)
   - Write to `sdlc-studio/change-requests/CR{NNNN}-{slug}.md`
   - Status: `Proposed`

9. **Update Index**
   - Create or update `sdlc-studio/change-requests/_index.md`
   - Use `templates/indexes/cr.md` if creating new
   - Add row to registry table
   - Recalculate summary counts

10. **Report**

    ```text
    Created CR-{NNNN}: {title}
    File: sdlc-studio/change-requests/CR{NNNN}-{slug}.md
    Priority: {priority}
    Type: {type}
    Items: {count}

    Next: /sdlc-studio cr action --cr CR-{NNNN}
    ```

---

## /sdlc-studio cr list - Step by Step {#cr-list-workflow}

1. **Parse Filters**

| | Filter | Values | Default |
| --- | --- | --- | --- |
| | `--status` | proposed, approved, in-progress, complete, rejected, deferred | all |
| | `--priority` | P1, P2, P3, P4 | all |
| | `--affects` | module or component name | all |
| | `--type` | feature-request, production-feedback, spec-gap, retrospective, design-change | all |

1. **Read CR Files**
   - Glob `sdlc-studio/change-requests/CR*.md`
   - Parse frontmatter metadata from each file (Status, Priority, Type, Affects)

2. **Apply Filters and Sort**
   - Filter by matching criteria
   - Sort by priority (P1 first), then by date (oldest first)

3. **Display**

   ```text
   Change Requests (3 of 10)

   | ID | Title | Priority | Status | Type | Date |
   |----|-------|----------|--------|------|------|
   | CR-0008 | Email sender filtering | P1 | Proposed | feature-request | 2026-04-06 |
   | CR-0009 | Sender trust classification | P1 | Proposed | feature-request | 2026-04-06 |
   | CR-0010 | Outbound email enhancements | P3 | Proposed | feature-request | 2026-04-06 |
   ```

---

## /sdlc-studio cr action - Step by Step {#cr-action-workflow}

This is the key workflow that bridges from CR to the epic/story pipeline.

1. **Parse Arguments**
   - `--cr CR-NNNN` (required)

2. **Read CR**
   - Load the CR file from `sdlc-studio/change-requests/CR{NNNN}-*.md`
   - Parse all sections: Summary, Problem, Proposed Changes, Impact, AC
   - Validate status is `Proposed` or `Approved` (not already actioned)
   - If status is `In Progress` or `Complete`, warn and ask to confirm

3. **Check Dependencies**
   - If CR has dependencies (`Depends on` field), check their status
   - If any dependency is not `Complete` or `In Progress`, warn:

     ```text
     CR-0009 depends on CR-0008 (Status: Proposed)
     Proceed anyway? [y/N]
     ```

4. **Analyse Items**
   For each proposed change item in the CR:
   a) Determine if it maps to an existing epic (enhancement) or needs a new epic
   b) Cross-check PRD Feature Inventory for related features
   c) Estimate scope: new epic, stories added to existing epic, or single story

5. **Present Action Plan**
   Show the user a proposed mapping for confirmation:

   ```text
   CR-0001: Agent Lifecycle Endpoints

   Proposed action plan:
   | # | CR Item | Target | Action |
   |---|---------|--------|--------|
   | 1 | Quiesce agent | New EP00XX | Create epic + stories |
   | 2 | Resume agent | EP00XX (same) | Add to same epic |
   | 3 | Workspace metadata | EP00XX (same) | Add to same epic |

   Estimated: 1 new epic, 3 stories

   Proceed? [Y/n/edit]
   ```

   If user chooses "edit", allow them to reassign items to different epics.

6. **Generate Epics** (for new-epic items)
   For each new epic:
   a) Follow the standard epic creation workflow (`reference-epic.md#epic-workflow`)
   b) Add CR Reference to epic frontmatter:

      ```markdown
      > **Change Request:** [CR-{NNNN}: {title}](../change-requests/CR{NNNN}-{slug}.md)
      ```

   c) Populate epic from CR content:
      - Summary from CR summary (scoped to this epic's items)
      - Problem statement from CR problem
      - Acceptance criteria from CR AC (subset relevant to this epic)
      - Risks from CR risks
   d) Add revision history entry: `Epic created from CR-{NNNN}`
   e) Update epic index (`sdlc-studio/epics/_index.md`)

7. **Generate Stories** (for each epic)
   Follow standard story generation (`reference-story.md`) but:
   a) Use CR proposed changes as the primary input (not PRD features)
   b) Each CR item becomes one or more stories
   c) Stories reference CR in their Background section and revision history

8. **Update PRD Feature Inventory**
   For new features introduced by this CR:
   a) Add new rows to PRD Feature Inventory table
   b) Format: `| Feature Name | Description (CR-NNNN) | Priority | EP00XX |`
   c) If modifying existing features, add CR reference to description

9. **Update CR Status and Links**
   - Set CR status: `Proposed` or `Approved` → `In Progress`
   - Populate the "Linked Epics" section with generated/linked epic references
   - Update revision history: `CR actioned -- {N} epic(s), {M} story/stories created`

10. **Update Index and Report**
    - Refresh CR index counts
    - Report summary:

      ```text
      CR-0001 actioned successfully

      Epics created: 1 (EP0013: Agent Lifecycle Endpoints)
      Stories created: 3 (US0045, US0046, US0047)
      PRD features added: 1 (Agent Lifecycle)

      Next steps:
      - Review generated epics: /sdlc-studio epic review --epic EP0013
      - Plan implementation: /sdlc-studio epic plan --epic EP0013
      - Or implement directly: /sdlc-studio epic implement --epic EP0013
      ```

---

## /sdlc-studio cr review - Step by Step {#cr-review-workflow}

1. **Read All CRs**
   - Glob `sdlc-studio/change-requests/CR*.md`
   - Parse status, linked epics, created date, depends-on from each

2. **Status Cascade Check**
   For each CR with status `In Progress`:
   a) Find all linked epics from the "Linked Epics" section
   b) Look up each epic's actual status
   c) If ALL linked epics are `Done`:
      - Flag: "CR-{NNNN} -- all linked epics Done, suggest marking Complete"
   d) If SOME linked epics are Done but not all:
      - Report progress: "CR-{NNNN} -- 2/3 linked epics Done"

3. **Staleness Check**
   For each CR with status `Proposed`:
   a) Parse created date
   b) If older than 14 days: flag as stale
   c) Suggest action: approve, reject, or defer

4. **Dependency Check**
   For CRs with dependencies:
   a) Check if dependent CRs are `Complete`
   b) If dependency is still `Proposed`: flag the chain
   c) Report: "CR-0009 blocked by CR-0008 (Proposed)"

5. **Report**

   ```text
   Change Request Review

   In Progress (1):
     CR-0001: Agent Lifecycle -- all 1 epic(s) Done ✅ suggest close

   Proposed (3):
     CR-0008: Email Sender Filtering -- 8 days old
     CR-0009: Sender Trust Classification -- 8 days old, blocked by CR-0008
     CR-0010: Outbound Email -- 2 days old

   Stale (> 14 days): 0

   Actions:
   - Close CR-0001: /sdlc-studio cr close --cr CR-0001
   - Action CR-0008: /sdlc-studio cr action --cr CR-0008
   ```

---

## /sdlc-studio cr close - Step by Step {#cr-close-workflow}

1. **Parse Arguments**
   - `--cr CR-NNNN` (required)

2. **Read CR**
   - Load CR file
   - Validate CR exists
   - If already `Complete`, `Rejected`, or `Deferred`: warn "CR already closed"

3. **Prompt for Close Reason**

   ```text
   Close CR-0001: Agent Lifecycle Endpoints

   Outcome:
   1. Complete -- all changes implemented and verified
   2. Rejected -- will not implement (provide reason)
   3. Deferred -- postponed to future release (provide timeline)
   ```

   For **Complete**:
   - Verify all linked epics are Done
   - Verify all AC checkboxes can be ticked
   - If not all Done: warn and ask to confirm

   For **Rejected**:
   - Prompt for rejection reason

   For **Deferred**:
   - Prompt for expected timeline or release target

4. **Update CR File**
   - Set status to chosen terminal status
   - For Complete: format as `Complete -- EP{NNNN} (Done)` (matching agent-bridge pattern)
   - Tick all AC checkboxes (for Complete)
   - Fill "Close Reason" section with outcome and rationale
   - Update revision history

5. **Update Index**
   - Refresh summary counts
   - Update registry table row

---

## Integration with Existing Workflows {#cr-integration}

## Status Dashboard {#cr-status-integration}

When `/sdlc-studio status` runs, add to the Requirements pillar:

```text
📋 REQUIREMENTS
   ...existing PRD/Epic/Story status...
   📝 CRs: 2 Proposed, 1 In Progress, 7 Complete
```

Only show if `sdlc-studio/change-requests/` directory exists with CR files.

## Hint {#cr-hint-integration}

When `/sdlc-studio hint` runs:

- If stale Proposed CRs (> 14 days): suggest `cr review`
- If In Progress CRs with all epics Done: suggest `cr close --cr CR-NNNN`
- If Proposed CRs exist and no epics in progress: suggest `cr action --cr CR-NNNN`

## Reconcile {#cr-reconcile-integration}

When `/sdlc-studio reconcile` runs (with `--scope crs` or no scope filter):

**Detect:**

- CR index entry status vs CR file status → mismatch?
- CR index summary counts vs actual counts → drift?
- In Progress CRs with all linked epics Done → suggest completion (report only, never auto-apply)

**Fix (mechanical only):**

- Update index entry statuses to match file statuses
- Recalculate summary counts
- Update dependency statuses from actual CR files

## Review {#cr-review-integration}

When `/sdlc-studio review` runs (unified review):

- Add CR staleness check after cross-document consistency
- Include CR counts in the consolidated report
- Flag In Progress CRs where all linked epics are Done

---

## Principles {#cr-principles}

1. **File is truth.** The CR file is the authoritative source. The index is derived.
2. **Complete is never auto-assigned.** Completing a CR requires user confirmation because it's a judgment call (did the implementation actually address the request?).
3. **Action is the bridge.** The `action` command is the critical workflow that connects CRs to the epic/story pipeline. Without it, CRs are just documents.
4. **Multi-item CRs are first-class.** A single CR can contain multiple change items, each mapping to different epics. The action plan makes this explicit.
5. **Dependencies are declared, not enforced.** CRs declare dependencies but don't block actioning. The user is warned and decides.
6. **CRs are durable.** Unlike bugs (which get fixed and closed), CRs may span multiple releases and epics. The "Linked Epics" section grows over time.

---

## See Also

- `help/cr.md` -- Quick command reference
- `reference-outputs.md` -- Status values, ID formats, file locations
- `reference-epic.md` -- Epic generation workflow (used by `cr action`)
- `reference-story.md` -- Story generation workflow (used by `cr action`)
- `reference-reconcile.md` -- Reconciliation including CR scope
- `reference-review.md` -- Unified review including CR staleness
