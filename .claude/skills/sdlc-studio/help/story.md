<!--
Load: On /sdlc-studio story or /sdlc-studio story help
Dependencies: SKILL.md (always loaded first)
Related: reference-story.md (deep workflow), reference-philosophy.md (create vs generate), templates/core/story.md
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

### Story Cohesion Review (Automatic)

After story generation, a cohesion review validates coverage of epic requirements.

**What it checks:** AC coverage, edge case distribution, dependency cycles, story sizing, overlaps.

**Auto-fixes:** Adds missing edge cases, flags sizing issues, reports gaps as open questions.

> **Full details:** See `reference-story.md#story-cohesion-review` for checks, output format, and auto-fix behaviour.

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

> **Source of truth:** See `reference-philosophy.md#ac-implementation-ready` for bad vs good AC patterns with detailed examples.

**Key principle:** Good AC can be implemented by someone who has never seen the original code. Avoid documentation-style ("search works") in favour of specification-style (exact inputs, outputs, values).

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

## Formats

**Story:** `As a {persona} I want {capability} So that {benefit}`

**AC:** `Given {precondition} When {action} Then {outcome}`

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

Story generation automatically detects schema, API, and service dependencies between stories. Warnings are shown if dependent stories are not Done.

> **Details:** See `reference-story.md#story-workflow` step 3b for detection logic and warning format.

## Workflow Commands

Automate the full implementation workflow for a single story.

### plan

Preview the full implementation workflow for a story.

```
/sdlc-studio story plan --story US0024
```

**What happens:**
1. Validates story Ready criteria
2. Checks dependencies (warns if not Done)
3. Determines TDD vs Test-After approach
4. Creates plan and test spec
5. Shows 8-phase execution preview

> **Full workflow details:** See `reference-story.md#story-plan-workflow`

### implement

Execute the full implementation workflow for a story.

```
/sdlc-studio story implement --story US0024
/sdlc-studio story implement --story US0024 --from-phase 3
```

| Flag | Description |
|------|-------------|
| `--story US000X` | Target story (required) |
| `--from-phase N` | Resume from specific phase (1-8) |
| `--tdd` / `--no-tdd` | Force TDD or Test-After mode |

**8 phases:** Plan → Test Spec → Tests → Implement → Test → Verify → Check → Review

**CRITICAL:** `code implement` (Phase 4) must complete ALL plan phases before continuing.

> **Full workflow details:** See `reference-story.md#story-implement-workflow`

## See Also

**REQUIRED for this workflow:**
- `reference-story.md` - Story workflow details including workflow orchestration
- `reference-decisions.md#story-ready` - Ready status criteria

**Recommended:**
- `/sdlc-studio epic help` - Generate Epics (upstream)
- `/sdlc-studio code plan help` - Implementation planning (downstream)

**Optional (deep dives):**
- `reference-philosophy.md` - Create vs Generate philosophy
- `reference-outputs.md` - Output formats reference
- `/sdlc-studio epic plan help` - Plan workflow for entire epic
