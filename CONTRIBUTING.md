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
- Use progressive disclosure (reference-*.md files for detailed docs)
- Maintain the `{{placeholder}}` syntax in templates
- Update help files when changing commands

### Best Practices

Before submitting changes, review the relevant best practice guide:

| Changing... | Check |
| ------------- | ------- |
| Main skill file | `best-practices/claude-skill.md` |
| Documentation | `best-practices/documentation.md` |
| README | `best-practices/readme-guide.md` |
| Templates | Template conventions in claude-skill.md |

### Testing Changes

- Test the skill locally before submitting
- Verify commands work: `/sdlc-studio help`, `/sdlc-studio status`
- Check that templates render correctly
- Ensure all internal links work

## Development Workflow

SDLC Studio dogfoods itself - it is built with its own lifecycle. A few non-negotiables:

- **Setup:** Node (for the markdown lint suite) + Python 3.10+ (for the scripts and their tests).
  Run `npm install` once; the Python scripts are pure stdlib (nothing to pip install).
- **Gate every commit.** Before each commit, all three must pass:
  `npm run lint && npm test && python3 .claude/skills/sdlc-studio/scripts/gate.py --root .`
  Lint covers markdown, house style, links, SKILL.md, versions, budgets, and the neutrality guard;
  the gate covers conformance, reconcile drift, validation, integrity, duplicate ids, and docs.
- **Trunk-based, small green units.** Commit to `main` in small, individually-green increments; CI
  re-runs the same gate on push, plus a coverage floor (>= 80% of the runtime scripts) and a
  `bandit` security scan. Branches are for isolation, not ceremony.
- **Paperwork in the same commit.** Every behaviour or doc change carries its `CHANGELOG.md`
  `[Unreleased]` entry and any help/reference update in the same commit.
- **Bug to CR to RFC lifecycle.** Track work as artifacts created and closed with
  `scripts/artifact.py` (`BG` bugs, `CR` change requests, `RFC` design exploration; globally
  numbered). A change request implements a concrete improvement; a bug fixes something broken; an
  RFC explores an unsettled design before either.
- **Every bug ships a regression test.** A fix is not done until a test would catch the bug's return.
- **Forward-port skill edits.** Changes under `.claude/skills/sdlc-studio/` are mirrored to each
  install target (see `install.sh --list-targets`); verify the installed copy matches the repo.

## Architecture

Start with `AGENTS.md` (the operating doctrine) and
`.claude/skills/sdlc-studio/best-practices/architecture.md`. The skill is a lean always-loaded
router (`SKILL.md`) plus on-demand `reference-*.md` workflows, `help/` command docs, `templates/`,
and stdlib Python helpers in `scripts/` (sharing `scripts/lib/sdlc_md.py`). Repo CI checks live in
`tools/`. Volatile project state lives in `sdlc-studio/reviews/LATEST.md` - read it first.

## Questions?

If you have questions about contributing, open an issue for discussion.
