# CLAUDE.md

Guidance for Claude Code when working with this repository.

## Project Overview

SDLC Studio is a Claude Code skill for managing the full software development lifecycle - from PRD creation through Epic decomposition, User Story generation, implementation planning, and test automation.

**This is a Claude Code skill** installed to `.claude/skills/sdlc-studio/`.

## Skill Structure

| Path | Purpose |
|------|---------|
| `.claude/skills/sdlc-studio/SKILL.md` | Main entry point (307 lines) |
| `.claude/skills/sdlc-studio/reference.md` | PRD, TRD, Epic, Story, Persona workflows |
| `.claude/skills/sdlc-studio/reference-code.md` | Code plan, implement, review workflows |
| `.claude/skills/sdlc-studio/reference-testing.md` | Test Strategy, Spec, Automation workflows |
| `.claude/skills/sdlc-studio/help/` | Type-specific help (16 files) |
| `.claude/skills/sdlc-studio/templates/` | Document and code templates (22 files) |
| `.claude/skills/sdlc-studio/best-practices/` | Quality guidelines (11 files) |

## Testing the Skill

No automated tests. To verify manually:

1. Install: `cp -r .claude/skills/sdlc-studio ~/.claude/skills/`
2. Run `/sdlc-studio help` - displays command reference
3. Run `/sdlc-studio status` - shows pipeline state

## Development Guidelines

When modifying the skill:

- **SKILL.md:** Keep under 500 lines (currently 307)
- **New commands:** Add help file to `help/`, update SKILL.md tables
- **New templates:** Add to `templates/`, update See Also section
- **Workflows:** Update relevant `reference*.md` file

## Style Requirements

- British English (analyse, colour, behaviour)
- No em dashes - use en dash with spaces or restructure
- No corporate jargon (synergy, leverage, robust)
- Dense, economical writing
- `{{placeholder}}` syntax in templates

## Best Practices

Check the relevant guide before creating artifacts:

| Creating... | Check |
|-------------|-------|
| Python script | `best-practices/python.md` then `script.md` |
| Bash script | `best-practices/script.md` |
| Documentation | `best-practices/documentation.md` |
| Claude skill | `best-practices/skill.md` |

## Related

- [README.md](README.md) - Installation and quick start
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
