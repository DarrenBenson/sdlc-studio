---
name: sdlc-studio
description: /sdlc-studio [type] [action] - SDLC pipeline: requirements, specifications, code, testing. Run /sdlc-studio help for commands and /sdlc-studio status for next steps.
allowed-tools: Read, Glob, Grep, Write, Edit, Task, AskUserQuestion
---

# SDLC Studio

Manage project specifications and test artifacts. Supports the full pipeline from PRD creation through Epic decomposition, User Story generation, and streamlined test automation.

## Create vs Generate: Know the Difference

| Mode | Purpose | Use When |
|------|---------|----------|
| **create** | Plan something new | Greenfield, new features |
| **generate** | Extract testable specification from existing code | Brownfield, migration, refactoring |

**Generate mode is NOT documentation.** It produces a **migration blueprint** - a specification detailed enough that another team could rebuild the system in a different technology stack. Generated specs MUST be validated by running tests against the existing implementation.

> **New to Create vs Generate?** Read `reference-philosophy.md` first - it explains why these modes exist and how they differ fundamentally.

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
/sdlc-studio code test               # Run tests with traceability
/sdlc-studio code verify             # Verify code against AC
/sdlc-studio code check              # Run linters and checks
/sdlc-studio tsd                      # Create test strategy document
/sdlc-studio test-spec               # Generate test specifications
/sdlc-studio test-automation         # Generate executable tests
/sdlc-studio story plan              # Preview story workflow
/sdlc-studio story implement         # Execute story workflow (all phases)
/sdlc-studio epic plan               # Preview epic workflow (all stories)
/sdlc-studio epic implement          # Execute epic workflow (all stories)
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
/sdlc-studio code help               # Code plan/test/verify/check help
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
- "Verify my code against acceptance criteria"
- "Run the tests for this epic" → `/sdlc-studio code test --epic EP0001`
- "Generate test specifications"
- "Create automated tests from specs"
- "What's the current status of my specs?"
- "Run the full workflow for this story"
- "Implement all stories in this epic"
- "Show me the workflow plan for US0024"
- `/sdlc-studio prd`, `/sdlc-studio trd`, `/sdlc-studio epic`, `/sdlc-studio story`, `/sdlc-studio persona`
- `/sdlc-studio bug`, `/sdlc-studio bug list`, `/sdlc-studio bug fix`, `/sdlc-studio bug verify`, `/sdlc-studio bug close`
- `/sdlc-studio code plan`, `/sdlc-studio code implement`, `/sdlc-studio code test`, `/sdlc-studio code verify`, `/sdlc-studio code check`
- `/sdlc-studio tsd`, `/sdlc-studio test-spec`, `/sdlc-studio test-automation`
- `/sdlc-studio story plan`, `/sdlc-studio story implement`, `/sdlc-studio epic plan`, `/sdlc-studio epic implement`
- `/sdlc-studio status`

## File Loading Guide

Claude loads files progressively - only what's needed for the current task.

**Loading hierarchy:**
```
Level 1: SKILL.md (Always loaded - "what can I do?")
    ↓
Level 2: help/{type}.md (On command - "how do I do X?")
    ↓
Level 3: reference-*.md (Deep workflow - "step-by-step for X")
    ↓
Level 4: templates/*.md (Creating artifacts - "what goes in the file?")
```

**Pattern-based loading:**

| When | Load |
|------|------|
| Any `/sdlc-studio {type}` command | help/{type}.md first |
| Executing multi-step workflow | Relevant reference-*.md |
| Creating/updating artifacts | Relevant template from templates/ |
| Validating Ready status | reference-decisions.md |
| Choosing TDD vs Test-After | reference-decisions.md |
| Enforcing edge case/AC coverage | reference-decisions.md |

**Reference file mapping:**

| Domain | Reference File |
|--------|----------------|
| PRD workflows | reference-prd.md |
| TRD workflows | reference-trd.md |
| Persona workflows | reference-persona.md |
| Epic workflows | reference-epic.md |
| Story workflows | reference-story.md |
| Bug workflows | reference-bug.md |
| Code plan/implement/verify/test/check | reference-code.md |
| TSD/test-spec/test-automation | reference-testing.md |
| Architecture decisions | reference-architecture.md |
| Cross-stage decisions, Ready criteria | reference-decisions.md |
| Create vs Generate philosophy | reference-philosophy.md |
| Test writing guidelines | reference-test-best-practices.md |
| E2E and mocking patterns | reference-test-e2e-guidelines.md |

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `type` | See Type Reference below | Required |
| `action` | create, generate, review, plan, verify, check, list, fix, close, **help** | varies |
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
| `--from-phase` | Resume workflow from phase N (for story implement) | 1 |
| `--skip` | Skip specific story (for epic implement) | none |

