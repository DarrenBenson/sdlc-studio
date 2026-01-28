<!--
Load: On /sdlc-studio epic or /sdlc-studio epic help
Dependencies: SKILL.md (always loaded first)
Related: reference-epic.md (deep workflow), templates/core/epic.md
-->

# /sdlc-studio epic - Epics

## Quick Reference

```
/sdlc-studio epic                   # Generate Epics from PRD
/sdlc-studio epic review            # Review Epic status
/sdlc-studio epic --perspective engineering  # TRD-aligned technical focus
/sdlc-studio epic --perspective product      # PRD-aligned product focus
/sdlc-studio epic --perspective test         # TSD-aligned testing focus
/sdlc-studio epic plan --epic EP0004      # Preview workflow for all stories
/sdlc-studio epic implement --epic EP0004 # Execute workflow for all stories
```

## Prerequisites

- PRD must exist at `sdlc-studio/prd.md`
- Run `/sdlc-studio prd` first if missing

## Actions

### generate (default)
Parse PRD and group features into Epics.

**What happens:**
1. Reads Feature Inventory from PRD
2. Groups related features (5-8 per Epic)
3. Creates Epic files with business context, scope, acceptance criteria
4. Creates `sdlc-studio/epics/_index.md` registry

**Grouping heuristics:**
- Features sharing same user type → same Epic
- Features with shared dependencies → same Epic
- Features forming complete user journey → same Epic

**Perspective option:**

Use `--perspective` to generate epics with specific focus aligned to document types:

| Perspective | Aligns With | Focus Areas |
|-------------|-------------|-------------|
| `engineering` | TRD | Components, APIs, data models, tech dependencies |
| `product` | PRD | User value, success metrics, priority rationale |
| `test` | TSD | Test types, coverage targets, risk-based priorities |

### review
Review Epic status based on Stories and codebase. **Cascades by default** - reviews epic and all changed stories/code.

```bash
/sdlc-studio epic review                  # Cascade review (default)
/sdlc-studio epic review --quick          # Epic only, skip stories
/sdlc-studio epic review --resume         # Resume from pause point
/sdlc-studio epic review --epic EP0001    # Target specific epic
```

**Flags:**

| Flag | Description | Default |
|------|-------------|---------|
| `--quick` | Skip cascade, review only the epic | false |
| `--resume` | Resume from where review paused | false |
| `--epic` | Target specific epic | all epics |

**What happens (cascade mode):**
1. Builds review queue - stories/code changed since last review
2. Reviews changed story specs against implementation
3. Reviews changed code for quality issues
4. Reviews epic-level acceptance criteria
5. Stores findings in `sdlc-studio/reviews/RV{NNNN}-*.md`
6. Updates `.local/review-state.json` with review timestamps

**What happens (quick mode):**
1. Reads all Epics and their linked Stories
2. Calculates completion from Story status
3. Updates status and acceptance criteria checkboxes
4. No deep story/code review

## Output

**Files:**
- `sdlc-studio/epics/EP{NNNN}-{slug}.md` per Epic
- `sdlc-studio/epics/_index.md` registry

**Status values:** Draft | Ready | Approved | In Progress | Done

**Status rules:**
- New epics start as "Draft"
- `epic review` suggests "Done" when all stories complete, but user confirms

> **Source of truth:** `reference-decisions.md` → Status Transition Rules

**Epic sections:**
- Summary
- Business Context (problem, value, metrics)
- Scope (in/out, affected personas)
- Acceptance Criteria
- Dependencies
- Risks & Assumptions
- Technical Considerations
- Sizing & Effort
- Story Breakdown
- Test Plan link

## Examples

```
# Generate all Epics from PRD
/sdlc-studio epic

# Review Epic status after Stories complete
/sdlc-studio epic review

# Use custom PRD location
/sdlc-studio epic --prd ./docs/requirements.md

# Generate with engineering perspective (TRD-aligned)
/sdlc-studio epic --perspective engineering

# Generate with product perspective (PRD-aligned)
/sdlc-studio epic --perspective product

# Generate with test perspective (TSD-aligned)
/sdlc-studio epic --perspective test
```

## Next Steps

After generating Epics:
```
/sdlc-studio story                # Generate Stories from Epics
/sdlc-studio test-plan            # Generate Test Plans for Epics
```

## Naming Convention

- ID format: `EP0001`, `EP0002`, etc. (global numbering)
- Slug: kebab-case from title, max 50 chars
- Example: `EP0001-user-authentication.md`

## Workflow Commands

Automate the full implementation workflow for all stories in an epic.

### plan

Preview the implementation workflow for all stories in an epic.

```
/sdlc-studio epic plan --epic EP0004
```

**What happens:**
1. Lists all stories in epic with status
2. Filters to stories that need implementation (Ready, not Done)
3. Analyses cross-story dependencies
4. Determines execution order (topological sort)
5. Shows aggregate work preview

**Output:**
```
## Epic Workflow Plan: EP0004

**Epic:** Agent Execution Engine
**Stories:** 8 total (3 Done, 5 Ready)

### Execution Order

| Order | Story | Title | Dependencies | Approach |
|-------|-------|-------|--------------|----------|
| 1 | US0023 | Config Schema | None | TDD |
| 2 | US0024 | Action Queue API | US0023 | TDD |
| 3 | US0025 | Script Parser | US0023 | TDD |
| 4 | US0026 | Action Executor | US0024, US0025 | TDD |
| 5 | US0027 | Agent Runner | US0026 | Test-After |

### Summary
- **Stories to implement:** 5
- **TDD stories:** 4
- **Test-After stories:** 1
- **Estimated phases:** 40 (8 per story)

### Dependency Graph
US0023 --+-- US0024 --+-- US0026 -- US0027
         +-- US0025 --+

Ready to execute? Run: /sdlc-studio epic implement --epic EP0004
```

### implement

Execute the full implementation workflow for all stories in an epic.

```
/sdlc-studio epic implement --epic EP0004
/sdlc-studio epic implement --epic EP0004 --story US0024
/sdlc-studio epic implement --epic EP0004 --skip US0025
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--epic EP000X` | Target epic (required) |
| `--story US000X` | Start from specific story |
| `--skip US000X` | Skip specific story |

**What happens:**
1. Loads or creates epic workflow plan
2. Processes stories in dependency order
3. Runs `story implement` for each story
4. Tracks overall progress
5. Pauses on story failure with resume capability
6. Updates epic status on completion

**State tracking:**
Creates `sdlc-studio/workflows/WF{NNNN}-{epic-slug}.md` to track progress.

**Story execution:**

For each story in dependency order:
1. Check dependencies are Done
2. Run `story implement --story US000X`
3. On success: mark story Done, continue to next
4. On failure: pause epic workflow, save state

**Resume after pause:**
```
/sdlc-studio epic implement --epic EP0004 --story US0024
```

## See Also

**REQUIRED for this workflow:**
- `reference-epic.md` - Epic workflow details including workflow orchestration

**Recommended:**
- `/sdlc-studio prd help` - Product requirements (upstream)
- `/sdlc-studio story help` - User Stories (downstream)

**Optional (deep dives):**
- `reference-outputs.md` - Output formats reference
- `/sdlc-studio story plan help` - Plan workflow for single story
