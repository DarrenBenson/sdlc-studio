# AGENTS.md

Guidance for coding agents working on this repository. Claude Code
reads this via the `@AGENTS.md` import in [CLAUDE.md](CLAUDE.md);
Codex, Copilot, Cursor, Gemini, and others read it directly.

## Project Overview

SDLC Studio is an agent skill (the [Agent Skills](https://agentskills.io)
open format) for managing the full software development lifecycle - from
PRD creation through Epic decomposition, User Story generation,
implementation planning, and test automation.

SDLC Studio enables **Goal-Driven Development**: set a goal and acceptance
criteria, and the agent drives the proven lifecycle to it (TDD -> BDD ->
Eval-Driven -> Goal-Driven). The `autosprint` command runs it and closes every
run with a reconcile and review.

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
| `.claude/skills/sdlc-studio/templates/` | Document and code templates, incl. `agent-instructions.md` (tool-neutral `AGENTS.md`/`CLAUDE.md` starter for consuming projects) and `personas/persona-template.md` (personas are generated on demand from archetype seeds, not baked - RFC0007) |
| `.claude/skills/sdlc-studio/scripts/` | 40+ skill-internal Python helpers sharing `lib/sdlc_md.py`. **`reference-scripts.md` is the catalogue - read it before hand-doing a mechanical task.** Load-bearing ones an agent reaches for constantly: `artifact.py` (create/close an artefact - collision-free id + index row; never hand-author `_index.md`), `file_finding.py` (file a Bug/CR/RFC from a finding), `next_id.py` (allocate an id), `reconcile.py` (`detect` read-only + `apply` mechanical fixes), `validate.py` (structure + status-vocab), `transition.py` (gated status change), `verify_ac.py` (executable ACs), `status.py`, `audit.py`, `critic.py`, `conformance.py`, `doc_freshness.py` |
| `.claude/skills/sdlc-studio/best-practices/` | Quality guidelines (19 files) |
| `tools/` | Repo CI guards (run via `npm run lint`, or directly - see "Testing the Skill"): `lint-style.sh`, `check_links.py`, `validate_skill.py`, `check_versions.py`, `check_budgets.py`, `check_neutrality.py`, plus `style-allowlist.txt` |

## Soft Dependencies (runtime)

Some features need external tools on PATH:

| Feature | Requires | Notes |
| --- | --- | --- |
| `cr sync`, `story sync`, `project sync` | `gh` CLI authenticated | No PyGitHub dependency; all calls routed through gh |
| `reconcile --verify` | `pytest`, `jest`, `vitest`, `go`, `curl`, `jq`, `rg` (whichever your AC verifiers reference) | Only the tools your Verify lines invoke need to be installed |
| `repo map build` | Python 3.10+ | Pure stdlib; no ctags or tree-sitter needed |

## Testing the Skill

**Enable the pre-commit hook once per clone: `bash tools/enable-hooks.sh`.** It runs
the whole gate below on every commit and blocks a breaking one, printing for each
failure what the guard enforces, the offending line, and how to fix it. This makes
the gate un-skippable rather than something an agent has to remember (emergency
bypass: `git commit --no-verify`). Everything below is what it runs; run any of it
by hand too.

**Run the full gate before every commit, not just before a release tag.** CI runs
these same checks; skipping them locally is how style, neutrality, budget, and
link breakage reaches `main`. Each guard below has caught a real breakage that the
unit tests do not.

With npm: `npm run lint` (markdown + all guards) and `npm test` (the script suite).

**Without npm (it is not always on PATH):** every check except markdownlint is a
plain Python/bash command you can run directly. Do not skip the gate because
`npm` is missing.

| Guard | Command | Catches |
| --- | --- | --- |
| Style | `bash tools/lint-style.sh` | em-dash (U+2014), corporate jargon, internal provenance tags in consuming-facing files |
| Links | `python3 tools/check_links.py` | broken markdown anchor links |
| Skill spec | `python3 tools/validate_skill.py` | SKILL.md frontmatter |
| Versions | `python3 tools/check_versions.py` | version-string drift across authoritative files |
| Budgets | `python3 tools/check_budgets.py` | a reference file over its declared line ceiling |
| Neutrality | `python3 tools/check_neutrality.py` | a private consuming-project name leaking into a tracked file |
| Scripts | `python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests` | every script and checker unit test |
| Drift | `python3 .claude/skills/sdlc-studio/scripts/reconcile.py detect` | index / status / count drift in the dogfooded `sdlc-studio/` workspace |

Only `lint:md` (markdownlint) needs Node; the rest are stdlib Python or bash.
`markdownlint-cli` is a devDependency, so `npm install` provides it at
`node_modules/.bin/markdownlint` and the pre-commit hook runs it from there (no
global install needed). If Node is absent the hook prints a visible SKIP for
markdown and CI still enforces it, so a markdown-mechanics error (e.g. MD032,
blank lines around lists) can pass a Node-less machine and fail on push - run
`npm install` to close that gap. A change that touches a `reference-*.md` line
count, an artefact status, prose style, or any consuming-project name must pass the
relevant guard; none are optional.

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
- **Use the deterministic tooling - never hand-roll what it wires:** create artifacts with
  `scripts/artifact.py new` / `batch` (collision-free id + index row + epic wiring); never
  hand-author `_index.md` or hand-allocate ids; the index is derived (`reconcile` syncs it);
  a story reaches Done only when its executable ACs pass (`transition -> Done` is gated).
  This is the discipline the shipped `agent-instructions.md` enforces for consuming projects
  (CR0083) - dogfooded here.

## Style Requirements

**Enforced by `tools/lint-style.sh`** (run it, or `npm run lint`, before committing;
it has no code-span or "I am only quoting the rule" exception):

- British English (analyse, colour, behaviour) - spelling not yet auto-checked (CR0135)
- No em dashes (U+2014) - use a hyphen with spaces, or restructure
- No corporate jargon (synergy, leverage, robust, journey), allowlist in `tools/style-allowlist.txt`
- No internal provenance tags like `(CR1234)` in consuming-facing `reference-*.md` / `help/` / `scripts/`
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
