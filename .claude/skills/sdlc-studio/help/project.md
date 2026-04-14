<!--
Load: On /sdlc-studio project or /sdlc-studio project help
Dependencies: SKILL.md (always loaded first)
Related: reference-project.md (deep workflow), reference-epic.md
-->

# /sdlc-studio project - Project Implementation

## Quick Reference

```text
/sdlc-studio project plan                              # Preview execution plan
/sdlc-studio project implement                         # Execute all epics sequentially
/sdlc-studio project implement --agentic               # Agentic waves within each epic
/sdlc-studio project implement --agentic --no-artifacts  # Fast mode: no PL/TS/WF files
/sdlc-studio project implement --resume EP0003         # Resume from specific epic
/sdlc-studio project implement --from stories          # Generate stories first
/sdlc-studio project implement --from epics            # Generate epics + stories first
/sdlc-studio project implement --dry-run               # Preview without executing
```

## Prerequisites

- PRD must exist at `sdlc-studio/prd.md`
- TRD must exist at `sdlc-studio/trd.md`
- TSD must exist at `sdlc-studio/tsd.md`
- Epics must exist (or use `--from epics` to generate)
- Stories must exist (or use `--from stories` to generate)

## Actions

### plan

Preview the project execution plan: epic dependency order, story counts, readiness assessment.

**What happens:**

1. Loads all epics and their dependencies
2. Topological sort for execution order
3. Assesses story readiness per epic
4. If `--agentic`: estimates wave counts per epic
5. Displays execution plan

### implement

Execute full project implementation across all epics.

**What happens:**

1. Builds epic dependency graph and execution order
2. Optionally generates missing epics/stories (`--from`)
3. For each epic in order:
   - Promotes stories to Ready (validates criteria)
   - Runs `epic implement` (sequential or agentic)
   - Commits at configured boundary
   - Reconciles indexes and statuses
   - Periodic quick reviews
4. Final: full review + reconcile + report

## Flags

| Flag | Description | Default |
| --- | --- | --- |
| `--agentic` | Use agentic concurrent waves within each epic | false |
| `--no-artifacts` | Suppress plan/test-spec/workflow file creation (agentic only) | false |
| `--resume EP000X` | Resume from specific epic | first incomplete |
| `--skip EP000X` | Skip specific epic(s), comma-separated | none |
| `--from stories` | Generate stories for epics missing them before implementing | - |
| `--from epics` | Generate epics from PRD, then stories, then implement | - |
| `--commit-strategy` | `per-wave`, `per-epic` (default), `per-project` | per-epic |
| `--skip-personas` | Skip persona consultations | false |
| `--yes` | Auto-approve generated artifacts (skip pause after `--from`) | false |
| `--dry-run` | Show execution plan without running | false |

## Commit Strategy

| Strategy | Commits After | Best For |
| --- | --- | --- |
| `per-wave` | Each agentic wave | Maximum safety, easy rollback |
| `per-epic` | Each epic completes | **Default.** Balance of safety and cleanliness |
| `per-project` | All epics complete | Speed, manual commit control |

## Quality Gates (Enforced)

| Boundary | Checks |
| --- | --- |
| Wave | typecheck + test suite (must pass to advance) |
| Epic | auto-reconcile + status cascade |
| Every 3 epics | quick review |
| Project | full review + reconcile + code check |

## Output

```text
== PROJECT IMPLEMENTATION COMPLETE ==

Epics: 9/9 Done
Stories: 61/61 Done
Tests: 645 passing
Coverage: 91.7%
Commits: 25

All quality gates passed.
```

## Examples

```bash
# Full autonomous implementation of a greenfield project
/sdlc-studio project implement --agentic --no-artifacts

# Generate stories first, then implement
/sdlc-studio project implement --from stories --agentic --no-artifacts

# Start from scratch (generate epics + stories + implement)
/sdlc-studio project implement --from epics --agentic --no-artifacts --yes

# Resume after a failure
/sdlc-studio project implement --resume EP0004

# Skip a problematic epic
/sdlc-studio project implement --skip EP0008

# Preview execution plan
/sdlc-studio project plan --agentic

# Conservative: sequential with full artifacts
/sdlc-studio project implement
```

## When to Use

| Scenario | Command |
| --- | --- |
| Implementing a full PRD (5+ epics) | `project implement --agentic --no-artifacts` |
| Implementing remaining epics after partial work | `project implement --resume EP0005` |
| Previewing execution order and dependencies | `project plan` |
| Generating + implementing in one pass | `project implement --from stories --agentic --no-artifacts` |
| Conservative step-by-step with full audit trail | `project implement` (no flags) |

## Error Recovery

If an epic fails during execution:

```bash
# Fix the issue, then resume from the failed epic
/sdlc-studio project implement --resume EP0004

# Or skip the problematic epic and continue
/sdlc-studio project implement --skip EP0004
```

## See Also

**REQUIRED for this workflow:**

- `reference-project.md` - Full step-by-step workflow

**Related:**

- `/sdlc-studio epic implement --agentic` - Epic-level execution (called by project implement)
- `/sdlc-studio reconcile` - Status reconciliation (auto-run at checkpoints)
- `/sdlc-studio review` - Document review (auto-run periodically)
