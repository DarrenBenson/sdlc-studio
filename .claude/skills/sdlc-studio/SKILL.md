---
name: sdlc-studio
description: /sdlc-studio [type] [action] - Manage specifications and test artifacts. Types: prd, trd, epic, story, persona, bug, test-strategy, test-spec, test-automation, code, test, status, migrate, init, hint. Use when user wants to create/update PRDs, TRDs, generate epics, stories, track bugs, test artifacts, or plan/review code.
allowed-tools: Read, Glob, Grep, Write, Edit, Task, AskUserQuestion
---

# SDLC Studio

Manage project specifications and test artifacts. Supports the full pipeline from PRD creation through Epic decomposition, User Story generation, and streamlined test automation.

## Quick Start

```
/sdlc-studio help                    # Show command reference
/sdlc-studio status                  # Check pipeline state and next steps
/sdlc-studio prd generate            # Create PRD from codebase
/sdlc-studio trd generate            # Create TRD from codebase
/sdlc-studio epic                    # Generate Epics from PRD
/sdlc-studio story                   # Generate Stories from Epics
/sdlc-studio bug                     # Create or list bugs
/sdlc-studio code plan               # Plan implementation for story
/sdlc-studio code implement          # Execute implementation plan
/sdlc-studio code review             # Review code against AC
/sdlc-studio code check              # Run linters and checks
/sdlc-studio test                    # Run tests with traceability
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
/sdlc-studio bug help                # Bug tracking help
/sdlc-studio code help               # Code plan/review/check help
/sdlc-studio test help               # Test runner help
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
- "Create a TRD for this project"
- "Generate technical requirements from this codebase"
- "Generate epics from the PRD"
- "Create user stories from the epics"
- "Create personas for this project"
- "Report a bug I found"
- "List all open bugs"
- "Fix this bug"
- "Plan the implementation for this story"
- "Implement the plan for this story"
- "Implement this story with TDD"
- "Check my code quality"
- "Review my code against acceptance criteria"
- "Run the tests for this epic"
- "Generate test specifications"
- "Create automated tests from specs"
- "What's the current status of my specs?"
- `/sdlc-studio prd`, `/sdlc-studio trd`, `/sdlc-studio epic`, `/sdlc-studio story`, `/sdlc-studio persona`
- `/sdlc-studio bug`, `/sdlc-studio bug list`, `/sdlc-studio bug fix`, `/sdlc-studio bug verify`, `/sdlc-studio bug close`
- `/sdlc-studio code plan`, `/sdlc-studio code implement`, `/sdlc-studio code review`, `/sdlc-studio code check`
- `/sdlc-studio test`, `/sdlc-studio test-strategy`, `/sdlc-studio test-spec`, `/sdlc-studio test-automation`
- `/sdlc-studio status`, `/sdlc-studio migrate`

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `type` | See Type Reference below | Required |
| `action` | create, generate, update, plan, review, check, list, fix, verify, close, **help** | varies |
| `--output` | Output path (file or directory) | varies by type |
| `--prd` | PRD file path (for epic) | sdlc-studio/prd.md |
| `--epic` | Specific epic ID | all epics |
| `--story` | Specific story ID | auto-select |
| `--bug` | Specific bug ID | auto-select |
| `--severity` | Bug severity filter (critical, high, medium, low) | all |
| `--spec` | Specific test spec ID (for test-automation) | all specs |
| `--type` | Test type filter (unit, integration, api, e2e) | all types |
| `--framework` | Override framework detection | auto-detect |
| `--personas` | Personas file path | sdlc-studio/personas.md |
| `--force` | Overwrite existing files | false |
| `--no-fix` | Report without auto-fixing (code check) | false |
| `--verbose` | Detailed test output | false |
| `--plan` | Specific plan ID (for implement) | auto-select |
| `--tdd` | Force TDD mode (for implement) | plan recommendation |
| `--no-tdd` | Force Test-After mode (for implement) | plan recommendation |
| `--docs` | Update documentation (for implement) | true |
| `--no-docs` | Skip documentation updates (for implement) | false |

## Type Reference

| Type | Description |
|------|-------------|
| `help` | Show command reference and examples |
| `status` | Show pipeline state and next steps |
| `prd` | Product Requirements Document |
| `trd` | Technical Requirements Document |
| `epic` | Feature groupings (Epics) |
| `story` | User Stories with acceptance criteria |
| `persona` | User Personas |
| `bug` | Bug tracking and traceability |
| `code` | Implementation planning and quality |
| `test` | Run tests with traceability |
| `test-strategy` | Project-level test strategy |
| `test-spec` | Consolidated test specification (plan + cases + fixtures) |
| `test-automation` | Generate executable test code |
| `migrate` | Migrate from old format (test-plan/suite/case) |
| `init` | Bootstrap pipeline (auto-detect brownfield/greenfield) |
| `hint` | Single actionable next step |

## Command Reference

### Pipeline Status

| Command | Description |
|---------|-------------|
| `/sdlc-studio status` | Show full pipeline state |
| `/sdlc-studio status --testing` | Show testing pipeline only |
| `/sdlc-studio status --brief` | One-line summary |

### Project Setup

| Command | Description |
|---------|-------------|
| `/sdlc-studio init` | Auto-detect and bootstrap pipeline |
| `/sdlc-studio init --brownfield` | Force existing project mode |
| `/sdlc-studio init --skip-tests` | Skip test artifact generation |
| `/sdlc-studio hint` | Get single actionable next step |

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

### Technical Requirements

| Command | Description |
|---------|-------------|
| `/sdlc-studio trd` | Ask which mode (create/generate/update) |
| `/sdlc-studio trd create` | Interactive TRD creation |
| `/sdlc-studio trd generate` | Reverse-engineer TRD from codebase |
| `/sdlc-studio trd update` | Update TRD with implementation changes |

### Bug Tracking

| Command | Description |
|---------|-------------|
| `/sdlc-studio bug` | Create new bug (interactive) |
| `/sdlc-studio bug create` | Create bug report |
| `/sdlc-studio bug list` | List all bugs |
| `/sdlc-studio bug list --status open` | List open bugs |
| `/sdlc-studio bug list --severity critical` | List critical bugs |
| `/sdlc-studio bug list --epic EP0001` | List bugs for epic |
| `/sdlc-studio bug fix --bug BG0001` | Start fixing a bug |
| `/sdlc-studio bug verify --bug BG0001` | Verify bug fix |
| `/sdlc-studio bug close --bug BG0001` | Close a bug |
| `/sdlc-studio bug reopen --bug BG0001` | Reopen a closed bug |

### Development Pipeline

| Command | Description |
|---------|-------------|
| `/sdlc-studio code plan` | Plan next incomplete story |
| `/sdlc-studio code plan --story US0001` | Plan specific story |
| `/sdlc-studio code plan --epic EP0001` | Plan next story in epic |
| `/sdlc-studio code implement` | Implement next planned story |
| `/sdlc-studio code implement --plan PL0001` | Implement specific plan |
| `/sdlc-studio code implement --story US0001` | Implement by story |
| `/sdlc-studio code implement --tdd` | Force TDD mode |
| `/sdlc-studio code implement --no-docs` | Skip doc updates |
| `/sdlc-studio code review` | Review next In Progress story |
| `/sdlc-studio code review --story US0001` | Review specific story |
| `/sdlc-studio code check` | Run linters with auto-fix |
| `/sdlc-studio code check --no-fix` | Check only, no changes |
| `/sdlc-studio test` | Run all tests |
| `/sdlc-studio test --epic EP0001` | Run tests for specific epic |
| `/sdlc-studio test --story US0001` | Run tests for specific story |
| `/sdlc-studio test --type unit` | Run only unit tests |

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

## Workflows

For detailed step-by-step workflows, see reference files:
- `reference.md` - PRD, TRD, Epic, Story, Persona workflows
- `reference-code.md` - Code plan, implement, review, check, test workflows
- `reference-testing.md` - Test Strategy, Test Spec, Test Automation, Migrate workflows

---

## Output Formats

| Type | Location | Status Values |
|------|----------|---------------|
| PRD | `sdlc-studio/prd.md` | Feature status markers |
| TRD | `sdlc-studio/trd.md` | Draft/Approved |
| Epic | `sdlc-studio/epics/EP{NNNN}-*.md` | Draft/Ready/Approved/In Progress/Done |
| Story | `sdlc-studio/stories/US{NNNN}-*.md` | Draft/Ready/Planned/In Progress/Review/Done |
| Plan | `sdlc-studio/plans/PL{NNNN}-*.md` | Draft/In Progress/Complete |
| Bug | `sdlc-studio/bugs/BG{NNNN}-*.md` | Open/In Progress/Fixed/Verified/Closed/Won't Fix |
| Persona | `sdlc-studio/personas.md` | - |
| Test Strategy | `sdlc-studio/testing/strategy.md` | - |
| Test Spec | `sdlc-studio/testing/specs/TSP{NNNN}-*.md` | Draft/Ready/In Progress/Complete |
| Test Code | `tests/` | - |

Each type with `{NNNN}` also has an `_index.md` registry.

## Examples

```
# Requirements
/sdlc-studio prd generate             /sdlc-studio prd create
/sdlc-studio epic                     /sdlc-studio story --epic EP0001

