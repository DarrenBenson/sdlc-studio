# SDLC Studio Reference - Project

Detailed workflows for project-level orchestration across all epics.

<!-- Load when: running /sdlc-studio project plan or /sdlc-studio project implement -->

## Reading Guide

| Section | When to Read |
| --- | --- |
| Project Plan | When previewing execution order |
| Project Implement | When executing full project implementation |
| Commit Strategy | When choosing commit granularity |
| Quality Gates | When understanding enforcement boundaries |
| Mode Guide | When choosing between sequential, epic batch, and project batch |

---

## /sdlc-studio project plan - Step by Step {#project-plan-workflow}

1. **Load Epics**
   - Read `sdlc-studio/epics/_index.md`
   - For each epic, load the epic file
   - Extract "Blocked By" dependency entries

2. **Build Dependency Graph**
   - Create directed acyclic graph from epic dependencies
   - Topological sort to determine execution order
   - **Abort if circular dependencies detected** (report the cycle)

3. **Assess Readiness**
   For each epic in execution order:
   - Count stories by status (Draft, Ready, Done)
   - Flag epics with zero stories ("needs story generation")
   - Flag epics with all Draft stories ("needs Ready promotion")
   - Flag epics with unresolved dependency (blocked epic not Done)

4. **Estimate Waves** (if `--agentic`)
   For each epic, estimate agentic wave count:
   - Parse story dependencies within the epic
   - Classify stories by layer (backend/frontend/infra)
   - Estimate concurrent groups

5. **Output Plan**

   ```text
   == PROJECT IMPLEMENTATION PLAN ==

   Epics: 9 total (1 Done, 8 to implement)
   Stories: 55 remaining across 8 epics
   Estimated waves: 27 (with --agentic)

   Execution Order:
   | # | Epic | Title | Stories | Deps | Status |
   |---|------|-------|---------|------|--------|
   | 1 | EP0003 | Space Manifest System | 7 | None | Ready |
   | 2 | EP0002 | Dashboard & Agent Views | 8 | EP0001 (Done) | Ready |
   | 3 | EP0006 | Config, Audit & Notifications | 8 | EP0001 (Done) | Ready |
   | 4 | EP0004 | Backup & Storage | 10 | EP0001, EP0003 | Blocked |
   ...

   Dependency Graph:
   EP0001 (Done) --+-- EP0002 --+-- EP0007
                   |            +-- EP0009
                   +-- EP0006
                   +-- EP0004 -- EP0005
   EP0003 ---------+-- EP0004
                   +-- EP0008

   Ready to execute? Run: /sdlc-studio project implement [--agentic]
   ```

---

## /sdlc-studio project implement - Step by Step {#project-implement-workflow}

## 1. Parse Arguments

| Flag | Effect | Default |
| --- | --- | --- |
| `--agentic` | Use agentic waves within each epic | false |
| `--resume EP000X` | Resume from specific epic | first incomplete |
| `--skip EP000X` | Skip epic(s), comma-separated | none |
| `--from stories` | Generate stories for epics without them, then implement | - |
| `--from epics` | Generate epics from PRD, then stories, then implement | - |
| `--commit-strategy` | `per-wave`, `per-epic` (default), `per-project` | per-epic |
| `--no-artifacts` | Suppress PL/TS/WF file creation (agentic only) | false |
| `--skip-personas` | Skip persona consultations | false |
| `--yes` | Skip generation pause (auto-approve generated artifacts) | false |
| `--dry-run` | Preview plan without executing | false |

## 2. Load or Create Project State

Check for `sdlc-studio/.local/project-state.json`:

- If exists and `--resume` not specified: resume from last incomplete epic
- If exists and `--resume EP000X`: override resume point
- If not exists: create from epic dependency graph

```json
{
  "version": 1,
  "started_at": "2026-04-04T10:00:00Z",
  "updated_at": "2026-04-04T12:30:00Z",
  "status": "in_progress",
  "flags": {
    "agentic": true,
    "no_artifacts": true,
    "commit_strategy": "per-epic"
  },
  "epic_order": ["EP0003", "EP0002", "EP0006", "EP0004", "EP0005", "EP0009", "EP0007", "EP0008"],
  "epics": {
    "EP0003": { "status": "done", "stories": 7, "done": 7, "committed": true },
    "EP0002": { "status": "in_progress", "stories": 8, "done": 5, "committed": false },
    "EP0006": { "status": "pending", "stories": 8, "done": 0, "committed": false }
  },
  "checkpoints": {
    "last_commit": "EP0003",
    "last_reconcile": "EP0003",
    "last_review": null,
    "epics_since_review": 1
  }
}
```

