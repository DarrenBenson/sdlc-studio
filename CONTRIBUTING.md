# Contributing to SDLC Studio

Thank you for your interest in contributing to SDLC Studio.

## How to Contribute

### Reporting Issues

- Use GitHub Issues to report bugs or suggest features
- Include clear steps to reproduce any bugs
- Provide context about your environment and use case

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run any relevant tests
5. Commit with a clear message
6. Push to your fork
7. Open a Pull Request

### Code Style

This project follows specific writing and code conventions:

#### Writing Style

- **British English** throughout (analyse, colour, behaviour)
- **No em dashes** - use en dash with spaces or restructure sentences
- **No corporate jargon** - avoid words like synergy, leverage, robust, journey
- **Dense, economical writing** - be concise

#### Documentation

- Follow the best practices in `.claude/skills/sdlc-studio/best-practices/`
- Use Markdown with consistent header hierarchy
- Include examples for complex concepts

#### Skill Structure

When modifying the skill:

- Keep SKILL.md under 500 lines
- Use progressive disclosure (reference.md for detailed docs)
- Maintain the `{{placeholder}}` syntax in templates
- Update help files when changing commands

### Best Practices

Before submitting changes, review the relevant best practice guide:

| Changing... | Check |
|-------------|-------|
| Main skill file | `best-practices/skill.md` |
| Documentation | `best-practices/documentation.md` |
| README | `best-practices/readme.md` |
| Templates | Template conventions in skill.md |

### Testing Changes

- Test the skill locally before submitting
- Verify commands work: `/sdlc-studio help`, `/sdlc-studio status`
- Check that templates render correctly
- Ensure all internal links work

## Questions?

If you have questions about contributing, open an issue for discussion.