# Bugs
/sdlc-studio bug                      /sdlc-studio bug list --status open
/sdlc-studio bug fix --bug BG0001     /sdlc-studio bug verify --bug BG0001

# Development
/sdlc-studio code plan --story US0001 /sdlc-studio code implement
/sdlc-studio code implement --tdd     /sdlc-studio code implement --no-docs
/sdlc-studio code review              /sdlc-studio test --story US0001
/sdlc-studio code check

# Testing
/sdlc-studio test-spec --epic EP0001  /sdlc-studio test-automation
/sdlc-studio migrate --execute        /sdlc-studio status
```

See `help/{type}.md` for full examples per type.

## Error Handling

**Missing prerequisites:** Prompts to run earlier pipeline step (e.g., no PRD → `prd`, no epics → `epic`, no stories → `story`, no plans → `code plan`). **Existing files:** Warns and asks to continue unless `--force`. **No type:** Asks user which type. **ID collision:** Auto-increments. **Open questions:** Reports and pauses. **Unknown language:** Asks user to specify framework.

## Typical Workflow

### Full Pipeline
```
prd → trd → persona → epic → story → code plan → code implement → code review → test
```

### Development Cycle
```
code plan → code implement → code check → code review → test
```
Status: `Draft/Ready → Planned → In Progress → Review → Done`

### Daily Usage
```
/sdlc-studio status          # What needs attention?
/sdlc-studio code plan       # Plan next story
/sdlc-studio code implement  # Execute plan
```

## See Also

**Help:** `help/help.md` (main), `help/{type}.md` (type-specific)

**References:** `reference.md` (PRD, Epic, Story, Persona), `reference-code.md` (Code, Test), `reference-testing.md` (Test artifacts)

**Templates:** `templates/prd-template.md`, `trd-template.md`, `epic-template.md`, `story-template.md`, `personas-template.md`, `definition-of-done-template.md`, `plan-template.md`, `plan-index-template.md`, `bug-template.md`, `bug-index-template.md`, `test-strategy-template.md`, `test-spec-template.md`, `automation/*.template`
