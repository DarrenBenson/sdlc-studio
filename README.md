# SDLC Studio

A Claude Code skill for managing the full software development lifecycle - from Product Requirements Documents through to automated test generation.

## Features

- **PRD Management** - Create, generate from codebase, or update Product Requirements Documents
- **Epic Generation** - Group features into manageable Epics with acceptance criteria
- **Story Breakdown** - Generate User Stories with Given/When/Then acceptance criteria
- **Persona Creation** - Define or infer user personas from codebase patterns
- **Test Strategy** - Document project-level testing approach
- **Test Specifications** - Consolidated test specs with embedded fixtures
- **Test Automation** - Generate executable tests for pytest, Jest, Vitest, Go, and more

## Installation

Copy the skill to your Claude Code skills directory:

```bash
# Project-level installation (recommended)
mkdir -p .claude/skills
cp -r sdlc-studio/.claude/skills/sdlc-studio .claude/skills/

# Or global installation
cp -r sdlc-studio/.claude/skills/sdlc-studio ~/.claude/skills/
```

## Quick Start

```bash
# Check pipeline status
/sdlc-studio status

# Generate PRD from existing codebase
/sdlc-studio prd generate

# Create Epics from PRD
/sdlc-studio epic

# Generate User Stories
/sdlc-studio story

# Create test specifications
/sdlc-studio test-spec

# Generate executable tests
/sdlc-studio test-automation
```

## Workflows

### Greenfield Project

```
/sdlc-studio prd create        # Interactive PRD creation
/sdlc-studio persona           # Define user personas
/sdlc-studio epic              # Generate Epics
/sdlc-studio story             # Generate Stories
/sdlc-studio test-strategy     # Define test approach
/sdlc-studio test-spec         # Generate test specs
/sdlc-studio test-automation   # Generate executable tests
```

### Brownfield Project

```
/sdlc-studio prd generate      # Reverse-engineer PRD from code
/sdlc-studio persona generate  # Infer personas from codebase
/sdlc-studio epic              # Generate Epics
/sdlc-studio story             # Generate Stories
/sdlc-studio test-strategy generate  # Infer from existing tests
/sdlc-studio test-spec generate      # Reverse-engineer from tests
/sdlc-studio test-automation   # Fill test gaps
```

## Output Structure

All artifacts are created in the `sdlc-studio/` directory:

```
sdlc-studio/
  prd.md                      # Product Requirements Document
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

## Documentation

- [SKILL.md](.claude/skills/sdlc-studio/SKILL.md) - Full command reference
- [reference.md](.claude/skills/sdlc-studio/reference.md) - Detailed workflows for requirements
- [reference-testing.md](.claude/skills/sdlc-studio/reference-testing.md) - Testing workflows
- [best-practices/](.claude/skills/sdlc-studio/best-practices/) - Quality guidelines

## Best Practices

The skill includes best practice guides for creating quality artifacts:

| Creating... | Check |
|-------------|-------|
| Python script | `best-practices/python.md` then `best-practices/script.md` |
| Bash script | `best-practices/script.md` |
| README file | `best-practices/readme.md` |
| Documentation | `best-practices/documentation.md` |
| Claude skill | `best-practices/skill.md` |
| Claude command | `best-practices/command.md` |

## Getting Help

```bash
/sdlc-studio help              # Show command reference
/sdlc-studio prd help          # PRD-specific help
/sdlc-studio test-spec help    # Test specification help
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this project.

## Licence

This project is licensed under the MIT Licence - see the [LICENSE](LICENSE) file for details.
