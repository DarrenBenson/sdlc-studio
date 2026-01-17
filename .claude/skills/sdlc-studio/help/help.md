# /sdlc-studio help - Command Reference

## Quick Start

```
/sdlc-studio status                  # Check pipeline state
/sdlc-studio prd generate            # Create PRD from codebase
/sdlc-studio epic                    # Generate Epics from PRD
/sdlc-studio story                   # Generate Stories from Epics
/sdlc-studio test-strategy           # Create test strategy
/sdlc-studio test-spec               # Generate test specifications
/sdlc-studio test-automation         # Generate executable tests
```

## Get Help for Specific Types

```
/sdlc-studio prd help                # PRD commands and options
/sdlc-studio epic help               # Epic generation help
/sdlc-studio story help              # Story generation help
/sdlc-studio persona help            # Persona management help
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

### Requirements Pipeline

| Command | Description |
|---------|-------------|
| `/sdlc-studio prd create` | Interactive PRD creation |
| `/sdlc-studio prd generate` | Reverse-engineer PRD from codebase |
| `/sdlc-studio prd update` | Update feature implementation status |
| `/sdlc-studio epic` | Generate Epics from PRD |
| `/sdlc-studio epic update` | Update Epic status |
| `/sdlc-studio story` | Generate Stories from Epics |
| `/sdlc-studio story --epic EP0001` | Generate for specific Epic |
| `/sdlc-studio story update` | Update Story status |
| `/sdlc-studio persona` | Interactive persona creation |
| `/sdlc-studio persona generate` | Infer personas from codebase |
| `/sdlc-studio persona update` | Refine existing personas |

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
  personas.md                 # User Personas
  definition-of-done.md       # Definition of Done
  epics/
    _index.md                 # Epic registry
    EP0001-*.md               # Epic files
  stories/
    _index.md                 # Story registry
    US0001-*.md               # Story files
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

### Greenfield Project
```
/sdlc-studio prd create
/sdlc-studio persona
/sdlc-studio epic
/sdlc-studio story
/sdlc-studio test-strategy
/sdlc-studio test-spec
/sdlc-studio test-automation
```

### Brownfield Project
```
/sdlc-studio prd generate
/sdlc-studio persona generate
/sdlc-studio epic
/sdlc-studio story
/sdlc-studio test-strategy generate
/sdlc-studio test-spec generate
/sdlc-studio test-automation
```

### Daily Usage
```
/sdlc-studio status              # What needs attention?
/sdlc-studio test-automation     # Generate pending tests
```

## Common Options

| Option | Description |
|--------|-------------|
| `--force` | Overwrite existing files |
| `--epic EP0001` | Target specific Epic |
| `--spec TSP0001` | Target specific Test Spec |
| `--type unit` | Filter by test type |
| `--framework pytest` | Override framework detection |

## See Also

- `SKILL.md` - Full skill documentation
- `reference.md` - Detailed workflows
- `reference-testing.md` - Testing workflows
