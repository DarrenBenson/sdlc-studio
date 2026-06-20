# AGENTS.md

Guidance for coding agents working on this repository. Claude Code
reads this via the `@AGENTS.md` import in [CLAUDE.md](CLAUDE.md);
Codex, Copilot, Cursor, Gemini, and others read it directly.

## Project Overview

SDLC Studio is an agent skill (the [Agent Skills](https://agentskills.io)
open format) for managing the full software development lifecycle - from
PRD creation through Epic decomposition, User Story generation,
implementation planning, and test automation.

**The skill source lives at `.claude/skills/sdlc-studio/`** and installs
to each tool's skill directory (see `install.sh --list-targets`).

## Orientation & Current State

This repo dogfoods the skill against its own source. Durable guidance lives in
this file; volatile project state - what exists, what is in flight, known
divergences, next steps - lives in `sdlc-studio/reviews/LATEST.md`, so the two do
not drift (progressive disclosure).

- **At session start, and after any context reset or compaction:** re-read
  `sdlc-studio/reviews/LATEST.md` and run `/sdlc-studio status` before acting, to
  re-anchor on where the pipeline is.

## Skill Structure

| Path | Purpose |
| ------ | --------- |
| `.claude/skills/sdlc-studio/SKILL.md` | Main entry point / lean router (~200 lines) |
| `.claude/skills/sdlc-studio/reference-philosophy.md` | Create vs Generate modes - read first |
| `.claude/skills/sdlc-studio/reference-doctrine.md` | Operating doctrine - onboard an agent to any project (v1.7.0) |
| `.claude/skills/sdlc-studio/reference-outputs.md` | Canonical story and epic completion cascades |
| `.claude/skills/sdlc-studio/reference-project.md` | Full-PRD orchestration (`project plan` and `project implement`) |
| `.claude/skills/sdlc-studio/reference-cr.md` | Change request lifecycle (plus `cr sync` for GitHub) |
| `.claude/skills/sdlc-studio/reference-rfc.md` | RFC design-exploration lifecycle (v1.7.0) |
| `.claude/skills/sdlc-studio/reference-reconcile.md` | Census-based drift detection, `--verify` delegates to verify_ac.py |
| `.claude/skills/sdlc-studio/reference-agentic-lessons.md` | Production patterns plus per-project lessons accumulation |
| `.claude/skills/sdlc-studio/reference-operator-heuristics.md` | Cross-cutting operator patterns for live services (v1.7.0) |
| `.claude/skills/sdlc-studio/reference-deploy-readiness.md` | Post-deploy verification patterns (v1.7.0) |
| `.claude/skills/sdlc-studio/reference-plan-files.md` | Claude Code plan-file lifecycle (v1.7.0) |
| `.claude/skills/sdlc-studio/reference-workflow-personas.md` | Three Amigos consultation model |
| `.claude/skills/sdlc-studio/reference-repo-map.md` | AST repo indexer design (v1.6.0) |
| `.claude/skills/sdlc-studio/reference-verify.md` | Executable AC verifier DSL (v1.6.0) |
| `.claude/skills/sdlc-studio/reference-github-sync.md` | GitHub Issues two-way sync (v1.6.0) |
| `.claude/skills/sdlc-studio/reference-scripts.md` | Scripts directory convention (v1.6.0) |
| `.claude/skills/sdlc-studio/reference-*.md` | Domain-specific workflows (42 files total) |
| `.claude/skills/sdlc-studio/help/` | Type-specific help (31 files) |
| `.claude/skills/sdlc-studio/lessons/` | Cross-project lessons registry (v1.7.0) |
| `.claude/skills/sdlc-studio/templates/` | Document and code templates (72 files), incl. `agent-instructions.md` (tool-neutral `AGENTS.md`/`CLAUDE.md` starter for consuming projects) |
| `.claude/skills/sdlc-studio/scripts/` | Skill-internal Python helpers: `repo_map`, `verify_ac`, `github_sync`, plus read-only JSON helpers `reconcile`, `status`, `validate`, `next_id`, `review_prep`, plus `plan` and `lessons` managers, sharing `lib/sdlc_md.py` |
| `.claude/skills/sdlc-studio/best-practices/` | Quality guidelines (19 files) |
| `tools/` | Repo CI checks: `check_links.py`, `lint-style.sh`, `validate_skill.py` |

## Soft Dependencies (runtime)

Some features need external tools on PATH:

| Feature | Requires | Notes |
| --- | --- | --- |
| `cr sync`, `story sync`, `project sync` | `gh` CLI authenticated | No PyGitHub dependency; all calls routed through gh |
| `reconcile --verify` | `pytest`, `jest`, `vitest`, `go`, `curl`, `jq`, `rg` (whichever your AC verifiers reference) | Only the tools your Verify lines invoke need to be installed |
| `repo map build` | Python 3.10+ | Pure stdlib; no ctags or tree-sitter needed |

## Testing the Skill

Markdown: `npm run lint` runs markdownlint, the style guard, the
anchor-link checker, and the SKILL.md frontmatter validator.

Scripts: `npm test` (or `python3 -m unittest discover -s
.claude/skills/sdlc-studio/scripts/tests`) runs the unit tests for
every script in `scripts/` and every checker in `tools/`. All tests
must pass before a release is tagged.

Manual verification:

1. Install: `./install.sh --local` (or `cp -r .claude/skills/sdlc-studio <tool skills dir>`)
2. Run `/sdlc-studio help` - displays command reference
3. Run `/sdlc-studio status` - shows pipeline state
4. Run `/sdlc-studio repo map build` - produces .local/repo-map.json
5. Run `/sdlc-studio reconcile --verify --dry-run` against a fixture
   story with Verify lines

## Development Guidelines

When modifying the skill:

- **SKILL.md:** Main entry point / lean router (~200 lines, CI-budgeted
  under 500). It is the only always-loaded file, so keep it minimal:
  philosophy gates, the Progressive Loading Guide, and pointers. Delegate
  the command catalogue to `help/help.md`, flags to `help/arguments.md`,
  the reference index to `help/references.md`, and workflow detail to
  `reference-*.md` rather than inline it.
- **New commands:** Add help file to `help/`, update SKILL.md tables
- **New templates:** Add to `templates/`, update See Also section
- **Workflows:** Update relevant `reference*.md` file
- **Paperwork in the same commit:** every behaviour or doc change carries
  its `CHANGELOG.md` [Unreleased] entry (see `lessons/LL0004`)
- **Recall lessons first:** read `.claude/skills/sdlc-studio/lessons/_index.md`
  before substantive design decisions

## Style Requirements

- British English (analyse, colour, behaviour)
- No em dashes - use en dash with spaces or restructure
- No corporate jargon (synergy, leverage, robust)
- Dense, economical writing
- `{{placeholder}}` syntax in templates

## Best Practices

Check the relevant guide before creating artifacts:

| Creating... | Check |
| ------------- | ------- |
| Python script | `best-practices/python.md` then `script.md` |
| Bash script | `best-practices/script.md` |
| Documentation | `best-practices/documentation.md` |
| Agent skill | `best-practices/claude-skill.md` |

## Related

- [README.md](README.md) - Installation and quick start
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
