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
- **Fetch before trusting local state.** A local clone can be behind its remote; planning or
  allocating ids against a stale checkout risks minting an id the remote already used or planning
  over an artefact a teammate has changed. `sprint plan` runs a `git fetch origin` + origin-drift
  pre-flight (skipped gracefully with no remote; warns when behind, refuses under `--strict`), and
  id allocation is remote-aware. When in doubt, `git fetch` and rebase before a batch.

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
| `.claude/skills/sdlc-studio/reference-*.md` | Domain-specific workflows (50+ files) |
| `.claude/skills/sdlc-studio/help/` | Type-specific help (nearly 40 files) |
| `.claude/skills/sdlc-studio/lessons/` | Cross-project lessons registry (v1.7.0) |
| `.claude/skills/sdlc-studio/templates/` | Document and code templates, incl. `agent-instructions.md` (tool-neutral `AGENTS.md`/`CLAUDE.md` starter for consuming projects) and `personas/persona-template.md` (personas are generated on demand from archetype seeds, not baked - RFC0007) |
| `.claude/skills/sdlc-studio/scripts/` | 40+ skill-internal Python helpers sharing `lib/sdlc_md.py`. **`reference-scripts.md` is the catalogue - read it before hand-doing a mechanical task.** Load-bearing ones an agent reaches for constantly: `artifact.py` (create/close an artefact - collision-free id + index row; never hand-author `_index.md`), `file_finding.py` (file a Bug/CR/RFC from a finding), `next_id.py` (allocate an id), `reconcile.py` (`detect` read-only + `apply` mechanical fixes), `validate.py` (structure + status-vocab), `transition.py` (gated status change), `verify_ac.py` (executable ACs), `status.py`, `audit.py`, `critic.py`, `conformance.py`, `doc_freshness.py` |
| `.claude/skills/sdlc-studio/best-practices/` | Quality guidelines (19 files) |
| `tools/` | Repo CI guards (run via `npm run lint`, or directly - see "Testing the Skill"): `lint-style.sh`, `check_links.py`, `validate_skill.py`, `check_versions.py`, `check_budgets.py`, `check_neutrality.py`, plus `style-allowlist.txt` |

## Forward-porting to the installed copy

Never run `install.sh` from the dev repo (its sweep clobbers the git-tracked
working tree). To mirror the repo's skill tree into the installed copy
(`~/.claude/skills/sdlc-studio`) use the guarded wrapper - dry-run by default,
`--yes` to apply, wrong direction or a non-dev-repo cwd refused:

```bash
bash tools/forward-port.sh          # show the itemised diff
bash tools/forward-port.sh --yes    # apply (.local and __pycache__ untouched)
bash tools/forward-port.sh --check  # exit non-zero if the copy has drifted
```

`--check` is the drift gate. The installed copy is what every other project on
this machine loads, so the window between a fix landing here and the mirror
running is a window in which a fix believed shipped is in force nowhere. The
check writes nothing, prints the itemised list and the count of differing files,
and exits non-zero when that count is not zero. Two states are reported rather
than failed: no installed copy at the target path, and a copy holding a
`.local/forward-port.pin` marker - a machine that deliberately does not mirror
is not held to a drift verdict.

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

**Budget the time.** The unit suites are the one slow guard (~2.5 min), which is longer
than the 2-minute default of most tooling - give a commit at least a 10-minute timeout.
The hook prints the expected duration from its own recorded history before it starts, and
**skips** the unit suites entirely (saying so) for a commit touching no `scripts/`,
`templates/`, or `tools/` file.

With npm: `npm run lint` (markdown + all guards) and `npm test` (the script suite).

**Without npm (it is not always on PATH):** every check except markdownlint is a
plain Python/bash command you can run directly. Do not skip the gate because
`npm` is missing.

| Guard | Command | Catches |
| --- | --- | --- |
| Style | `bash tools/lint-style.sh` | em-dash (U+2014), corporate jargon, American spellings, internal provenance tags in consuming-facing files |
| Links | `python3 tools/check_links.py` | broken markdown anchor links |
| Skill spec | `python3 tools/validate_skill.py` | SKILL.md frontmatter |
| Versions | `python3 tools/check_versions.py` | version-string drift across authoritative files |
| Budgets | `python3 tools/check_budgets.py` | a reference file over its declared line ceiling |
| Neutrality | `python3 tools/check_neutrality.py` | a private consuming-project name leaking into a tracked file |
| Skill tests | `python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests` | every shipped skill-script unit test |
| Tool tests | `python3 -m unittest discover -s tools/tests` | every repo-only `tools/` checker unit test (kept out of the shipped payload) |
| Drift | `python3 .claude/skills/sdlc-studio/scripts/reconcile.py detect` | index / status / count drift in the dogfooded `sdlc-studio/` workspace |

One lane is deliberately **not** in the gate. `npm run lint:corpus`
(`tools/lint_corpus.py`) lints every tracked markdown file under the strict root
rule set - dot-directories included, which no `**/*.md` glob can reach - and
attributes each finding against the latest tag, so the report says what the
release introduced rather than reciting the backlog. It runs from a scheduled CI
job and by hand before a release; the gate above is already over its time budget
and a guard whose cost is paid on every commit gets switched off.

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

## Non-negotiable gates

**No ad-hoc coding: delivery flows through stories and sprints.** Work becomes a
story or a bug with acceptance criteria before it becomes a diff. A request (CR or
RFC) is not work until `refine` decomposes it into sized units - that is the
two-backlog rule, and this repo is held to it like any consuming project. A change
that arrives without a unit behind it is the failure the engagement floor exists to
catch.

**Review is independent of the author.** Whoever wrote the change never records its
sign-off. Two roles, never merged: an **adversarial reviewer** (a fresh context that
did not write the code) files findings as evidence, and a **reviewer of record** - the
operator, or a named delegate in a separate trust boundary - approves. This repo sets
`review.two_role_after` in `sdlc-studio/.config.yaml`, so a unit past that number holds
at Review until that sign-off lands. A delegate the author controls does not satisfy
this, which is the whole point of the trust boundary.

## Style Requirements

**Enforced by `tools/lint-style.sh`** (run it, or `npm run lint`, before committing;
it has no code-span or "I am only quoting the rule" exception):

- British English (analyse, colour, behaviour) - a bounded American-spelling list is auto-checked; allowlist genuine exceptions (API identifiers, quotations)
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