## 3. Handle `--from` Generation

### `--from epics`

1. Check if `sdlc-studio/epics/` has epic files
2. If empty or incomplete: run `/sdlc-studio epic` to generate from PRD
3. Then fall through to `--from stories`

### `--from stories`

1. For each epic in execution order:
   - Check if epic has story files
   - If no stories: run `/sdlc-studio story --epic EP000X`
2. **Pause after generation** (unless `--yes`):

   ```text
   Generated stories for 8 epics (55 stories total).
   Review generated stories before proceeding?
   [Continue] / [Abort]
   ```

## 4. Validate Prerequisites

Before starting implementation:

- All epics have stories
- All stories for the first epic(s) meet Ready criteria (or can be auto-promoted)
- Git working tree is clean (source files; sdlc-studio changes acceptable)
- If `--agentic`: verify git worktree support

## 5. Execute Epics in Dependency Order

> **Before launching the first wave of the first epic:** Load `reference-agentic-lessons.md`. These are battle-tested lessons from production runs that prevent common failure modes in agentic execution.

For each epic in `epic_order`:

### 5a. Skip Check

- If epic in `--skip` list: mark skipped in state, continue
- If `--resume` and epic already Done: skip
- If epic blocked by incomplete dependency: **pause with clear message**

### 5b. Promote Stories

- All Draft stories in this epic: validate Ready criteria
- If criteria met: promote to Ready
- If criteria not met: report which stories fail and why, **pause**

### 5c. Execute Epic

```text
/sdlc-studio epic implement --epic EP000X [--agentic] [--no-artifacts] [--skip-personas]
```

This delegates to the existing epic implement workflow, which handles:

- Story dependency ordering within the epic
- Agentic wave analysis and execution (if `--agentic`)
- Per-story implementation (tests, code, verification)
- Story completion cascades

### 5d. Commit Checkpoint

Based on `--commit-strategy`:

| Strategy | Action |
| --- | --- |
| `per-wave` | Committed by epic implement after each wave |
| `per-epic` | Commit all epic changes now |
| `per-project` | Skip (commit at end) |

**Commit message format:**

```text
feat(EP000X): {epic title} ({N} stories)

{Story IDs completed}
Tests: {count} passing
Coverage: {percent}%

Co-Authored-By: Claude <noreply@anthropic.com>
```

### 5e. Reconcile Checkpoint

```text
/sdlc-studio reconcile --scope stories,epics
```

Auto-fixes: story index entries, epic status, dependency tables, AC checkboxes.

### 5f. Review Checkpoint

Check `checkpoints.epics_since_review`:

- If >= `review_interval` (default 3): run `/sdlc-studio review --quick`
- Reset counter

### 5g. Update Project State

Update `project-state.json` with:

- Epic status: done
- Timestamps
- Commit/reconcile flags
- Increment `epics_since_review`

## 6. Project Completion

After all epics complete:

1. **Final reconcile:** `/sdlc-studio reconcile` (full scope)
2. **Final review:** `/sdlc-studio review` (full, not quick)
3. **Final code check:** `/sdlc-studio code check`
4. **Update project state:** status: done, completed_at timestamp
5. **Report:**

```text
== PROJECT IMPLEMENTATION COMPLETE ==

Epics: 9/9 Done
Stories: 61/61 Done
Tests: 645 passing
Coverage: 91.7%
Commits: 25

Duration: ~2 hours
Waves: 27 (agentic)

All quality gates passed.
```

---

## Error Handling {#project-error-handling}

## Epic Failure

When an epic's implementation fails:

1. Update project state: epic status → failed, record error
2. Report which story and phase failed
3. Print resume instructions:

   ```text
   Epic EP0004 failed at US0025 (Backup Engine), Phase 5 (Test).
   
   To fix and resume:
   1. Fix the failing tests
   2. Run: /sdlc-studio project implement --resume EP0004
   ```

## Dependency Block

When an epic cannot start because a dependency is not Done:

```text
EP0004 blocked: depends on EP0003 (status: failed)

Options:
  1. Fix EP0003 first: /sdlc-studio project implement --resume EP0003
  2. Skip EP0004: /sdlc-studio project implement --skip EP0004
```

