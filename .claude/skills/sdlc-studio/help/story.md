<!--
Load: On /sdlc-studio story or /sdlc-studio story help
Dependencies: SKILL.md (always loaded first)
Related: reference-story.md (deep workflow), reference-philosophy.md (create vs generate), templates/story-template.md
-->

# /sdlc-studio story - User Stories

## Quick Reference

```
/sdlc-studio story                  # Generate Stories from Epics (default)
/sdlc-studio story --epic EP0001    # Generate for specific Epic
/sdlc-studio story generate         # Extract detailed specs from CODE
/sdlc-studio story generate --epic EP0002  # Extract for specific Epic
/sdlc-studio story review           # Review Story status
/sdlc-studio story plan --story US0024     # Preview workflow for story
/sdlc-studio story implement --story US0024  # Execute full workflow
```

## Two Modes: Understand the Difference

| Command | Input | Purpose |
|---------|-------|---------|
| `story` | Epics | Forward-looking planning from requirements |
| `story generate` | **Codebase** | Extract testable specification from existing code |

**`story generate` is for brownfield specification extraction.**

The output must be detailed enough that another team could rebuild the system without seeing the original code. This is a **migration blueprint**, not documentation.

See `reference-philosophy.md` for the complete philosophy.

## Prerequisites

- Epics must exist in `sdlc-studio/epics/`
- Personas must exist at `sdlc-studio/personas.md`
- Run `/sdlc-studio epic` and `/sdlc-studio persona` first if missing

## Actions

### (default) - Generate from Epics

Break Epic acceptance criteria into atomic User Stories.

**What happens:**
1. Checks for Epics and Personas (creates persona template if missing)
2. Creates Definition of Done if not exists
3. For each Epic, identifies distinct user actions
4. Generates Stories with Given/When/Then acceptance criteria
5. Updates Epic files with Story links
6. Creates `sdlc-studio/stories/_index.md` registry

**Breakdown heuristics:**
- One story per distinct user action
- Stories completable in one sprint
- Split by persona when multiple involved

### generate - Extract from Codebase

Reverse-engineer detailed specifications from actual code behaviour.

**When to use:**
- Existing functionality with no/poor documentation
- Legacy code that needs to be understood before migration
- Preparing for major refactor or technology change
- Creating a specification that could rebuild the system

**What happens:**
1. Reads the Epic to understand scope
2. Explores the codebase to find implementing code
3. Analyses actual:
   - API endpoints and their contracts
   - Validation rules and error messages
   - Edge cases and error handling
   - Data transformations
   - Business logic
4. Generates Stories with **implementation-ready** detail:
   - Precise Given/When/Then with actual values
   - Exhaustive edge case tables
   - Exact API request/response shapes
   - Real error messages from code
5. Status set to **Ready** (not Done) - awaiting validation

**Quality requirements for generated stories:**
- AC detailed enough to implement without seeing original code
- All edge cases documented with specific inputs/outputs
- API contracts include exact request/response shapes
- No ambiguous language ("handles errors", "returns data")

### review

Review Story status based on codebase implementation.

**What happens:**
1. Reads all Stories and their acceptance criteria
2. Searches codebase for implementation evidence
3. Updates status and checks off completed criteria
4. Updates Definition of Done items

## Output

**Files:**
- `sdlc-studio/stories/US{NNNN}-{slug}.md` per Story
- `sdlc-studio/stories/_index.md` registry
- `sdlc-studio/personas.md` (created if missing)

**Status values:** Draft | Ready | Planned | In Progress | Review | Done

**Status rules for generate mode:**
- Generated stories start as **Ready** (not Done)
- **Done** requires validation: tests must pass against implementation
- Never auto-assign Done for brownfield
- User confirms Done only after test validation

**Story sections:**
- User Story (As a... I want... So that...)
- Context (persona reference, background)
- Acceptance Criteria (Given/When/Then)
- Scope
- UI/UX Requirements
- Technical Notes
- Edge Cases & Error Handling
- Test Scenarios
- Test Cases (links)
- Definition of Done
- Dependencies
- Estimation

## Examples

```
# Forward-looking: Generate Stories from Epics
/sdlc-studio story
/sdlc-studio story --epic EP0001

# Specification extraction: Generate from codebase
/sdlc-studio story generate --epic EP0002

# Review status after implementation
/sdlc-studio story review
```

## Acceptance Criteria Quality

### Bad (documentation-style)
```
### AC1: Search works
- Given a user searches
- When they enter a query
- Then results are returned
```

### Good (specification-style)
```
### AC1: Search returns ranked results by relevance
- Given the index contains engrams with slugs "alice-smith", "bob-jones", "alice-wong"
- When I GET /search?q=alice
- Then I receive results with alice-smith and alice-wong
- And alice-smith has match_score >= 0.9 (exact slug match)
- And results are sorted by match_score descending
- And each result includes slug, name, role, category, match_score, matched_field
```

The good version can be implemented by someone who has never seen the original code.

## Edge Case Documentation

For generate mode, edge cases must be exhaustive:

| Scenario | Input | Expected Output |
|----------|-------|-----------------|
| Query too short | `q=a` | 422, `{"detail": "ensure this value has at least 2 characters"}` |
| No matches | `q=zzzznotfound` | 200, `[]` |
| Special characters | `q=o'brien` | 200, matches o'brien |
| Limit exceeded | `limit=500` | Silently capped at 100 |

## Test-Spec Timing: TDD vs Test-After

Choose **per story** whether to use TDD (test-first) or Test-After (code-first).

