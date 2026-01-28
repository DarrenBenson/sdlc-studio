---
name: sdlc-studio
description: /sdlc-studio [type] [action] - SDLC pipeline: requirements, specifications, code, testing. Run /sdlc-studio help for commands and /sdlc-studio status for next steps.
allowed-tools: Read, Glob, Grep, Write, Edit, Task, AskUserQuestion
---

# SDLC Studio

Manage project specifications and test artifacts. Supports the full pipeline from PRD creation through Epic decomposition, User Story generation, and streamlined test automation.

## Critical Philosophy (Read This First)

**Two modes for every artifact type:**

| Mode | Purpose | When to Use |
|------|---------|-------------|
| **create** | Author new specifications from user input | Greenfield projects, new features |
| **generate** | Extract specifications from existing code | Brownfield projects, documentation gaps |

> **New to Create vs Generate?** Read `reference-philosophy.md` - it explains why these modes exist and how they differ fundamentally.
>
> **Using generate mode?** You MUST read `reference-philosophy.md#generate-mode` first - generated specs must be validated by tests.

**Generate mode is NOT documentation.** It produces a **migration blueprint** - a specification detailed enough that another team could rebuild the system in a different technology stack. Generated specs MUST be validated by running tests against the existing implementation.

## Quick Start

```bash
/sdlc-studio help                    # Show command reference
/sdlc-studio status                  # Check pipeline state and next steps
/sdlc-studio review                  # Unified PRD/TRD/TSD review
/sdlc-studio upgrade --dry-run       # Preview schema upgrade
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

```bash
/sdlc-studio {type} help             # Show help for specific type
```

Examples:

```bash
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

Use when asked about: PRD, TRD, epics, stories, personas, bugs, code planning, implementation, testing, test specs, test automation, project status, or any `/sdlc-studio` command.

## Instructions

When invoked with `/sdlc-studio [type] [action]`:

1. **Parse Command:** Extract type and action from arguments
2. **Load Help File:** Read `help/{type}.md` for command-specific guidance
3. **Check Philosophy:** If generate mode, load `reference-philosophy.md#generate-mode` FIRST
4. **Follow Progressive Loading:**
   - Load reference files only for multi-step workflows
   - Load templates only when creating artifacts
   - Load decision files when choosing approaches (TDD, Ready status)
5. **Execute Workflow:** Follow step-by-step procedure in reference file
6. **Update Status:** Modify artifact status markers per `reference-outputs.md`
7. **Validate:** Check Ready criteria in `reference-decisions.md` before proceeding

**Note:** Version checks run on `hint` and `status` commands only (see those help files).

See "Progressive Loading Guide" below for detailed file loading patterns.

## Progressive Loading Guide

Claude loads files progressively based on task needs:

