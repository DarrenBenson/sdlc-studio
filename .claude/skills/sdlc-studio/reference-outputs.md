# SDLC Studio Output Reference

Single source of truth for all output formats, file locations, status values, and transitions.

## Output Formats {#output-formats}

| Type | Location | Naming | Status Values |
| --- | --- | --- | --- |
| PRD | `sdlc-studio/prd.md` | Fixed | Feature status markers |
| TRD | `sdlc-studio/trd.md` | Fixed | Draft/Approved |
| Persona | `sdlc-studio/personas.md` | Fixed | - |
| TSD | `sdlc-studio/tsd.md` | Fixed | - |
| Epic | `sdlc-studio/epics/EP{NNNN}-*.md` | EP0001, EP0002, EP0003... | Draft/Ready/Approved/In Progress/Done |
| Story | `sdlc-studio/stories/US{NNNN}-*.md` | US0001, US0002, US0003... | Draft/Ready/Planned/In Progress/Review/Done/Won't Implement/Deferred/Superseded |
| Plan | `sdlc-studio/plans/PL{NNNN}-*.md` | PL0001, PL0002, PL0003... | Draft/In Progress/Complete/Superseded |
| Bug | `sdlc-studio/bugs/BG{NNNN}-*.md` | BG0001, BG0002, BG0003... | Open/In Progress/Fixed/Verified/Closed/Won't Fix |
| CR | `sdlc-studio/change-requests/CR{NNNN}-*.md` | CR0001, CR0002, CR0003... | Proposed/Approved/In Progress/Complete/Rejected/Deferred |
| Test Spec | `sdlc-studio/test-specs/TS{NNNN}-*.md` | TS0001, TS0002, TS0003... | Draft/Ready/In Progress/Complete/Superseded |
| Workflow | `sdlc-studio/workflows/WF{NNNN}-*.md` | WF0001, WF0002, WF0003... | Created/Planning/Testing/Implementing/Verifying/Reviewing/Checking/Done/Paused/Superseded |
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

**Terminal status transitions (non-Done):**