## Git Conflict

If commit fails (pre-commit hook, merge conflict):

1. Pause execution
2. Report the git error
3. User resolves manually, then: `/sdlc-studio project implement --resume EP000X`

---

## Commit Strategy {#commit-strategy}

| Strategy | Granularity | Rollback | Noise | Best For |
| --- | --- | --- | --- | --- |
| `per-wave` | After each agentic wave (2-3 stories) | Easy | High | Maximum safety, debugging |
| `per-epic` | After each epic completes | Medium | Low | **Default.** Balance of safety and cleanliness |
| `per-project` | After all epics complete | Hard | None | Speed, manual commit control |

**Commit message format varies by strategy:**

- `per-wave`: `feat(EP000X): wave N - US0001 summary bar + US0003 agent card`
- `per-epic`: `feat(EP000X): {epic title} ({N} stories, {M} tests)`
- `per-project`: User commits manually after project completes

---

## Quality Gates {#quality-gates}

Quality gates are **enforced** (blocking), not advisory. Failure pauses execution.

| Boundary | Checks | On Failure |
| --- | --- | --- |
| Wave | `typecheck` + `test suite` + `reconcile --scope stories` | Pause wave, report failures |
| Epic | `reconcile --scope stories,epics` + commit | Auto-fix drift, report unfixable |
| Every N epics | `review --quick` | Report findings, continue (advisory only) |
| Project | `review` + `reconcile` (full) + `code check` | Report all findings |

**Why reconcile at wave boundaries:** Without per-wave reconcile, story index entries, dependency tables, and epic checkboxes drift across waves. A 10-story epic with 4 waves accumulates 10 stories worth of drift before the epic reconcile runs. Per-wave reconcile (scoped to just the stories in that wave) keeps drift near zero with minimal overhead.

### Detecting Test/Typecheck Commands

| Indicator | Test Command | Typecheck Command |
| --- | --- | --- |
| `package.json` | `pnpm test` or `npm test` | `npx tsc --noEmit` |
| `pyproject.toml` | `pytest` | `mypy src/` |
| `go.mod` | `go test ./...` | `go vet ./...` |
| `Cargo.toml` | `cargo test` | `cargo check` |

---

## When to Use Each Mode {#mode-guide}

| Mode | Command | Artifacts Created | Status Flow | Use When |
| --- | --- | --- | --- | --- |
| **Full sequential** | `story implement --story US0001` | PL + TS + WF files | Draft -> Ready -> Planned -> In Progress -> Review -> Done | Single story work, debugging a failure, compliance/audit needs |
| **Epic batch** | `epic implement --agentic` | Optional (`--no-artifacts`) | Ready -> Done | One epic at a time, moderate-size features |
| **Project batch** | `project implement --agentic --no-artifacts` | project-state.json only | Ready -> Done | Full project implementation, greenfield, sprint planning |

### Artifact Value by Scale

| Artifact | Single Story | Epic Scale | Project Scale |
| --- | --- | --- | --- |
| Plan (PL file) | **Essential** - audit trail, edge case discovery | Useful - but agent prompt covers same ground | **Optional** - agent prompt IS the plan |
| Test Spec (TS file) | **Useful** - decouples spec from implementation | Marginal - story AC is the spec | **Skip** - inline TDD covers this |
| Workflow (WF file) | **Essential** - resume across sessions | Marginal - epic-level tracking suffices | **Skip** - project-state.json tracks progress |
| Status transitions | **All states** - Planned, In Progress, Review | Ready -> Done | Ready -> Done |

### Decision Tree

```text
Is this a single story fix or feature?
  Yes -> story implement (full 8-phase)
  No ->
    Is this one epic (3-10 stories)?
      Yes -> epic implement [--agentic]
      No ->
        Is this a full project (multiple epics)?
          Yes -> project implement --agentic --no-artifacts
```

---

## See Also

- `help/project.md` - Command quick reference
- `reference-epic.md` - Epic-level orchestration (called by project implement)
- `reference-epic.md#agent-prompt-template` - **Critical:** How to write effective agent prompts
- `reference-epic.md#post-wave-merge-protocol` - Step-by-step merge checklist
- `reference-story.md` - Story-level workflow (8-phase detail)
- `reference-outputs.md` - Status flows and completion cascades
- `reference-config.md` - Project configuration options
- `reference-reconcile.md` - Reconciliation workflow
- `reference-review.md` - Review workflow