## Type Reference

| Type | Description |
|------|-------------|
| `prd` | Product Requirements Document |
| `trd` | Technical Requirements Document |
| `tsd` | Test Strategy Document (project-level) |
| `persona` | User Personas |
| `epic` | Feature groupings (Epics) |
| `story` | User Stories with acceptance criteria |
| `code` | Implementation planning, testing, and quality |
| `test-spec` | Consolidated test specification (plan + cases + fixtures) |
| `test-automation` | Generate executable test code |
| `bug` | Bug tracking and traceability |
| `status` | Show pipeline state and next steps |
| `hint` | Single actionable next step |
| `help` | Show command reference and examples |

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
| `/sdlc-studio hint` | Get single actionable next step |
| `/sdlc-studio help` | Show command reference and examples |
| `/sdlc-studio prd` | Ask which mode (create/generate/review) |
| `/sdlc-studio prd create` | Interactive PRD creation |
| `/sdlc-studio prd generate` | **Extract PRD from codebase** (brownfield) |
| `/sdlc-studio prd review` | Review PRD against codebase, update status |
| `/sdlc-studio epic` | Generate Epics from PRD |
| `/sdlc-studio epic review` | Review Epic status from codebase |
| `/sdlc-studio story` | Generate User Stories from Epics |
| `/sdlc-studio story generate` | **Extract detailed specs from CODE** (brownfield) |
| `/sdlc-studio story review` | Review Story status from codebase |
| `/sdlc-studio persona` | Ask which mode (create/generate/review) |
| `/sdlc-studio persona create` | Interactive persona creation |
| `/sdlc-studio persona generate` | **Infer personas from codebase** (brownfield) |
| `/sdlc-studio persona review` | Review and refine existing personas |

### Technical Requirements

| Command | Description |
|---------|-------------|
| `/sdlc-studio trd` | Ask which mode (create/generate/review) |
| `/sdlc-studio trd create` | Interactive TRD creation |
| `/sdlc-studio trd generate` | **Extract TRD from architecture** (brownfield) |
| `/sdlc-studio trd review` | Review TRD against implementation |

### Bug Tracking

| Command | Description |
|---------|-------------|
| `/sdlc-studio bug` | Create new bug (interactive) |
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
| `/sdlc-studio code verify` | Verify next In Progress story |
| `/sdlc-studio code verify --story US0001` | Verify specific story |
| `/sdlc-studio code test` | Run all tests |
| `/sdlc-studio code test --epic EP0001` | Run tests for specific epic |
| `/sdlc-studio code test --story US0001` | Run tests for specific story |
| `/sdlc-studio code test --type unit` | Run only unit tests |
| `/sdlc-studio code check` | Run linters with auto-fix |
| `/sdlc-studio code check --no-fix` | Check only, no changes |

### Testing Pipeline

| Command | Description |
|---------|-------------|
| `/sdlc-studio tsd` | Create test strategy document |
| `/sdlc-studio tsd generate` | Infer strategy from codebase |
| `/sdlc-studio tsd review` | Review and update strategy |
| `/sdlc-studio test-spec` | Generate test specs from epics/stories |
| `/sdlc-studio test-spec --epic EP0001` | Generate for specific Epic |
| `/sdlc-studio test-spec generate` | Reverse-engineer from existing tests |
| `/sdlc-studio test-spec review` | Sync automation status |
| `/sdlc-studio test-automation` | Generate executable tests |
| `/sdlc-studio test-automation --spec TS0001` | Generate for specific spec |
| `/sdlc-studio test-automation --type unit` | Generate only unit tests |

### Workflow Automation

| Command | Description |
|---------|-------------|
| `/sdlc-studio story plan --story US0001` | Preview story workflow |
| `/sdlc-studio story implement --story US0001` | Execute story workflow |
| `/sdlc-studio story implement --tdd` | Execute with TDD approach |
| `/sdlc-studio story implement --from-phase 3` | Resume from phase |
| `/sdlc-studio epic plan --epic EP0001` | Preview epic workflow |
| `/sdlc-studio epic implement --epic EP0001` | Execute epic workflow |
| `/sdlc-studio epic implement --story US0001` | Resume from story |
| `/sdlc-studio epic implement --skip US0001` | Skip specific story |

## Workflows

For detailed step-by-step workflows, see reference files:
- `reference-requirements.md` - PRD, TRD, Persona workflows
- `reference-specifications.md` - Epic, Story, Bug workflows
- `reference-code.md` - Code plan, implement, review, check, test workflows
- `reference-testing.md` - TSD, Test Spec, Test Automation workflows

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
| TSD | `sdlc-studio/tsd.md` | - |
| Test Spec | `sdlc-studio/test-specs/TS{NNNN}-*.md` | Draft/Ready/In Progress/Complete |
| Test Code | `tests/` | - |
| Workflow | `sdlc-studio/workflows/WF{NNNN}-*.md` | Created/Planning/Testing/Implementing/Verifying/Reviewing/Checking/Done/Paused |

