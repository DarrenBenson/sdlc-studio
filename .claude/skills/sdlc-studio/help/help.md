# /sdlc-studio help - Command Reference

## Quick Start

```
/sdlc-studio init                    # Bootstrap entire pipeline (auto-detect)
/sdlc-studio hint                    # Get single next step suggestion
/sdlc-studio status                  # Check pipeline state
/sdlc-studio prd generate            # Create PRD from codebase
/sdlc-studio trd generate            # Create TRD from codebase
/sdlc-studio epic                    # Generate Epics from PRD
/sdlc-studio story                   # Generate Stories from Epics
/sdlc-studio code plan               # Plan implementation for story
/sdlc-studio code implement          # Execute implementation plan
/sdlc-studio code review             # Review code against AC
/sdlc-studio code check              # Run linters and checks
/sdlc-studio test                    # Run tests with traceability
/sdlc-studio test-strategy           # Create test strategy
/sdlc-studio test-spec               # Generate test specifications
/sdlc-studio test-automation         # Generate executable tests
```

## Get Help for Specific Types

```
/sdlc-studio init help               # Project initialisation help
/sdlc-studio hint help               # Next step suggestion help
/sdlc-studio prd help                # PRD commands and options
/sdlc-studio trd help                # TRD commands and options
/sdlc-studio epic help               # Epic generation help
/sdlc-studio story help              # Story generation help
/sdlc-studio persona help            # Persona management help
/sdlc-studio code help               # Code plan/review/check help
/sdlc-studio test help               # Test runner help
/sdlc-studio test-strategy help      # Test strategy help
/sdlc-studio test-spec help          # Test specification help
/sdlc-studio test-automation help    # Test automation help
/sdlc-studio status help             # Pipeline status help
/sdlc-studio migrate help            # Migration help
```

## All Commands

### Pipeline Status

| Command | Description |
|---------|-------------|
| `/sdlc-studio status` | Show full pipeline state |
| `/sdlc-studio status --testing` | Testing pipeline only |
| `/sdlc-studio status --brief` | One-line summary |

### Project Setup

| Command | Description |
|---------|-------------|
| `/sdlc-studio init` | Auto-detect and bootstrap pipeline |
| `/sdlc-studio init --brownfield` | Force existing project mode |
| `/sdlc-studio init --greenfield` | Force new project mode |
| `/sdlc-studio init --skip-tests` | Skip test artifact generation |
| `/sdlc-studio init --dry-run` | Show plan without executing |
| `/sdlc-studio hint` | Get single actionable next step |

### Requirements Pipeline

| Command | Description |
|---------|-------------|
| `/sdlc-studio prd create` | Interactive PRD creation |
| `/sdlc-studio prd generate` | Reverse-engineer PRD from codebase |
| `/sdlc-studio prd update` | Update feature implementation status |
| `/sdlc-studio trd create` | Interactive TRD creation |
| `/sdlc-studio trd generate` | Reverse-engineer TRD from codebase |
| `/sdlc-studio trd update` | Update TRD with implementation changes |
| `/sdlc-studio epic` | Generate Epics from PRD |
| `/sdlc-studio epic update` | Update Epic status |
| `/sdlc-studio story` | Generate Stories from Epics |
| `/sdlc-studio story --epic EP0001` | Generate for specific Epic |
| `/sdlc-studio story update` | Update Story status |
| `/sdlc-studio persona` | Interactive persona creation |
| `/sdlc-studio persona generate` | Infer personas from codebase |
| `/sdlc-studio persona update` | Refine existing personas |

### Development Pipeline

| Command | Description |
|---------|-------------|
| `/sdlc-studio code plan` | Plan next incomplete story |
| `/sdlc-studio code plan --story US0001` | Plan specific story |
| `/sdlc-studio code implement` | Implement next planned story |
| `/sdlc-studio code implement --plan PL0001` | Implement specific plan |
| `/sdlc-studio code implement --tdd` | Implement with TDD mode |
| `/sdlc-studio code implement --no-docs` | Implement without doc updates |
| `/sdlc-studio code review` | Review next In Progress story |
| `/sdlc-studio code review --story US0001` | Review specific story |
| `/sdlc-studio code check` | Run linters with auto-fix |
| `/sdlc-studio code check --no-fix` | Check only, no changes |
| `/sdlc-studio test` | Run all tests |
| `/sdlc-studio test --story US0001` | Run tests for specific story |
| `/sdlc-studio test --epic EP0001` | Run tests for specific epic |
| `/sdlc-studio test --type unit` | Run only unit tests |

### Testing Pipeline

| Command | Description |
|---------|-------------|
| `/sdlc-studio test-strategy` | Create project test strategy |
| `/sdlc-studio test-strategy generate` | Infer from codebase |
| `/sdlc-studio test-spec` | Generate test specs from epics |
| `/sdlc-studio test-spec --epic EP0001` | Generate for specific Epic |
| `/sdlc-studio test-spec generate` | Reverse-engineer from existing tests |
| `/sdlc-studio test-spec update` | Sync automation status |
| `/sdlc-studio test-automation` | Generate executable tests |
| `/sdlc-studio test-automation --spec TSP0001` | Generate for specific spec |
| `/sdlc-studio test-automation --type unit` | Generate only unit tests |
| `/sdlc-studio migrate` | Preview migration from old format |
| `/sdlc-studio migrate --execute` | Execute migration |

## Output Locations

All artifacts are under the `sdlc-studio/` directory:

```
sdlc-studio/
  prd.md                      # Product Requirements
  trd.md                      # Technical Requirements
  personas.md                 # User Personas
  definition-of-done.md       # Definition of Done
  epics/
    _index.md                 # Epic registry
    EP0001-*.md               # Epic files
  stories/
    _index.md                 # Story registry
    US0001-*.md               # Story files
  plans/
    _index.md                 # Plan registry
    PL0001-*.md               # Implementation plans
  testing/
    strategy.md               # Test Strategy
    specs/
      _index.md               # Spec registry
      TSP0001-*.md            # Test Specifications

tests/                        # Generated test code
  unit/
  integration/
  api/
  e2e/
```

## Typical Workflows

### Quick Start (Recommended)
```
/sdlc-studio init                # Auto-detect and bootstrap everything
/sdlc-studio hint                # Get suggested next step
```

### Greenfield Project (Manual)
```
/sdlc-studio prd create
/sdlc-studio trd create
/sdlc-studio persona
/sdlc-studio epic
/sdlc-studio story
/sdlc-studio test-strategy
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
/sdlc-studio test-strategy generate
/sdlc-studio test-spec generate
/sdlc-studio test-automation
```

### Development Cycle
```
/sdlc-studio code plan           # Plan story (status → Planned)
/sdlc-studio code implement      # Execute plan (status → In Progress)
/sdlc-studio code check          # Run linters, fix issues
/sdlc-studio code review         # Verify AC (status → Review)
/sdlc-studio test                # Run tests (status → Done)
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
| `--spec TSP0001` | Target specific Test Spec |
| `--type unit` | Filter by test type |
| `--framework pytest` | Override framework detection |
| `--no-fix` | Check without auto-fixing (code check) |
| `--verbose` | Detailed test output |

## See Also

- `SKILL.md` - Full skill documentation
- `reference.md` - Detailed workflows (PRD, Epic, Story, Persona)
- `reference-code.md` - Detailed workflows (Code, Test)
- `reference-testing.md` - Testing workflows (Test artifacts)