| Task Type | Primary Load | Secondary Load | Decision Load |
|-----------|--------------|----------------|---------------|
| Understanding command | help/{type}.md | - | - |
| Create mode workflow | help/{type}.md | reference-{domain}.md | reference-philosophy.md#create-mode |
| Generate mode workflow | reference-philosophy.md#generate-mode | help/{type}.md | reference-{domain}.md |
| Creating artifacts | templates/core/{type}.md | reference-outputs.md | - |
| Loading modules | templates/modules/{domain}/*.md | - | - |
| Planning code | reference-code.md#code-plan-workflow | reference-decisions.md#story-ready | best-practices/{language}.md |
| Choosing TDD/Test-After | reference-decisions.md#tdd-decision-tree | reference-test-best-practices.md | - |
| Validating Ready status | reference-decisions.md#{type}-ready | reference-outputs.md | - |
| Document review | reference-review.md | reference-{doc}.md | - |
| Schema upgrade | reference-upgrade.md | reference-config.md | - |

**Template structure:**

| Path | Purpose |
|------|---------|
| `templates/core/*.md` | Streamlined core templates (v2) |
| `templates/indexes/*.md` | Index file templates |
| `templates/modules/trd/*.md` | Optional TRD modules (diagrams, containers, ADR) |
| `templates/modules/tsd/*.md` | Optional TSD modules (contract, perf, security) |
| `templates/modules/epic/*.md` | Optional Epic perspective modules |
| `templates/config-defaults.yaml` | Skill default configuration |

**Module loading flags:**

| Flag | Modules Loaded |
|------|---------------|
| `trd create --with-diagrams` | modules/trd/c4-diagrams.md |
| `trd create --with-containers` | modules/trd/container-design.md |
| `trd create --full` | All TRD modules |
| `epic --perspective engineering` | modules/epic/engineering-view.md |
| `epic --perspective product` | modules/epic/product-view.md |
| `epic --perspective test` | modules/epic/test-view.md |

**Reference file mapping:**

| Domain | Reference File |
|--------|----------------|
| PRD workflows | reference-prd.md#prd-create-workflow, reference-prd.md#prd-generate-workflow |
| TRD workflows | reference-trd.md#trd-create-workflow, reference-trd.md#trd-generate-workflow |
| Persona workflows | reference-persona.md#persona-workflow, reference-persona.md#persona-generate-workflow |
| Epic workflows | reference-epic.md#epic-workflow |
| Story workflows | reference-story.md#story-workflow, reference-story.md#story-generate-workflow |
| Bug workflows | reference-bug.md#bug-create-workflow, reference-bug.md#bug-fix-workflow |
| Code plan/implement/verify/test/check | reference-code.md#code-plan-workflow, reference-code.md#code-implementation-workflow |
| Code refactor/review | reference-refactor.md |
| TSD, status dashboard, TSD review | reference-tsd.md, reference-tsd.md#tsd-review-workflow |
| Unified document review | reference-review.md |
| Test specifications | reference-test-spec.md |
| Test automation, test-env | reference-test-automation.md |
| Architecture decisions | reference-architecture.md |
| Cross-stage decisions, Ready criteria | reference-decisions.md#tdd-decision-tree, reference-decisions.md#story-ready |
| Create vs Generate philosophy | reference-philosophy.md#create-mode, reference-philosophy.md#generate-mode |
| Test writing guidelines | reference-test-best-practices.md |
| E2E and mocking patterns | reference-test-e2e-guidelines.md |
| Configuration options | reference-config.md |
| Schema upgrade | reference-upgrade.md |
| Output formats and status values | reference-outputs.md#output-formats, reference-outputs.md#status-transitions |

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `type` | See Type Reference below | Required |
| `action` | create, generate, review, plan, verify, check, list, fix, close, **help** | varies |
| `--output` | Output path (file or directory) | varies by type |
| `--prd` | PRD file path (for epic) | sdlc-studio/prd.md |
| `--epic` | Specific epic ID | all epics |
| `--perspective` | Epic breakdown focus (engineering, product, test) | balanced |
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
| `--env` | Test environment (local, docker) | local |
| `--plan` | Specific plan ID (for implement) | auto-select |
| `--tdd` | Force TDD mode (for implement) | plan recommendation |
| `--no-tdd` | Force Test-After mode (for implement) | plan recommendation |
| `--docs` | Update documentation (for implement) | true |
| `--no-docs` | Skip documentation updates (for implement) | false |
| `--from-phase` | Resume workflow from phase N (for story implement) | 1 |
| `--skip` | Skip specific story (for epic implement) | none |
| `--dry-run` | Preview changes without applying (for refactor) | false |
| `--focus` | Review focus area (patterns, security, performance, testing, all) | all |
| `--severity` | Minimum severity to report (for review) | all |
| `--quick` | Use cached status results (for status), skip cascade (for epic review) | varies |
| `--full` | Run fresh status analysis | false |
| `--resume` | Resume cascading review from pause point | false |

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
| `test-env` | Containerised test environment setup |
| `bug` | Bug tracking and traceability |
| `status` | Visual dashboard: Requirements, Code, Tests health |
| `hint` | Single actionable next step |
| `help` | Show command reference and examples |

## Command Reference

### Pipeline Status

| Command | Description |
|---------|-------------|
| `/sdlc-studio status` | Visual dashboard (quick mode, uses cache) |
| `/sdlc-studio status --full` | Full refresh, updates cache |
| `/sdlc-studio status --testing` | Tests pillar only |
| `/sdlc-studio status --workflows` | Workflow state only |
| `/sdlc-studio status --brief` | One-line summary |

**Four Pillars:**

- 📋 **Requirements** (PRD Status) - PRD, Personas, Epics, Stories
- 💻 **Code** (TRD Status) - TRD, Lint, TODOs
- 🧪 **Tests** (TSD Status) - Coverage, E2E features
- 🔍 **Reviews** - Review currency, findings status

### Requirements Pipeline

| Command | Description |
|---------|-------------|
| `/sdlc-studio init` | Initialise project context and config |
| `/sdlc-studio upgrade` | Upgrade project to latest schema version |
| `/sdlc-studio upgrade --dry-run` | Preview upgrade changes without applying |
| `/sdlc-studio review` | Unified PRD, TRD, TSD review |
| `/sdlc-studio review --quick` | Fast review using cached data |
| `/sdlc-studio review --focus {doc}` | Review specific document (prd, trd, tsd) |
| `/sdlc-studio hint` | Get single actionable next step |
| `/sdlc-studio help` | Show command reference and examples |
| `/sdlc-studio prd` | Ask which mode (create/generate/review) |
| `/sdlc-studio prd create` | Interactive PRD creation |
| `/sdlc-studio prd generate` | **Extract PRD from codebase** (brownfield) |
| `/sdlc-studio prd review` | Review PRD against codebase, update status |
| `/sdlc-studio epic` | Generate Epics from PRD |
| `/sdlc-studio epic review` | Cascading review of epic + changed stories (default) |
| `/sdlc-studio epic review --quick` | Quick review - epic only, skip cascade |
| `/sdlc-studio epic review --resume` | Resume from pause point |
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
| `/sdlc-studio trd visualise` | Regenerate C4 architecture diagrams |
| `/sdlc-studio trd containerize` | Add container design decisions to TRD |

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
| `/sdlc-studio code refactor` | Guided refactoring workflow |
| `/sdlc-studio code refactor --type extract-method` | Apply specific refactoring |
| `/sdlc-studio code review` | Design pattern and quality review |
| `/sdlc-studio code review --story US0001` | Review specific story implementation |
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
| `/sdlc-studio test-env setup` | Generate docker-compose.test.yml |
| `/sdlc-studio test-env up` | Start test environment |
| `/sdlc-studio test-env down` | Stop test environment |
| `/sdlc-studio test-env status` | Check environment health |

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

- `reference-prd.md`, `reference-trd.md`, `reference-persona.md` - PRD, TRD, Persona workflows
- `reference-epic.md`, `reference-story.md`, `reference-bug.md` - Epic, Story, Bug workflows
- `reference-code.md` - Code plan, implement, verify, check, test workflows
- `reference-refactor.md` - Code refactor, review workflows
- `reference-tsd.md` - TSD, status dashboard workflows
- `reference-test-spec.md` - Test specification workflows
- `reference-test-automation.md` - Test automation, test environment workflows

---

## Error Handling

**Missing prerequisites:** Prompts to run earlier pipeline step (e.g., no PRD → `prd`, no epics → `epic`, no stories → `story`, no plans → `code plan`). **Existing files:** Warns and asks to continue unless `--force`. **No type:** Asks user which type. **ID collision:** Auto-increments. **Open questions:** Reports and pauses. **Unknown language:** Asks user to specify framework.

## Typical Workflow

### Greenfield (Create Mode)

```text

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

```text

PRD → TRD → Personas → Epics → Stories
                                  │
                          story plan --story US0001
                                  │
                          story implement --story US0001
                                  │
                          (all 7 phases run automatically)
```

Or at the epic level:

```text

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
8. Review (status review)

### Brownfield (Specification Extraction)

```bash

prd generate → trd generate → persona generate → epic → story generate → test-spec → test-automation → code test (VALIDATE)
```

**Critical:** The `code test` step validates specs against reality. Not optional.

### Development Cycle

```text

code plan → code implement → code test → code verify → code check
```

Status: `Draft/Ready → Planned → In Progress → Review → Done`

### Daily Usage

```bash

/sdlc-studio status          # Visual dashboard - what needs attention?
/sdlc-studio status --brief  # Quick: Requirements 85% | Code 90% | Tests 94%
/sdlc-studio hint            # Single next step
/sdlc-studio code plan       # Plan next story
/sdlc-studio code implement  # Execute plan
```

## See Also

**Philosophy:** `reference-philosophy.md` - **Read this first.** Explains Create vs Generate modes and why generate mode produces migration blueprints, not documentation.

**Decisions:** `reference-decisions.md` - Decision impact matrix, TDD decision tree, Ready status criteria, cross-stage validation checkpoints.

**Configuration:** `reference-config.md` - Project configuration options for coverage targets, story quality gates, and thresholds.

**Help:** `help/help.md` (main), `help/{type}.md` (type-specific), `help/upgrade.md` (schema upgrade)

**References:** `reference-prd.md`, `reference-trd.md`, `reference-persona.md` (Requirements), `reference-epic.md`, `reference-story.md`, `reference-bug.md` (Specifications), `reference-architecture.md` (Architecture), `reference-code.md` (Code, Test), `reference-refactor.md` (Refactoring, Review), `reference-review.md` (Unified document review), `reference-tsd.md`, `reference-test-spec.md`, `reference-test-automation.md` (Test artifacts), `reference-test-best-practices.md` (Test pitfalls), `reference-test-e2e-guidelines.md` (E2E patterns), `reference-upgrade.md` (Schema migration)

**Templates (v2 modular structure):**
- Core: `templates/core/*.md` (prd, trd, tsd, epic, story, plan, test-spec, bug, personas)
- Indexes: `templates/indexes/*.md` (epic, story, plan, bug, test-spec, review)
- Modules: `templates/modules/trd/*.md` (c4-diagrams, container-design, adr), `templates/modules/tsd/*.md` (contract-tests, performance-tests, security-tests), `templates/modules/epic/*.md` (engineering-view, product-view, test-view)
- Config: `templates/config-defaults.yaml`, `templates/config.yaml`, `templates/version.yaml`
- Automation: `templates/automation/*.template` (pytest, jest, vitest, go, xunit, junit)
