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

## What is This?

SDLC Studio is a **skill** (plugin) for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), Anthropic's official CLI tool for working with Claude. It adds commands that help you manage the entire software development process:

- Write Product Requirements Documents (PRDs)
- Break work into Epics and User Stories
- Plan and implement code changes
- Generate and run tests
- Track bugs

**New to Claude Code?** You'll need to [install Claude Code](https://docs.anthropic.com/en/docs/claude-code/getting-started) first before installing this skill.

## Prerequisites

Before installing SDLC Studio, ensure you have:

| Requirement | How to check | Install guide |
|-------------|--------------|---------------|
| Claude Code | Run `claude --version` | [Getting Started](https://docs.anthropic.com/en/docs/claude-code/getting-started) |
| curl or wget | Run `curl --version` | Usually pre-installed on macOS/Linux |

## Installation

### Option 1: One-line installer (recommended)

Open your terminal and run:

```bash
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash
```

This installs SDLC Studio globally, making it available in all your projects.

**What this does:**
1. Downloads the latest version from GitHub
2. Creates `~/.claude/skills/` if it doesn't exist
3. Installs the skill files

### Option 2: Install for a single project only

If you only want the skill available in one project:

```bash
cd /path/to/your/project
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash -s -- --local
```

This creates `.claude/skills/sdlc-studio/` in your current directory.

### Option 3: Install a specific version

```bash
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash -s -- --version v1.1.0
```

### Option 4: Manual installation

If you prefer not to use the installer script:

```bash
# Clone the repository
git clone https://github.com/DarrenBenson/sdlc-studio.git
cd sdlc-studio

# Copy to your Claude Code skills directory
mkdir -p ~/.claude/skills
cp -r .claude/skills/sdlc-studio ~/.claude/skills/
```

## Verify Installation

After installing, verify it works:

1. **Start Claude Code** in any project directory:
   ```bash
   cd /path/to/any/project
   claude
   ```

2. **Run the help command** inside Claude Code:
   ```
   /sdlc-studio help
   ```

   You should see a list of available commands.

3. **Check the status**:
   ```
   /sdlc-studio status
   ```

   This shows the current state of your SDLC pipeline (empty for a new project).

## Quick Start

Once installed, here's how to get started inside Claude Code:

### First time? Check the status

```
/sdlc-studio status
```

This shows what artifacts exist and suggests next steps.

### Don't know what to do next?

```
/sdlc-studio hint
```

This gives you a single, actionable next step based on your project's current state.

### Starting a new project?

```
/sdlc-studio prd create
```

Claude will ask you questions about your project and create a Product Requirements Document.

### Have existing code?

```
/sdlc-studio prd generate
```

Claude analyses your codebase and creates a PRD based on what it finds.

## Common Commands

| Command | What it does |
|---------|--------------|
| `/sdlc-studio help` | Show all available commands |
| `/sdlc-studio status` | Show pipeline state and progress |
| `/sdlc-studio hint` | Get a single suggested next action |
| `/sdlc-studio prd create` | Create a new PRD interactively |
| `/sdlc-studio prd generate` | Generate PRD from existing code |
| `/sdlc-studio epic` | Generate Epics from your PRD |
| `/sdlc-studio story` | Generate User Stories from Epics |
| `/sdlc-studio code plan` | Plan implementation for a story |
| `/sdlc-studio code implement` | Execute your implementation plan |
| `/sdlc-studio bug` | Report a new bug |

## Workflows

### New Project (Greenfield)

Follow this sequence to build from scratch:

```
/sdlc-studio prd create        # 1. Define what you're building
/sdlc-studio trd create        # 2. Define technical approach
/sdlc-studio persona           # 3. Define who will use it
/sdlc-studio epic              # 4. Break into Epics
/sdlc-studio story             # 5. Break into Stories
/sdlc-studio tsd               # 6. Define test strategy
/sdlc-studio test-spec         # 7. Create test specifications
/sdlc-studio code plan         # 8. Plan first story
/sdlc-studio code implement    # 9. Build it
```

### Existing Project (Brownfield)

Use `generate` to reverse-engineer documentation from code:

```
/sdlc-studio prd generate      # Analyse code, create PRD
/sdlc-studio trd generate      # Document technical decisions
/sdlc-studio persona generate  # Infer users from code
/sdlc-studio epic              # Create Epics for future work
/sdlc-studio story             # Break into Stories
```

### Daily Development

```
/sdlc-studio code plan         # Plan your changes
/sdlc-studio code implement    # Make the changes
/sdlc-studio code review       # Review what you built
/sdlc-studio code test         # Run tests
```

## Output Structure

SDLC Studio creates a `sdlc-studio/` directory in your project:

```
sdlc-studio/
  prd.md                      # Product Requirements Document
  trd.md                      # Technical Requirements Document
  tsd.md                      # Test Strategy Document
  personas.md                 # User Personas
  epics/
    _index.md                 # Epic registry
    EP0001-*.md               # Individual Epic files
  stories/
    _index.md                 # Story registry
    US0001-*.md               # Individual Story files
  bugs/
    _index.md                 # Bug registry
    BG0001-*.md               # Individual Bug files
  plans/
    _index.md                 # Plan registry
    PL0001-*.md               # Implementation plans
  test-specs/
    _index.md                 # Spec registry
    TSP0001-*.md              # Test Specifications

tests/                        # Generated test code (in project root)
  unit/
  integration/
  api/
  e2e/
```

## Troubleshooting

### "Command not found" when running /sdlc-studio

The skill isn't installed correctly. Check:

1. **Is the skill in the right place?**
   ```bash
   ls ~/.claude/skills/sdlc-studio/SKILL.md
   ```
   If this file doesn't exist, reinstall.

2. **For project-level installs**, check:
   ```bash
   ls .claude/skills/sdlc-studio/SKILL.md
   ```

3. **Try reinstalling**:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash
   ```

### Installer fails to download

Check your internet connection and that you can access GitHub:
```bash
curl -I https://github.com/DarrenBenson/sdlc-studio
```

If you're behind a corporate proxy, you may need to configure proxy settings.

### Commands run but nothing happens

Make sure you're running commands **inside Claude Code**, not in your regular terminal. Start Claude Code first:
```bash
claude
```
Then type the `/sdlc-studio` commands at the Claude Code prompt.

## Updating

To update to the latest version, simply run the installer again:

```bash
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash
```

The installer removes the old version before installing the new one.

## Uninstalling

### Global installation

```bash
rm -rf ~/.claude/skills/sdlc-studio
```

### Project-level installation

```bash
rm -rf .claude/skills/sdlc-studio
```

## Getting Help

Inside Claude Code:

```
/sdlc-studio help              # Show all commands
/sdlc-studio prd help          # Help for PRD commands
/sdlc-studio epic help         # Help for Epic commands
/sdlc-studio test-spec help    # Help for test specification
```

## Documentation

- [SKILL.md](.claude/skills/sdlc-studio/SKILL.md) - Full command reference
- [reference-philosophy.md](.claude/skills/sdlc-studio/reference-philosophy.md) - Create vs Generate modes (read first)
- [reference-*.md](.claude/skills/sdlc-studio/) - Domain-specific workflows
- [best-practices/](.claude/skills/sdlc-studio/best-practices/) - Quality guidelines

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Licence

MIT Licence - see [LICENSE](LICENSE) for details.