> **Decision tree:** `reference-decisions.md` → TDD vs Test-After Decision Tree

Both paths produce the same artifacts, just in different order.

## Validation Pipeline (Brownfield)

For generate mode, stories are not complete until validated:

```
story generate → test-spec → test-automation → test (MUST PASS)
```

Only mark stories as Done when tests pass against the existing implementation.

## Story Format

```markdown
**As a** {persona name}
**I want** {capability}
**So that** {benefit}
```

## Acceptance Criteria Format

```markdown
### AC1: {name}
- **Given** {precondition}
- **When** {action}
- **Then** {expected outcome}
```

## Next Steps

After generating Stories:
```
/sdlc-studio test-spec --epic EP0002   # Generate test specifications
/sdlc-studio test-automation           # Generate executable tests
/sdlc-studio code test --epic EP0002   # VALIDATE - tests must pass
```

## Naming Convention

- ID format: `US0001`, `US0002`, etc. (global, not per-Epic)
- Global numbering allows Stories to move between Epics
- Slug: kebab-case from title

## Ready Status Criteria

> **Source of truth:** `reference-decisions.md` → Story Ready

A story can be marked **Ready** when:

| Criterion | Check |
|-----------|-------|
| AC format | All AC in Given/When/Then with concrete values |
| No placeholders | No TBD or placeholder text in AC |
| Persona valid | Referenced persona exists in personas.md |
| Edge cases | Minimum 8 for API stories, 5 for others |
| No ambiguity | No "should", "might", "handles errors" language |
| Open Questions | All critical questions resolved |
| Dependencies | Identified with status |

**Blocking conditions:**
- TBD in acceptance criteria
- Edge case count below minimum
- Ambiguous language detected (see `reference-decisions.md`)
- Critical Open Question unresolved

## Cross-Story Dependency Detection

Story generation automatically detects dependencies:

| Detection | Source |
|-----------|--------|
| Schema dependencies | Config schemas, data models defined in other stories |
| API dependencies | Endpoints consumed that are defined in other stories |
| Service dependencies | Functions/services defined in other stories |

**Warning system:** If a dependent story is not Done, the story template shows a warning:
```
> **Warning:** This story depends on stories that are not Done:
> - US0013: Slack Notifications (In Progress)
```

## Workflow Commands

Automate the full implementation workflow for a single story.

### plan

Preview the full implementation workflow for a story.

```
/sdlc-studio story plan --story US0024
```

**What happens:**
1. Validates story is Ready (all AC in Given/When/Then, no TBD, edge cases complete)
2. Checks story dependencies (warns if blocking stories not Done)
3. Determines TDD vs Test-After approach (using decision tree from reference-decisions.md)
4. Creates implementation plan (code plan)
5. Creates test specification (test-spec)
6. Shows execution preview with phases

**Output:**
```
## Story Workflow Plan: US0024

**Story:** Action Queue API Endpoint
**Status:** Ready
**Dependencies:** US0023 (Done)

### Approach: TDD
Reason: API story with >5 edge cases, clear AC

### Execution Phases

| Phase | Command | Artifacts |
|-------|---------|-----------|
| 1. Plan | code plan | PL0024-action-queue-api.md |
| 2. Test Spec | test-spec | TS0024-action-queue-api.md |
| 3. Tests | test-automation | tests/test_action_queue_api.py |
| 4. Implement | code implement | src/api/action_queue.py |
| 5. Test | code test | Run tests |
| 6. Verify | code verify | Verify against AC |
| 7. Check | code check | Quality gates |

Ready to execute? Run: /sdlc-studio story implement --story US0024
```

### implement

Execute the full implementation workflow for a story.

```
/sdlc-studio story implement --story US0024
/sdlc-studio story implement --story US0024 --tdd
/sdlc-studio story implement --story US0024 --from-phase 3
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--story US000X` | Target story (required) |
| `--from-phase N` | Resume from specific phase (1-7) |
| `--tdd` | Force TDD mode |
| `--no-tdd` | Force Test-After mode |

**What happens:**
1. Loads or creates workflow plan
2. Executes each phase sequentially
3. Tracks progress in workflow state file
4. Pauses on errors with resume capability
5. Updates story status on completion

**State tracking:**
Creates `sdlc-studio/workflows/WF{NNNN}-{story-slug}.md` to track progress.

**Phase execution:**

| Phase | Command Run | On Success | On Failure |
|-------|-------------|------------|------------|
| 1 | `code plan` | Continue | Pause |
| 2 | `test-spec` | Continue | Pause |
| 3 | `test-automation` | Continue | Pause |
| 4 | `code implement` | Continue | Pause |
| 5 | `test` | Continue | Pause |
| 6 | `code verify` | Continue | Pause |
| 7 | `code check` | Complete | Pause |

**CRITICAL for Phase 4:** `code implement` must complete ALL implementation phases from the plan (backend, frontend, integration, etc.) before moving to Phase 5. Do NOT pause to ask questions mid-implementation.

**Resume after pause:**
```
/sdlc-studio story implement --story US0024 --from-phase 5
```

## See Also

- `reference-philosophy.md` - **Read first.** Create vs Generate philosophy
- `reference-decisions.md` - Ready criteria, dependency detection, decision guidance
- `reference-story.md` - Detailed story workflows including workflow orchestration
- `/sdlc-studio epic help` - Generate Epics (prerequisite)
- `/sdlc-studio epic plan` - Plan workflow for entire epic
- `/sdlc-studio persona help` - Define Personas (prerequisite)
- `/sdlc-studio test-spec help` - Generate Test Specs from Stories