Each type with `{NNNN}` also has an `_index.md` registry.

## Examples

```
# Requirements
/sdlc-studio prd generate             /sdlc-studio prd create
/sdlc-studio epic                     /sdlc-studio story --epic EP0001

# Bugs
/sdlc-studio bug                      /sdlc-studio bug list --status open
/sdlc-studio bug fix --bug BG0001     /sdlc-studio bug verify --bug BG0001

# Development (manual)
/sdlc-studio code plan --story US0001 /sdlc-studio code implement
/sdlc-studio code implement --tdd     /sdlc-studio code implement --no-docs
/sdlc-studio code test --story US0001 /sdlc-studio code verify
/sdlc-studio code check

# Workflow automation (recommended)
/sdlc-studio story plan --story US0001    /sdlc-studio story implement --story US0001
/sdlc-studio epic plan --epic EP0001      /sdlc-studio epic implement --epic EP0001
/sdlc-studio story implement --from-phase 3  # Resume from phase
/sdlc-studio epic implement --story US0002   # Resume from story

# Testing
/sdlc-studio test-spec --epic EP0001  /sdlc-studio test-automation
/sdlc-studio status
```

See `help/{type}.md` for full examples per type.

## Error Handling

**Missing prerequisites:** Prompts to run earlier pipeline step (e.g., no PRD → `prd`, no epics → `epic`, no stories → `story`, no plans → `code plan`). **Existing files:** Warns and asks to continue unless `--force`. **No type:** Asks user which type. **ID collision:** Auto-increments. **Open questions:** Reports and pauses. **Unknown language:** Asks user to specify framework.

## Typical Workflow

### Greenfield (Create Mode)
```
PRD → TRD → Personas → Epics → Stories
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
              TDD Path                    Test-After Path
              (test-first)                (code-first)
                    │                           │
              test-spec                    code plan
                    │                           │
              code plan                   code implement
                    │                           │
         code implement --tdd              test-spec
                    │                           │
              code verify                 test-automation
                    │                           │
              code test                     code verify
                                                │
                                            code test
```

**Per-story choice:** You choose TDD or Test-After for each story, not globally. Both paths produce the same artifacts, just in different order.

### Automated Workflow (Recommended)

For streamlined development, use workflow automation:

```
PRD → TRD → Personas → Epics → Stories
                                  │
                          story plan --story US0001
                                  │
                          story implement --story US0001
                                  │
                          (all 7 phases run automatically)
```

Or at the epic level:

```
PRD → TRD → Personas → Epics → Stories
                                  │
                          epic plan --epic EP0001
                                  │
                          epic implement --epic EP0001
                                  │
                          (all stories processed in dependency order)
```

**Workflow phases per story:**
1. Plan (code plan)
2. Test Spec (test-spec)
3. Tests (test-automation)
4. Implement (code implement)
5. Test (code test)
6. Verify (code verify)
7. Check (code check)

### Brownfield (Specification Extraction)
```
prd generate → trd generate → persona generate → epic → story generate → test-spec → test-automation → code test (VALIDATE)
```
**Critical:** The `code test` step validates specs against reality. Not optional.

### Development Cycle
```
code plan → code implement → code test → code verify → code check
```
Status: `Draft/Ready → Planned → In Progress → Review → Done`

### Daily Usage
```
/sdlc-studio status          # What needs attention?
/sdlc-studio code plan       # Plan next story
/sdlc-studio code implement  # Execute plan
```

## See Also

**Philosophy:** `reference-philosophy.md` - **Read this first.** Explains Create vs Generate modes and why generate mode produces migration blueprints, not documentation.

**Decisions:** `reference-decisions.md` - Decision impact matrix, TDD decision tree, Ready status criteria, cross-stage validation checkpoints.

**Help:** `help/help.md` (main), `help/{type}.md` (type-specific)

**References:** `reference-prd.md`, `reference-trd.md`, `reference-persona.md` (Requirements), `reference-epic.md`, `reference-story.md`, `reference-bug.md` (Specifications), `reference-architecture.md` (Architecture), `reference-code.md` (Code, Test), `reference-testing.md` (Test artifacts), `reference-test-best-practices.md` (Test pitfalls), `reference-test-e2e-guidelines.md` (E2E patterns)

**Templates:** `templates/prd-template.md`, `trd-template.md`, `epic-template.md`, `story-template.md`, `personas-template.md`, `plan-template.md`, `plan-index-template.md`, `bug-template.md`, `bug-index-template.md`, `tsd-template.md`, `test-spec-template.md`, `automation/*.template`
