---
name: sdlc-studio
description: /sdlc-studio [type] [action] - Manage specifications and test artifacts. Types: prd, epic, story, persona, test-strategy, test-spec, test-automation, status, migrate. Use when user wants to create/update PRDs, generate epics, stories, or test artifacts.
allowed-tools: Read, Glob, Grep, Write, Edit, Task, AskUserQuestion
---

# SDLC Studio

Manage project specifications and test artifacts. Supports the full pipeline from PRD creation through Epic decomposition, User Story generation, and streamlined test automation.

## Quick Start

```
/sdlc-studio help                    # Show command reference
/sdlc-studio status                  # Check pipeline state and next steps
/sdlc-studio prd generate            # Create PRD from codebase
/sdlc-studio epic                    # Generate Epics from PRD
/sdlc-studio story                   # Generate Stories from Epics
/sdlc-studio test-strategy           # Create test strategy
/sdlc-studio test-spec               # Generate test specifications
/sdlc-studio test-automation         # Generate executable tests
```

## Get Help for Any Type

```
/sdlc-studio {type} help             # Show help for specific type
```

Examples:
```
/sdlc-studio prd help                # PRD commands and options
/sdlc-studio epic help               # Epic generation help
/sdlc-studio test-spec help          # Test specification help
/sdlc-studio test-automation help    # Test automation help
```

Each help page shows:
- Available actions and what they do
- Prerequisites
- Output format and location
- Examples
- Next steps

## When to Use

- "Create a PRD for this project"
- "Generate requirements from this codebase"
- "Generate epics from the PRD"
- "Create user stories from the epics"
- "Create personas for this project"
- "Generate test specifications"
- "Create automated tests from specs"
- "What's the current status of my specs?"
- `/sdlc-studio prd`, `/sdlc-studio epic`, `/sdlc-studio story`, `/sdlc-studio persona`
- `/sdlc-studio test-strategy`, `/sdlc-studio test-spec`, `/sdlc-studio test-automation`
- `/sdlc-studio status`, `/sdlc-studio migrate`

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `type` | See Type Reference below | Required |
| `action` | create, generate, update, **help** (varies by type) | varies |
| `--output` | Output path (file or directory) | varies by type |
| `--prd` | PRD file path (for epic) | sdlc-studio/prd.md |
| `--epic` | Specific epic ID | all epics |
| `--spec` | Specific test spec ID (for test-automation) | all specs |
| `--type` | Test type filter (unit, integration, api, e2e) | all types |
| `--framework` | Override framework detection | auto-detect |
| `--personas` | Personas file path | sdlc-studio/personas.md |
| `--force` | Overwrite existing files | false |

## Type Reference

| Type | Description |
|------|-------------|
| `help` | Show command reference and examples |
| `status` | Show pipeline state and next steps |
| `prd` | Product Requirements Document |
| `epic` | Feature groupings (Epics) |
| `story` | User Stories with acceptance criteria |
| `persona` | User Personas |
| `test-strategy` | Project-level test strategy |
| `test-spec` | Consolidated test specification (plan + cases + fixtures) |
| `test-automation` | Generate executable test code |
| `migrate` | Migrate from old format (test-plan/suite/case) |

## Command Reference

### Pipeline Status

| Command | Description |
|---------|-------------|
| `/sdlc-studio status` | Show full pipeline state |
| `/sdlc-studio status --testing` | Show testing pipeline only |
| `/sdlc-studio status --brief` | One-line summary |

### Requirements Pipeline

| Command | Description |
|---------|-------------|
| `/sdlc-studio help` | Show command reference and examples |
| `/sdlc-studio prd` | Ask which mode (create/generate/update) |
| `/sdlc-studio prd create` | Interactive PRD creation |
| `/sdlc-studio prd generate` | Reverse-engineer PRD from codebase |
| `/sdlc-studio prd update` | Update feature implementation status |
| `/sdlc-studio epic` | Generate Epics from PRD |
| `/sdlc-studio epic update` | Update Epic status from codebase |
| `/sdlc-studio story` | Generate User Stories from Epics |
| `/sdlc-studio story update` | Update Story status from codebase |
| `/sdlc-studio persona` | Interactive persona creation |
| `/sdlc-studio persona generate` | Infer personas from codebase |
| `/sdlc-studio persona update` | Refine existing personas |

