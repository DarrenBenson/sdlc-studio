<!--
Load when: /sdlc-studio help
Dependencies: SKILL.md (always loaded first)
Related: help/arguments.md (full flags), help/references.md (reference catalogue), all help/*.md
-->

# /sdlc-studio help - Command Reference

This is the full command catalogue. SKILL.md stays lean and routes here on
`/sdlc-studio help`. For the full flag reference see `help/arguments.md`; for the
reference-file and template catalogue see `help/references.md`.

## Quick Start

```text
/sdlc-studio hint                    # Get single next step suggestion
/sdlc-studio status                  # Check pipeline state
/sdlc-studio prd generate            # Create PRD from codebase
/sdlc-studio trd generate            # Create TRD from codebase
/sdlc-studio epic                    # Generate Epics from PRD
/sdlc-studio story                   # Generate Stories from Epics
/sdlc-studio code plan               # Plan implementation for story
/sdlc-studio code implement          # Execute implementation plan
/sdlc-studio code test               # Run tests with traceability
/sdlc-studio code verify             # Verify code against AC
/sdlc-studio code check              # Run linters and checks
/sdlc-studio cr                      # Manage change requests
/sdlc-studio tsd                     # Create test strategy document
/sdlc-studio test-spec               # Generate test specifications
/sdlc-studio test-automation         # Generate executable tests
```

## Get Help for Specific Types

```text
/sdlc-studio prd help                # PRD commands and options
/sdlc-studio trd help                # TRD commands and options
/sdlc-studio tsd help                # Test strategy document help
/sdlc-studio persona help            # Persona management help
/sdlc-studio epic help               # Epic generation help
/sdlc-studio story help              # Story generation help
/sdlc-studio code help               # Code plan/test/verify/check help
/sdlc-studio test-spec help          # Test specification help
/sdlc-studio test-automation help    # Test automation help
/sdlc-studio bug help                # Bug tracking help
/sdlc-studio cr help                 # Change request help
/sdlc-studio rfc help                # RFC / design exploration help
/sdlc-studio lessons help            # Cross-project lessons-learned help
/sdlc-studio status help             # Pipeline status help
/sdlc-studio hint help               # Next step suggestion help
```

## All Commands

### Pipeline Status

| Command | Description |
| --- | --- |
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

### Reconciliation

| Command | Description |
| --- | --- |
| `/sdlc-studio reconcile` | Detect and fix all status drift |
| `/sdlc-studio reconcile --dry-run` | Preview fixes without applying |
| `/sdlc-studio reconcile --scope epics` | Reconcile epics only |
| `/sdlc-studio reconcile --scope stories` | Reconcile stories only |
| `/sdlc-studio reconcile --scope prd` | Reconcile PRD only |
| `/sdlc-studio reconcile --verify` | Run AC verifiers and update Verified state |
| `/sdlc-studio reconcile --verify --story US0001` | Verify a single story |
| `/sdlc-studio reconcile --verify --dry-run` | Preview verification without writes |

### Requirements Pipeline

| Command | Description |
| --- | --- |
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
| `/sdlc-studio epic review` | Cascading review (use `--quick` or `--resume`) |
| `/sdlc-studio story` | Generate User Stories from Epics |
| `/sdlc-studio story generate` | **Extract detailed specs from CODE** (brownfield) |
| `/sdlc-studio story review` | Review Story status from codebase |
| `/sdlc-studio persona` | Ask which mode (create/generate/review) |
| `/sdlc-studio persona create` | Interactive persona creation (Team or Stakeholder) |
| `/sdlc-studio persona generate` | Reverse engineer from `--from-prd`, `--from-code`, `--from-docs` |
| `/sdlc-studio persona list` | Show all project personas by category |
| `/sdlc-studio persona import/export` | Import or export persona markdown files |
| `/sdlc-studio persona review` | Review and refine existing personas |

### Persona Consultation & Chat

| Command | Description |
| --- | --- |
| `/sdlc-studio consult [persona] [artefact]` | Get structured feedback from persona |
| `/sdlc-studio consult team [artefact]` | Three Amigos review |
| `/sdlc-studio consult stakeholders [artefact]` | All stakeholder personas |
| `/sdlc-studio chat [persona]` | Interactive chat session |
| `/sdlc-studio chat --workshop [topic]` | Multi-persona discussion (see `help/chat.md`) |

### Technical Requirements

| Command | Description |
| --- | --- |
| `/sdlc-studio trd` | Ask which mode (create/generate/review) |
| `/sdlc-studio trd create` | Interactive TRD creation |
| `/sdlc-studio trd generate` | **Extract TRD from architecture** (brownfield) |
| `/sdlc-studio trd review` | Review TRD against implementation |
| `/sdlc-studio trd visualise` | Regenerate C4 architecture diagrams |
| `/sdlc-studio trd containerize` | Add container design decisions to TRD |

### Bug Tracking

| Command | Description |
| --- | --- |
| `/sdlc-studio bug` | Create new bug (interactive) |
| `/sdlc-studio bug list` | List all bugs |
| `/sdlc-studio bug list --status open` | List open bugs |
| `/sdlc-studio bug list --severity critical` | List critical bugs |
| `/sdlc-studio bug list --epic EP0001` | List bugs for epic |
| `/sdlc-studio bug fix --bug BG0001` | Start fixing a bug |
| `/sdlc-studio bug verify --bug BG0001` | Verify bug fix |
| `/sdlc-studio bug close --bug BG0001` | Close a bug |
| `/sdlc-studio bug reopen --bug BG0001` | Reopen a closed bug |

### Change Management

| Command | Description |
| --- | --- |
| `/sdlc-studio cr` | Ask what to do (create, list, action, review, close) |
| `/sdlc-studio cr create` | Interactive CR creation |
| `/sdlc-studio cr list` | List all change requests |
| `/sdlc-studio cr list --status proposed` | List proposed CRs |
| `/sdlc-studio cr list --priority P1` | List P1 change requests |
| `/sdlc-studio cr action --cr CR-0001` | Turn CR into epics and stories |
| `/sdlc-studio cr review` | Review CR statuses against implementation |
| `/sdlc-studio cr sync` | Two-way sync CRs with GitHub Issues |
| `/sdlc-studio cr sync --dry-run` | Preview sync without writes |
| `/sdlc-studio cr close --cr CR-0001` | Mark CR complete/rejected/deferred |

### Design Exploration (RFC)

| Command | Description |
| --- | --- |
| `/sdlc-studio rfc` | Ask what to do (create, list, review, accept, close) |
| `/sdlc-studio rfc create` | Draft a new RFC (unsettled design – options + open decisions) |
| `/sdlc-studio rfc list` | List RFCs (filter `--status`, `--priority`, `--author`) |
| `/sdlc-studio rfc review` | Flag stalled RFCs + unresolved open decisions |
| `/sdlc-studio rfc accept --rfc RFC-0001` | Record the decision + spawn/link the workstream CRs |
| `/sdlc-studio rfc close --rfc RFC-0001` | Supersede or withdraw an RFC |

### Development Pipeline

| Command | Description |
| --- | --- |
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
| --- | --- |
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
| --- | --- |
| `/sdlc-studio story plan --story US0001` | Create plan + test-spec, then review |
| `/sdlc-studio story implement --story US0001` | Execute story workflow (with state tracking) |
| `/sdlc-studio story implement --tdd` | Execute with TDD approach |
| `/sdlc-studio story implement --from-phase 3` | Resume from phase |
| `/sdlc-studio epic plan --epic EP0001` | Preview epic workflow |
| `/sdlc-studio epic plan --epic EP0001 --agentic` | Preview with agentic wave analysis |
| `/sdlc-studio epic implement --epic EP0001` | Execute epic workflow |
| `/sdlc-studio epic implement --epic EP0001 --agentic` | Execute with agentic waves |
| `/sdlc-studio epic implement --story US0001` | Resume from story |
| `/sdlc-studio epic implement --skip US0001` | Skip specific story |
| `/sdlc-studio project plan` | Preview project execution plan (all epics) |
| `/sdlc-studio project plan --agentic` | Preview with agentic wave estimates |
| `/sdlc-studio project implement` | Execute all epics in dependency order |
| `/sdlc-studio project implement --agentic` | Agentic waves within each epic |
| `/sdlc-studio project implement --agentic --no-artifacts` | Fast mode: no PL/TS/WF files |
| `/sdlc-studio project implement --from stories` | Generate stories first, then implement |
| `/sdlc-studio project implement --resume EP0003` | Resume from specific epic |

**State tracking:** `story implement` creates `sdlc-studio/workflows/WF{NNNN}.md` to track progress across sessions. `project implement` creates `sdlc-studio/.local/project-state.json` for cross-epic progress.

### Utilities

Skill-internal helpers live in the skill's `scripts/` directory (`$CLAUDE_SKILL_DIR/scripts/`, see `reference-scripts.md#skill-dir`). Claude invokes these on behalf of workflows; users do not call them directly. See `reference-scripts.md` for the full catalogue.

| Command | Description |
| --- | --- |
| `/sdlc-studio repo map build` | Index the repository symbols and imports |
| `/sdlc-studio repo map build --ignore vendor` | Skip an extra directory during indexing |
| `/sdlc-studio repo map query --story US0001` | Rank files by relevance to a story |
| `/sdlc-studio repo map query --story "auth flow"` | Rank files by a free-text query |
| `/sdlc-studio repo map stats` | Index size and top-10 hub files |

### Lessons (cross-project)

| Command | Description |
| --- | --- |
| `/sdlc-studio lessons recall` | Surface relevant cross-project lessons before a decision |
| `/sdlc-studio lessons add --global` | Promote a generalisable lesson to the skill's `lessons/` |
| `/sdlc-studio lessons list` | Print accumulated project lessons (`.local/lessons.md`) |
| `/sdlc-studio lessons add` | Append a new lesson to `.local/lessons.md` |
| `/sdlc-studio lessons prune --older EP0003` | Drop entries for old epics |

### Plan Files

| Command | Description |
| --- | --- |
| `/sdlc-studio plan list` | Show active Claude Code plan files (`--all`, `--stale`) |
| `/sdlc-studio plan archive {slug}` | Move a plan to `archive/{yyyy-mm}/` |

### External Integrations

Two-way sync between local records and external trackers. v1.6.0 ships GitHub Issues; Linear, Jira, and GitHub Projects board integration are deferred. Requires `gh` CLI installed and authenticated. See `reference-github-sync.md`.

| Command | Description |
| --- | --- |
| `/sdlc-studio cr sync` | Push + pull CRs to/from GitHub Issues |
| `/sdlc-studio story sync` | Push + pull Stories to/from GitHub Issues |
| `/sdlc-studio project sync` | Sync all three types (cr, story, epic) |
| `/sdlc-studio project sync push --type all` | Push only |
| `/sdlc-studio project sync pull --type cr` | Pull only |
| `/sdlc-studio project sync cascade` | Merged-PR cascade candidates |
| `/sdlc-studio project sync cascade --since <iso>` | Limit PR window |
| `/sdlc-studio project sync state` | Print sync state file |

## Output Locations

All artifacts are under the `sdlc-studio/` directory:

```text
sdlc-studio/
  prd.md                      # Product Requirements
  trd.md                      # Technical Requirements
  tsd.md                      # Test Strategy Document
  personas.md                 # User Personas
  epics/
    _index.md                 # Epic registry
    EP0001-*.md               # Epic files
  stories/
    _index.md                 # Story registry
    US0001-*.md               # Story files
  plans/
    _index.md                 # Plan registry
    PL0001-*.md               # Implementation plans
  bugs/
    _index.md                 # Bug registry
    BG0001-*.md               # Bug reports
  change-requests/
    _index.md                 # CR registry
    CR0001-*.md               # Change requests
  rfcs/
    _index.md                 # RFC registry
    RFC0001-*.md              # Design-exploration RFCs (pre-CR)
  test-specs/
    _index.md                 # Spec registry
    TS0001-*.md               # Test Specifications
  workflows/
    WF0001-*.md               # Workflow tracking

tests/                        # Generated test code
  unit/
  integration/
  api/
  e2e/
```

## Typical Workflows

### Quick Start

```text
/sdlc-studio hint                # Get suggested next step
/sdlc-studio status              # See full pipeline state
```

### Greenfield Project (Manual)

```text
/sdlc-studio prd create
/sdlc-studio trd create
/sdlc-studio persona
/sdlc-studio epic
/sdlc-studio story
/sdlc-studio tsd
/sdlc-studio test-spec
/sdlc-studio test-automation
```

Per-story you choose TDD or Test-After. Both paths produce the same artifacts, in different order:

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

### Brownfield Project (Manual)

```text
/sdlc-studio prd generate
/sdlc-studio trd generate
/sdlc-studio persona generate
/sdlc-studio epic
/sdlc-studio story
/sdlc-studio tsd generate
/sdlc-studio test-spec generate
/sdlc-studio test-automation
```

Flow: `prd generate → trd generate → persona generate → epic → story generate → test-spec → test-automation → code test (VALIDATE)`

**Critical:** The `code test` step validates specs against reality. Not optional.

### Automated Workflow (Recommended)

At story level:

```text

PRD → TRD → Personas → Epics → Stories
                                  │
                          story plan --story US0001
                                  │
                          story implement --story US0001
                                  │
                          (all 8 phases run automatically)
```

Or at the epic level with autonomous execution:

```text

epic plan --epic EP0001 --agentic
        │
(analyses dependencies → assigns concurrent waves)
        │
epic implement --epic EP0001 --agentic
        │
Wave 1: [US0001, US0003] concurrent
Wave 2: [US0002, US0004] concurrent
Wave 3: [US0005] sequential (hub file conflict)
```

`--agentic` analyses the dependency graph and hub file overlap to identify stories that can safely execute concurrently. Falls back to sequential for any stories with shared file conflicts.

**Workflow phases per story:**

1. Plan (code plan)
2. Test Spec (test-spec)
3. Tests (test-automation)
4. Implement (code implement)
5. Test (code test)
6. Verify (code verify)
7. Check (code check)
8. Review (status review)

### Project Implementation (Full PRD)

```text
/sdlc-studio project plan --agentic              # Preview execution order
/sdlc-studio project implement --agentic --no-artifacts  # Implement all epics
```

```text

project implement --agentic --no-artifacts
        │
EP0001: epic implement --agentic → commit → reconcile
EP0002: epic implement --agentic → commit → reconcile
EP0003: epic implement --agentic → commit → reconcile → review (every 3 epics)
...
Final: review → reconcile → report
```

**Quality gates enforced at every boundary:**

- Wave: typecheck + test suite
- Epic: reconcile + status cascade + commit
- Every 3 epics: quick review
- Project: full review + reconcile + code check

See `reference-project.md` for the full workflow.

### Epic Implementation

```text
/sdlc-studio epic plan --epic EP0002 --agentic   # Preview wave analysis
/sdlc-studio epic implement --epic EP0002 --agentic  # Implement one epic
```

### Story Implementation

```text
/sdlc-studio story plan --story US0001           # Create plan + test-spec
/sdlc-studio story implement --story US0001      # Execute 8-phase workflow
```

### Development Cycle (Manual)

```text
/sdlc-studio code plan           # Plan story (status -> Planned)
/sdlc-studio code implement      # Execute plan (status -> In Progress)
/sdlc-studio code test           # Run tests
/sdlc-studio code verify         # Verify AC (status -> Review)
/sdlc-studio code check          # Run linters (status -> Done)
```

Status: `Draft/Ready → Planned → In Progress → Review → Done`

### Daily Usage

```text
/sdlc-studio hint                # What should I do next?
/sdlc-studio status              # Full pipeline overview
/sdlc-studio status --brief      # Quick: Requirements 85% | Code 90% | Tests 94%
/sdlc-studio code plan           # Plan next story
```

## Common Options

| Option | Description |
| --- | --- |
| `--force` | Overwrite existing files |
| `--epic EP0001` | Target specific Epic |
| `--story US0001` | Target specific Story |
| `--spec TS0001` | Target specific Test Spec |
| `--type unit` | Filter by test type |
| `--framework pytest` | Override framework detection |
| `--no-fix` | Check without auto-fixing (code check) |
| `--verbose` | Detailed test output |

For the complete flag reference, see `help/arguments.md`.

## See Also

- `SKILL.md` - Skill router and Progressive Loading Guide
- `help/arguments.md` - Full argument and flag reference
- `help/references.md` - Reference-file and template catalogue
- `reference-code.md` - Detailed workflows (Code, Test)
- `reference-tsd.md`, `reference-test-spec.md`, `reference-test-automation.md` - Testing workflows
