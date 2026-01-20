<!--
Load: On /sdlc-studio help
Dependencies: SKILL.md (always loaded first)
Related: All help/*.md files for type-specific help
-->

# /sdlc-studio help - Command Reference

## Quick Start

```
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
/sdlc-studio tsd                     # Create test strategy document
/sdlc-studio test-spec               # Generate test specifications
/sdlc-studio test-automation         # Generate executable tests
```

## Get Help for Specific Types

```
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
/sdlc-studio status help             # Pipeline status help
/sdlc-studio hint help               # Next step suggestion help
```

## All Commands

### Pipeline Status

| Command | Description |
|---------|-------------|
| `/sdlc-studio status` | Show full pipeline state |
| `/sdlc-studio status --testing` | Testing pipeline only |
| `/sdlc-studio status --brief` | One-line summary |

### Requirements Pipeline

| Command | Description |
|---------|-------------|
| `/sdlc-studio hint` | Get single actionable next step |
| `/sdlc-studio prd create` | Interactive PRD creation |
| `/sdlc-studio prd generate` | Reverse-engineer PRD from codebase |
| `/sdlc-studio prd review` | Review PRD against codebase |
| `/sdlc-studio trd create` | Interactive TRD creation |
| `/sdlc-studio trd generate` | Reverse-engineer TRD from codebase |
| `/sdlc-studio trd review` | Review TRD against implementation |
| `/sdlc-studio epic` | Generate Epics from PRD |
| `/sdlc-studio epic review` | Review Epic status |
| `/sdlc-studio story` | Generate Stories from Epics |
| `/sdlc-studio story --epic EP0001` | Generate for specific Epic |
| `/sdlc-studio story review` | Review Story status |
| `/sdlc-studio persona` | Interactive persona creation |
| `/sdlc-studio persona generate` | Infer personas from codebase |
| `/sdlc-studio persona review` | Review and refine existing personas |

### Development Pipeline

| Command | Description |
|---------|-------------|
| `/sdlc-studio code plan` | Plan next incomplete story |
| `/sdlc-studio code plan --story US0001` | Plan specific story |
| `/sdlc-studio code implement` | Implement next planned story |
| `/sdlc-studio code implement --plan PL0001` | Implement specific plan |
| `/sdlc-studio code implement --tdd` | Implement with TDD mode |
| `/sdlc-studio code implement --no-docs` | Implement without doc updates |
| `/sdlc-studio code verify` | Verify next In Progress story |
| `/sdlc-studio code verify --story US0001` | Verify specific story |
| `/sdlc-studio code test` | Run all tests |
| `/sdlc-studio code test --story US0001` | Run tests for specific story |
| `/sdlc-studio code test --epic EP0001` | Run tests for specific epic |
| `/sdlc-studio code test --type unit` | Run only unit tests |
| `/sdlc-studio code check` | Run linters with auto-fix |
| `/sdlc-studio code check --no-fix` | Check only, no changes |

### Testing Pipeline

| Command | Description |
|---------|-------------|
| `/sdlc-studio tsd` | Create test strategy document |
| `/sdlc-studio tsd generate` | Infer strategy from codebase |
| `/sdlc-studio test-spec` | Generate test specs from epics |
| `/sdlc-studio test-spec --epic EP0001` | Generate for specific Epic |
| `/sdlc-studio test-spec generate` | Reverse-engineer from existing tests |
| `/sdlc-studio test-spec review` | Review and sync status |
| `/sdlc-studio test-automation` | Generate executable tests |
| `/sdlc-studio test-automation --spec TS0001` | Generate for specific spec |
| `/sdlc-studio test-automation --type unit` | Generate only unit tests |

## Output Locations

All artifacts are under the `sdlc-studio/` directory:

```
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
```
/sdlc-studio hint                # Get suggested next step
/sdlc-studio status              # See full pipeline state
```

### Greenfield Project (Manual)
```
/sdlc-studio prd create
/sdlc-studio trd create
/sdlc-studio persona
/sdlc-studio epic
/sdlc-studio story
/sdlc-studio tsd
/sdlc-studio test-spec
/sdlc-studio test-automation
```

### Brownfield Project (Manual)
```
/sdlc-studio prd generate
/sdlc-studio trd generate
/sdlc-studio persona generate
/sdlc-studio epic
/sdlc-studio story
/sdlc-studio tsd generate
/sdlc-studio test-spec generate
/sdlc-studio test-automation
```

### Development Cycle
```
/sdlc-studio code plan           # Plan story (status → Planned)
/sdlc-studio code implement      # Execute plan (status → In Progress)
/sdlc-studio code test           # Run tests
/sdlc-studio code verify         # Verify AC (status → Review)
/sdlc-studio code check          # Run linters (status → Done)
```

### Daily Usage
```
/sdlc-studio hint                # What should I do next?
/sdlc-studio status              # Full pipeline overview
/sdlc-studio code plan           # Plan next story
```

## Common Options

| Option | Description |
|--------|-------------|
| `--force` | Overwrite existing files |
| `--epic EP0001` | Target specific Epic |
| `--story US0001` | Target specific Story |
| `--spec TS0001` | Target specific Test Spec |
| `--type unit` | Filter by test type |
| `--framework pytest` | Override framework detection |
| `--no-fix` | Check without auto-fixing (code check) |
| `--verbose` | Detailed test output |

## See Also

- `SKILL.md` - Full skill documentation
- `reference-philosophy.md` - Create vs Generate modes (read first)
- `reference-*.md` - Domain-specific workflows (13 files)
- `reference-code.md` - Code plan, implement, review workflows
- `reference-testing.md` - Testing workflows
