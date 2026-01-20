```text
  _____ ____  _     _____   _____ _             _ _
 / ____|  _ \| |   / ____| / ____| |           | (_)
| (___ | | | | |  | |     | (___ | |_ _   _  __| |_  ___
 \___ \| | | | |  | |      \___ \| __| | | |/ _` | |/ _ \
 ____) | |_| | |__| |____  ____) | |_| |_| | (_| | | (_) |
|_____/|____/|_____\_____||_____/ \__|\__,_|\__,_|_|\___/

      From PRD to Quality, Fully Tested Code
```

[![MIT Licence](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)

A Claude Code skill for managing the full software development lifecycle.

## Features

- **PRD Management** - Create, generate from codebase, or update Product Requirements Documents
- **TRD Management** - Create, generate from codebase, or update Technical Requirements Documents
- **Epic Generation** - Group features into manageable Epics with acceptance criteria
- **Story Breakdown** - Generate User Stories with Given/When/Then acceptance criteria
- **Persona Creation** - Define or infer user personas from codebase patterns
- **Bug Tracking** - Report, list, fix, verify, and close bugs with traceability
- **Code Workflows** - Plan, implement, review, and check code against requirements
- **Test Strategy Document (TSD)** - Document project-level testing approach
- **Test Specifications** - Consolidated test specs with embedded fixtures
- **Test Automation** - Generate executable tests for pytest, Jest, Vitest, Go, and more
- **Test Execution** - Run tests with traceability to stories and epics
- **Workflow Automation** - Execute stories through 7 phases or epics in dependency order
- **Status & Hints** - Check pipeline state and get single actionable next steps

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

# Generate TRD from codebase
/sdlc-studio trd generate

# Create Epics from PRD
/sdlc-studio epic

# Generate User Stories
/sdlc-studio story

# Report a bug
/sdlc-studio bug

# Plan implementation for a story
/sdlc-studio code plan

# Execute implementation plan
/sdlc-studio code implement

# Execute full story workflow (7 phases)
/sdlc-studio story implement --story US0001

# Create test specifications
/sdlc-studio test-spec

# Generate executable tests
/sdlc-studio test-automation

# Run tests for an epic
/sdlc-studio code test --epic EP0001

# Get single actionable next step
/sdlc-studio hint
```

## Workflows

### Greenfield Project

```bash
/sdlc-studio prd create        # Interactive PRD creation
/sdlc-studio trd create        # Define technical requirements
/sdlc-studio persona           # Define user personas
/sdlc-studio epic              # Generate Epics
/sdlc-studio story             # Generate Stories
/sdlc-studio tsd               # Define test strategy
/sdlc-studio test-spec         # Generate test specs
/sdlc-studio test-automation   # Generate executable tests
# Or use workflow automation
/sdlc-studio story implement --story US0001  # Single story, all phases
```

### Brownfield Project

```bash
/sdlc-studio prd generate      # Reverse-engineer PRD from code
/sdlc-studio trd generate      # Generate TRD from codebase
/sdlc-studio persona generate  # Infer personas from codebase
/sdlc-studio epic              # Generate Epics
/sdlc-studio story             # Generate Stories
/sdlc-studio tsd generate      # Infer test strategy from existing tests
/sdlc-studio test-spec generate      # Reverse-engineer from tests
/sdlc-studio test-automation   # Fill test gaps
```

### Development Cycle

```bash
/sdlc-studio code plan         # Plan implementation for story
/sdlc-studio code implement    # Execute the plan
/sdlc-studio code review       # Review implementation
/sdlc-studio code test         # Run tests with traceability
```

## Output Structure

All artifacts are created in the `sdlc-studio/` directory:

```text
sdlc-studio/
  prd.md                      # Product Requirements Document
  trd.md                      # Technical Requirements Document
  tsd.md                      # Test Strategy Document
  personas.md                 # User Personas
  epics/
    _index.md                 # Epic registry
    EP0001-*.md               # Epic files
  stories/
    _index.md                 # Story registry
    US0001-*.md               # Story files
  bugs/
    _index.md                 # Bug registry
    BG0001-*.md               # Bug files
  plans/
    _index.md                 # Plan registry
    PL0001-*.md               # Implementation plans
  test-specs/
    _index.md                 # Spec registry
    TSP0001-*.md              # Test Specifications
  workflows/
    _index.md                 # Workflow registry
    WF0001-*.md               # Workflow tracking files

tests/                        # Generated test code
  unit/
  integration/
  api/
  e2e/
```

## Documentation

- [SKILL.md](.claude/skills/sdlc-studio/SKILL.md) - Full command reference
- [reference-philosophy.md](.claude/skills/sdlc-studio/reference-philosophy.md) - Create vs Generate modes (read first)
- [reference-*.md](.claude/skills/sdlc-studio/) - Domain-specific workflows (13 files)
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