### Testing Pipeline

| Command | Description |
|---------|-------------|
| `/sdlc-studio test-strategy` | Create project test strategy |
| `/sdlc-studio test-strategy generate` | Infer strategy from codebase |
| `/sdlc-studio test-strategy update` | Update strategy |
| `/sdlc-studio test-spec` | Generate test specs from epics/stories |
| `/sdlc-studio test-spec --epic EP0001` | Generate for specific Epic |
| `/sdlc-studio test-spec generate` | Reverse-engineer from existing tests |
| `/sdlc-studio test-spec update` | Sync automation status |
| `/sdlc-studio test-automation` | Generate executable tests |
| `/sdlc-studio test-automation --spec TSP0001` | Generate for specific spec |
| `/sdlc-studio test-automation --type unit` | Generate only unit tests |
| `/sdlc-studio migrate` | Preview migration from old format |
| `/sdlc-studio migrate --execute` | Execute migration |

## Instructions

For detailed step-by-step workflows, see `reference.md`.

### Type: STATUS

**Actions:** (default)

**Output:** Console output

Shows current pipeline state including:
- Requirements progress (PRD, Personas, Epics, Stories)
- Testing progress (Strategy, Specs, Automation coverage)
- Recommended next steps

### Type: PRD

**Actions:** create, generate, update

**Output:** `sdlc-studio/prd.md`

| Action | Summary |
|--------|---------|
| create | Guided conversation to build PRD from scratch |
| generate | Explore codebase and reverse-engineer requirements |
| update | Compare PRD against codebase, update feature status |

**Workflow summary:**
1. Gather context (user input or codebase exploration)
2. Extract/define features with acceptance criteria
3. Document non-functional requirements
4. Write PRD using `templates/prd-template.md`
5. Use confidence markers: [HIGH], [MEDIUM], [LOW], [UNKNOWN]

### Type: EPIC

**Actions:** generate (default), update

**Output:** `sdlc-studio/epics/EP{NNNN}-{slug}.md`

**Prerequisites:** PRD must exist at `sdlc-studio/prd.md`

**Workflow summary:**
1. Parse PRD Feature Inventory
2. Group related features into Epics (max 5-8 features per Epic)
3. Generate Epic files using `templates/epic-template.md`
4. Create `sdlc-studio/epics/_index.md` registry

**Grouping heuristics:**
- Features sharing user type → same Epic
- Features with shared dependencies → same Epic
- Features forming complete user journey → same Epic

### Type: STORY

**Actions:** generate (default), update

**Output:** `sdlc-studio/stories/US{NNNN}-{slug}.md`

**Prerequisites:**
- Epics must exist in `sdlc-studio/epics/`
- Personas must exist at `sdlc-studio/personas.md` (creates template if missing)

**Workflow summary:**
1. Check prerequisites (epics, personas, DoD)
2. For each Epic, break acceptance criteria into atomic stories
3. Generate Story files using `templates/story-template.md`
4. Update Epic files with story links
5. Create `sdlc-studio/stories/_index.md` registry

**Breakdown heuristics:**
- One story per distinct user action
- Stories completable in one sprint
- Split by persona when multiple involved

### Type: PERSONA

**Actions:** create (default), generate, update

**Output:** `sdlc-studio/personas.md`

| Action | Summary |
|--------|---------|
| create | Guided conversation to define personas |
| generate | Infer personas from codebase (roles, permissions, UI) |
| update | Refine existing personas with new information |

**Workflow summary:**
1. Gather persona details (name, role, goals, pain points)
2. Recommend 3-5 personas per project
3. Write using `templates/personas-template.md`