- **Any → Won't Implement:** Decision not to build this story. Document reason in story file. Execute [Story Completion Cascade](#story-completion-cascade) with target status "Superseded" for linked artifacts.
- **Any → Deferred:** Story postponed to a future release. Document reason and expected timeline. Execute [Story Completion Cascade](#story-completion-cascade) with target status "Superseded" for linked artifacts.
- **Any → Superseded:** Story replaced by a different story or combined approach (e.g. two stories merged into one). Document replacement in story file, cross-reference the superseding story. Execute [Story Completion Cascade](#story-completion-cascade) with target status "Superseded" for linked artifacts.

### Compressed Status Flow (Agentic Batch Mode) {#compressed-status-flow}

When `--no-artifacts` is active during `epic implement --agentic` or `project implement --agentic`:

```text
Story:  Draft → Ready → Done  (skip Planned, In Progress, Review)
Epic:   Draft → Done          (skip Ready, Approved, In Progress)
Plan:   (not created)
Test Spec: (not created)
Workflow:  (not created)
```

The compressed flow is valid **only** during batch agentic execution where:

- The agent prompt serves as the plan
- Tests are written inline (TDD within agent)
- Verification runs at wave boundaries (typecheck + test suite)
- Quality gates (phases 5-7) are still enforced

For sequential single-story work, use the full status flow above.

**Rationale:** In the compressed flow, the agent receives complete story AC, TRD context, and codebase patterns in a single prompt. It produces code + tests atomically. The intermediate states (Planned, In Progress, Review) would each persist for milliseconds during a wave, providing no audit value. Git history and the project-state.json provide equivalent traceability.

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

### Change Request Status Flow {#cr-status-flow}

```text

Proposed → Approved → In Progress → Complete
                   ↘ Rejected
                   ↘ Deferred
```

**Transition criteria:**

- **Proposed → Approved:** Stakeholder review complete, decision to proceed
- **Proposed → Rejected:** Decision not to implement (document reason)
- **Proposed → Deferred:** Postponed to future release (document timeline)
- **Approved → In Progress:** CR actioned -- epics and stories created via `/sdlc-studio cr action`
- **In Progress → Complete:** All linked epics Done, all AC met (user confirmation required)

**Note:** Complete is never auto-assigned. Completing a CR is a judgment call -- the reconciler suggests but does not auto-transition.

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

> **Agentic execution:** When `epic implement --agentic` runs, each story still produces a standard workflow file with these status transitions. Wave-level orchestration (pre-flight checks, post-wave test runs) is tracked in the epic file, not in individual workflow files. See `reference-epic.md#flag-agentic`.

## Status Vocabulary Enforcement {#status-vocabulary}

Each artifact type has a **canonical set of status values**. Do not use ad-hoc statuses (e.g., "Active", "Review", "Planned" for plans). Non-standard values cause dashboard misreporting.

| Type | Allowed Statuses | Terminal |
| --- | --- | --- |
| Epic | Draft, Ready, Approved, In Progress, Done | Done |
| Story | Draft, Ready, Planned, In Progress, Review, Done, Won't Implement, Deferred, Superseded | Done, Won't Implement, Deferred, Superseded |
| Plan | Draft, In Progress, Complete, Superseded | Complete, Superseded |
| Test Spec | Draft, Ready, In Progress, Complete, Superseded | Complete, Superseded |
| Bug | Open, In Progress, Fixed, Verified, Closed, Won't Fix | Closed, Won't Fix |
| CR | Proposed, Approved, In Progress, Complete, Rejected, Deferred | Complete, Rejected, Deferred |
| Workflow | Created, Planning, Testing, Implementing, Verifying, Reviewing, Checking, Done, Paused, Complete, Superseded | Done, Complete, Superseded |

**Validation rule:** When writing or updating a `> **Status:**` header, verify the value is in the allowed set for that artifact type. If a non-standard value is found during `status --full`, flag it in the INTEGRITY section.

### Project-Level Document Exemptions {#project-level-exemptions}

The following project-level documents do **not** follow the standard Draft-to-Done lifecycle. They are exempt from lifecycle status checks in `status --full` and health-check rules.

| Document | Location | Reason for Exemption |
| --- | --- | --- |
| PRD | `sdlc-studio/prd.md` | Living document. Uses feature status markers, not lifecycle status. |
| TRD | `sdlc-studio/trd.md` | Uses Draft/Approved only. No terminal "Done" state - evolves with architecture. |
| TSD | `sdlc-studio/tsd.md` | Strategy document. Updated as test approach evolves, not per-story lifecycle. |
| Personas | `sdlc-studio/personas.md` | Reference document. No status field - always current or updated in place. |
| Brand Guide | `sdlc-studio/brand-guide.md` | Reference document. No lifecycle status - defines project visual identity. |

**Rule:** When `status --full` or health-check scans for stale/missing statuses, skip files matching these locations. Do not flag them as missing a status field or having a non-standard status.

## ID Collision Prevention {#id-collision-prevention}

Before assigning any artifact ID, **always check for existing files with the same ID prefix:**

```text
Glob: sdlc-studio/{type}/{PREFIX}{NNNN}*.md
```

If one or more files already exist with that ID:

1. Increment to the next available ID
2. Log a warning: `ID collision avoided: {ID} already used by {existing_file}`

**Known historical collisions** (for reference): TS0012, TS0180, TS0190, TS0201, PL0180, PL0184, PL0190, PL0201. These exist from before collision prevention was added.

## File Naming Conventions {#file-naming}

### ID Formats {#id-formats}

Each numbered artifact type uses a 4-digit zero-padded ID:

| Type | Format | Example |
| --- | --- | --- |
| Epic | `EP{NNNN}` | EP0001, EP0024, EP0100 |
| Story | `US{NNNN}` | US0001, US0042, US0500 |
| Plan | `PL{NNNN}` | PL0001, PL0015, PL0200 |
| Bug | `BG{NNNN}` | BG0001, BG0007, BG0050 |
| CR | `CR{NNNN}` | CR0001, CR0008, CR0050 |
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
- `CR0001-agent-lifecycle-endpoints.md`
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
| --- | --- |
| Epic | `sdlc-studio/epics/_index.md` |
| Story | `sdlc-studio/stories/_index.md` |
| Plan | `sdlc-studio/plans/_index.md` |
| Bug | `sdlc-studio/bugs/_index.md` |
| CR | `sdlc-studio/change-requests/_index.md` |
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
 ├─ CR (CR0001) ← change request, actioned into epics via /sdlc-studio cr action
 │   └─ Epic (EP0013) ← created from CR
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
| --- | --- | --- |
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
| --- | --- | --- |
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
| --- | --- | --- |
| `review-state.json` | Review timestamps | Each developer's review history differs |
| `review-queue.json` | Pause/resume state | One user's paused review shouldn't affect others |
| `status-cache.json` | Cached lint/coverage | Machine-specific results |
| `upgrade-dismissed.json` | Upgrade prompt preference | User's choice to suppress upgrade prompts |
| `project-state.json` | Project implement progress | Tracks epic execution order, per-epic status, checkpoints. See `reference-project.md` for schema |

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
| --- | --- | --- |
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
| --- | --- | --- | --- |
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

### Story Completion Cascade Checklist {#story-completion-cascade}

When a story reaches any **terminal status** (Done, Won't Implement, Deferred, Superseded), all linked artifacts MUST be updated immediately. This is the single canonical cascade procedure - all code paths reference this checklist rather than maintaining inline copies.

> **Owner field:** When a story transitions to In Progress (during `code implement` or `story implement`), set `> **Owner:**` to the person or agent performing the work. If Owner is still `--` when the cascade runs, set it to the user's git identity or the project owner. This is a catch-up mechanism -- ideally Owner is set at implementation start.

**Target status mapping:**

| Story Terminal Status | Plan Target | Test Spec Target | Workflow Target |
| --- | --- | --- | --- |
| Done | Complete | Complete | Complete/Done |
| Won't Implement | Superseded | Superseded | Superseded |
| Deferred | Superseded | Superseded | Superseded |
| Superseded | Superseded | Superseded | Superseded |

**Mandatory cascade steps:**

1. **Find and update plan:** Search `sdlc-studio/plans/` for the plan linked to this story. Update `> **Status:**` to the target status from the table above. Update `plans/_index.md` entry.
2. **Find and update test spec:** Search `sdlc-studio/test-specs/` for the spec linked to this story. Update `> **Status:**` to the target status. Update `test-specs/_index.md` entry. For epic-scoped specs, see [Epic-Scoped Coverage](reference-test-spec.md#epic-scoped-coverage) - only cascade when ALL covered stories are terminal.
3. **Find and update workflow:** Search `sdlc-studio/workflows/WF*` for the workflow linked to this story. Update `> **Status:**` to the target status. Update any non-terminal phase statuses.
4. **Recalculate index counts:** Update summary counts in `plans/_index.md`, `test-specs/_index.md`, and `workflows/_index.md` if they contain summary sections.
5. **Check epic status:** If all stories in the parent epic are now terminal, suggest marking the epic as Done (user confirms - never auto-assign).
6. **Document reason:** For non-Done terminal statuses, ensure the story file contains a reason (e.g. "Superseded by US0026 which combines US0025 and US0027").
7. **Update story index entries:** Set the story's status in `stories/_index.md` -- both the per-epic table and the All Stories table. Recalculate summary counts (Draft↓, Done↑). This is mechanical bookkeeping, not a status decision.
8. **Update epic story breakdown:** In the parent epic file, tick the checkbox for this story in the Story Breakdown section (`- [ ]` → `- [x]`).
9. **Update downstream story dependency tables:** Search all story files (`sdlc-studio/stories/US*.md`) for dependency tables referencing this story. Update the Status column to match this story's terminal status. This prevents downstream stories from showing stale dependency statuses (e.g. "Draft" when the dependency is Done).
10. **Tick test scenario checkboxes:** If the story has a `## Test Scenarios` section with `- [ ]` checkboxes, tick all items that have corresponding passing tests. Match by test description -- if a test file contains a test matching the scenario description, tick it (`- [ ]` → `- [x]`).
11. **Cascade epic completion:** If step 5 resulted in the epic being marked Done (user confirmed), execute the **[Epic Completion Cascade](#epic-completion-cascade)** immediately. This cascades outward to PRD feature statuses, dependency tables in other epics, and all indexes.

**Code paths that trigger this cascade:**

- `reference-code.md` → code verify step 9 (story marked Done after verification)
- `reference-code.md` → code test step 8 (story moved to Done after tests pass)
- `reference-story.md` → story review step 3 (user confirms Done)
- `reference-story.md` → story implement step 6a (workflow completion cascade)
- `reference-reconcile.md` → reconcile command (catch-up for missed cascades)
- Manual status change (any workflow that sets a story to a terminal status)

> **Why this matters:** Without cascading, artifact files accumulate stale statuses (Draft/Ready/In Progress) even though the linked story is terminal. This creates misleading dashboard output, false health-check findings, stale dependency tables in downstream stories and epics, and PRD feature statuses stuck on "Not Started" despite implementation. Steps 7-11 were added after review sessions found 15 stale story index entries, 82+ unchecked checkboxes, 14 stale dependency references across 7 epics, and 31 unticked test scenario checkboxes across 3 stories.

### Epic Completion Cascade Checklist {#epic-completion-cascade}

When an epic is marked Done (user confirmed), all related artifacts MUST be updated immediately. This is the canonical cascade for epic completion -- all code paths reference this checklist.

**Mandatory cascade steps:**

1. **Update epic file:** Set `> **Status:** Done`. Set `> **Last Updated:** {today}` (add the field after Created if it doesn't exist). Tick all AC checkboxes (`- [ ]` → `- [x]`) that have been verified against the codebase. Tick all story breakdown checkboxes (`- [ ]` → `- [x]`).
2. **Update epic index:** Set epic status to Done in `epics/_index.md` table. Recalculate summary counts (Draft↓, Done↑).
3. **Update PRD feature statuses:** For each PRD feature mapped to this epic (via the Feature Inventory table's Epic column), update `**Status:** Not Started` → `**Status:** Complete` and tick AC checkboxes matching implemented functionality. Use `**Status:** Partial` if some AC items remain unmet.
4. **Update dependency tables:** Scan ALL epic files (`sdlc-studio/epics/EP*.md`) for dependency tables referencing this epic. Update the Status column from any non-Done value to "Done". This is mechanical bookkeeping -- the epic IS Done, so every reference to it should reflect that.
5. **Recalculate story index:** Ensure all stories for this epic show Done in `stories/_index.md` (both per-epic table and All Stories table). Recalculate summary counts. This catches up any stories missed by individual Story Completion Cascades.
6. **Update PRD metadata:** Update `**Last Updated:**` date in the PRD header to today. Add a changelog entry: `| {date} | Claude | EP{NNNN} marked Done: {N} features updated to Complete |`.
7. **Consult affected personas:** If personas exist in `sdlc-studio/personas/`, consult the personas listed in the epic's "Affected Personas" section. Brief consultation (not full workshop): does the implementation meet their stated needs? Append any concerns to the epic's Revision History. Skip if `--skip-personas` was passed.
8. **Flag TRD/TSD for review:** If the completed epic introduced new interfaces, endpoints, or test patterns, report that TRD and/or TSD may need updating. Do not auto-modify -- report only.
9. **Run reconcile (catch-up):** Execute `reconcile --scope stories,epics` to catch any drift missed by individual story cascades. This is especially important after `epic implement --agentic` where multiple stories complete in rapid succession and individual cascades may be compressed or skipped.

**Code paths that trigger this cascade:**

- `reference-epic.md` → epic implement step 6 (all stories complete, user confirms Done)
- `reference-epic.md` → epic review (user confirms Done)
- `reference-code.md` → code verify step 9 (if last story in epic triggers epic Done via Story Cascade step 9)
- `reference-reconcile.md` → reconcile command (catch-up cascade for epics already Done but never cascaded)
- Manual epic status change

> **Why this matters:** Without epic-level cascading, PRD feature statuses remain "Not Started" indefinitely, dependency tables in downstream epics show stale statuses, and epic indexes drift from reality. This was the primary source of drift found during the EP0001-EP0005 review session.

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
| --- | --- | --- |
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