---

## Testing Types

For detailed testing workflows, see `reference-testing.md`.

### Type: TEST-STRATEGY

**Actions:** create (default), generate, update

**Output:** `sdlc-studio/testing/strategy.md`

**Prerequisites:** PRD should exist

| Action | Summary |
|--------|---------|
| create | Guided conversation to define test strategy |
| generate | Infer strategy from codebase testing patterns |
| update | Update strategy based on changes |

**Workflow summary:**
1. Define test objectives and scope
2. Specify test levels (unit, integration, E2E)
3. Document automation strategy and quality gates
4. Write using `templates/test-strategy-template.md`

### Type: TEST-SPEC

**Actions:** generate (default), update

**Output:** `sdlc-studio/testing/specs/TSP{NNNN}-{slug}.md`

**Prerequisites:**
- Test Strategy should exist
- Epics must exist in `sdlc-studio/epics/`

| Action | Summary |
|--------|---------|
| (default) | Generate from epics/stories (greenfield) |
| generate | Reverse-engineer from existing tests (brownfield) |
| update | Sync spec status with codebase |

**Workflow summary:**
1. Parse Epic(s) to process
2. Generate consolidated test spec per Epic
3. Include test cases with Given/When/Then steps
4. Embed fixtures as YAML
5. Create `sdlc-studio/testing/specs/_index.md` registry

### Type: TEST-AUTOMATION

**Actions:** generate (default)

**Output:** `tests/` (framework-specific location)

**Prerequisites:** Test specs must exist in `sdlc-studio/testing/specs/`

**Language Detection:**
1. `pyproject.toml` → Python (pytest)
2. `package.json` + vitest → TypeScript (Vitest)
3. `package.json` → TypeScript (Jest)
4. `go.mod` → Go (testing)
5. `Cargo.toml` → Rust (cargo test)

**Workflow summary:**
1. Parse test spec files
2. Detect language and framework
3. Generate test files using appropriate template
4. Update spec with automation status

### Type: MIGRATE

**Actions:** (default), execute

**Output:** `sdlc-studio/testing/specs/` + `.archive/`

Migrates old test-plan/suite/case format to new test-spec format.

| Action | Summary |
|--------|---------|
| (default) | Preview migration plan |
| --execute | Perform migration |
| --backup | Create backup before migration |

**Workflow summary:**
1. Scan existing test artifacts
2. Group test cases by parent suite/plan
3. Create consolidated TSP files
4. Archive old files to `sdlc-studio/testing/.archive/`

---

## Output Formats

### PRD
- 14-section template with confidence markers
- Feature status: Complete | Partial | Stubbed | Broken | Not Started

### Epic
- `sdlc-studio/epics/EP{NNNN}-{slug}.md` per Epic
- `sdlc-studio/epics/_index.md` registry
- Status: Draft | Ready for Review | Approved | In Progress | Done

### Story
- `sdlc-studio/stories/US{NNNN}-{slug}.md` per Story
- `sdlc-studio/stories/_index.md` registry
- Status: Draft | Ready | In Progress | Review | Done
- Also creates: `sdlc-studio/personas.md`, `sdlc-studio/definition-of-done.md` if missing

### Persona
- Single `sdlc-studio/personas.md` with all personas
- Each persona has: name, role, proficiency, goals, needs, pain points, tasks, quote

### Test Strategy
- Single `sdlc-studio/testing/strategy.md`
- Project-level testing approach, levels, automation strategy

### Test Spec
- `sdlc-studio/testing/specs/TSP{NNNN}-{slug}.md` per Epic
- `sdlc-studio/testing/specs/_index.md` registry
- Consolidates: test plan + test cases + fixtures
- Status: Draft | Ready | In Progress | Complete

### Test Automation
- Framework-specific test files in `tests/`
- Updates test spec with automation status

## Examples

```
# Status
/sdlc-studio status                   # Full pipeline state

# PRD
/sdlc-studio prd create               # Interactive creation
/sdlc-studio prd generate             # Reverse-engineer from code
/sdlc-studio prd update               # Update status

# Epic
/sdlc-studio epic                     # Generate from PRD
/sdlc-studio epic update              # Update status

# Story
/sdlc-studio story                    # Generate from epics
/sdlc-studio story --epic EP0001      # Specific epic only
/sdlc-studio story update             # Update status

# Persona
/sdlc-studio persona                  # Interactive creation
/sdlc-studio persona generate         # Infer from codebase
/sdlc-studio persona update           # Refine existing

# Testing
/sdlc-studio test-strategy            # Create test strategy
/sdlc-studio test-strategy generate   # Infer from codebase
/sdlc-studio test-spec                # Generate from all Epics
/sdlc-studio test-spec --epic EP0001  # Specific Epic only
/sdlc-studio test-spec generate       # Reverse-engineer from tests
/sdlc-studio test-automation          # Generate all pending tests
/sdlc-studio test-automation --spec TSP0001  # Specific spec only
/sdlc-studio test-automation --type unit     # Only unit tests

# Migration
/sdlc-studio migrate                  # Preview migration
/sdlc-studio migrate --execute        # Execute migration

# Help
/sdlc-studio help                     # Show this guide
```

## Error Handling

### Requirements Pipeline
- No type specified → ask user which type
- PRD exists without --force → warn and ask to continue
- `/sdlc-studio epic` but no PRD → prompt to run `/sdlc-studio prd` first
- `/sdlc-studio story` but no epics → prompt to run `/sdlc-studio epic` first
- `/sdlc-studio story` but no personas → create template, ask user to populate, stop
- ID collision → increment to next available

### Testing Pipeline
- `/sdlc-studio test-spec` but no epics → prompt to run `/sdlc-studio epic` first
- `/sdlc-studio test-automation` but no test specs → prompt to run `/sdlc-studio test-spec` first
- `--spec` with invalid ID → report error, list valid spec IDs
- Unknown language → ask user to specify framework

## Typical Workflow

### Greenfield Project

```
1. /sdlc-studio prd create            → Create PRD
2. Review PRD
3. /sdlc-studio persona               → Define personas
4. /sdlc-studio epic                  → Generate Epics
5. Review Epics
6. /sdlc-studio story                 → Generate Stories
7. /sdlc-studio test-strategy         → Define test approach
8. /sdlc-studio test-spec             → Generate test specs
9. /sdlc-studio test-automation       → Generate executable tests
```

### Brownfield Project

```
1. /sdlc-studio prd generate          → Reverse-engineer PRD
2. /sdlc-studio persona generate      → Infer personas
3. /sdlc-studio epic                  → Generate Epics
4. /sdlc-studio story                 → Generate Stories
5. /sdlc-studio test-strategy generate → Infer test strategy
6. /sdlc-studio test-spec generate    → Reverse-engineer from tests
7. /sdlc-studio test-automation       → Generate tests for gaps
```

### Daily Usage

```
/sdlc-studio status                   → Check what needs attention
/sdlc-studio test-automation          → Generate pending tests
```

## See Also

### Help Files
- `help/help.md` - Main help (shown with `/sdlc-studio help`)
- `help/{type}.md` - Type-specific help (shown with `/sdlc-studio {type} help`)

### Core References
- `reference.md` - Detailed workflows (PRD, Epic, Story, Persona)
- `reference-testing.md` - Detailed workflows (Test artifacts)

### Requirements Templates
- `templates/prd-template.md` - PRD template
- `templates/epic-template.md` - Epic template
- `templates/story-template.md` - Story template
- `templates/personas-template.md` - Personas template
- `templates/definition-of-done-template.md` - DoD template

### Testing Templates
- `templates/test-strategy-template.md` - Test strategy template
- `templates/test-spec-template.md` - Test specification template
- `templates/automation/*.template` - Framework-specific test templates
