# SDLC Studio Reference - Skill Internal Scripts

Runtime helpers that live in the skill's `scripts/` directory and
are invoked by workflow reference files. Claude calls these; users do
not.

<!-- Load when: a reference file instructs invoking a script in scripts/ -->

## Reading Guide

| Section | When to Read |
| --- | --- |
| Locating the skill directory | When running any script example |
| Rationale | When deciding whether a new helper belongs in scripts/ |
| Invocation | When a reference file needs to call a script |
| Contract | When writing or modifying a script |
| Catalogue | When finding an existing helper before writing a new one |

## Locating the Skill Directory {#skill-dir}

Script examples throughout the skill use the form
`python3 "$CLAUDE_SKILL_DIR/scripts/<name>.py"`. Claude Code sets
`$CLAUDE_SKILL_DIR` to this skill's directory at every install level
(personal, project, or plugin). If the variable is not set (another
agent tool, or a shell outside skill execution), substitute the
directory containing this skill's `SKILL.md` - for example
`~/.claude/skills/sdlc-studio`, `~/.agents/skills/sdlc-studio`, or
`.github/skills/sdlc-studio`. The quoted variable fails loudly when
unset; never guess between multiple installed copies.

## Rationale {#scripts-rationale}

SDLC Studio was Claude-native through v1.5.0: every workflow was a
markdown instruction that Claude executed using built-in tools (Read,
Grep, Bash, Edit). v1.6.0 introduces three capabilities that need
deterministic computation:

1. **AST repository indexing** (`repo_map.py`) – reinventing a ranked
   file index every session wastes tokens and drifts.
2. **AC verifier execution** (`verify_ac.py`) – running pytest, curl,
   or shell assertions at scale needs a single entry point that
   parses results and updates story files atomically.
3. **GitHub issue sync** (`github_sync.py`) – diffing local CR/Story
   files against GitHub Issues and writing back needs idempotent
   logic that a script can unit-test.

A later wave extends the same principle - **determinism in scripts,
judgement in Claude** - to the highest-frequency mechanical workflows,
which had been running inside Claude's context:

4. **Drift detection** (`reconcile.py`) – the file census and index-drift
   comparison doctrine rule 3 prescribes is a deterministic algorithm.
5. **Pipeline status** (`status.py`) – the four-pillar census and hint ladder.
6. **Artifact validation** (`validate.py`) – ID/Status/structure linting.
7. **ID allocation** (`next_id.py`) – cross-repo-safe numbering (rule 13).
8. **Review inputs** (`review_prep.py`) – the mechanical inputs the five-leg
   review consumes (staleness, persona usage, counts).

These five are **read-only**: each emits JSON (or writes only to
`.local/`), and Claude consumes it and does the judgement - adjudicating
ambiguous drift, applying body-level edits, and rendering the dashboard or
the review verdict. The census and computation move to the script; the
decision stays with Claude. The five-leg review verdict and the CODE leg in
particular are never scripted - they are irreducibly judgement.

For everything else (reading files, walking directories, simple
transforms) Claude's built-in tools are still the right answer. The
scripts directory is for computation that benefits from being written
once and tested. All scripts share `lib/sdlc_md.py`, the single source of
truth for the markdown conventions (metadata fields, artifact IDs, AC
blocks, the artifact-type and status-vocabulary tables).

## Invocation {#scripts-invocation}

Reference files call scripts via Bash:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/repo_map.py" query \
  --story sdlc-studio/stories/US0001-user-login.md --top 10
```

Always use the absolute path from repo root. Never `cd` into the
scripts directory. Always pass `--dry-run` first when the workflow
explicitly supports it.

## Contract {#scripts-contract}

Every script in `scripts/`:

1. Starts with `#!/usr/bin/env python3` and is executable
2. Uses `argparse` subcommands for commands (e.g. `repo_map.py build`)
3. Supports `--help` on every subcommand
4. Exits non-zero on any failure that should halt the workflow
5. Never mutates files outside `sdlc-studio/.local/` or the files
   passed on the command line. One flagged exception: `plan.py archive`
   moves files under `~/.claude/plans/`, an operator-owned directory
   outside any project - it is the only script that writes outside
   `.local/`, only on that explicit subcommand, and it never deletes
   or overwrites
6. Never fetches network resources except the explicit GitHub CLI
   wrapper, and even then only via the `gh` tool (no token handling)
7. Prints plain text to stdout by default, with `--format json` where
   machine-parseable output matters
8. Has unit tests under `scripts/tests/test_<script>.py`

See `best-practices/script.md` for the shared style rules (shebang,
error handling, CLI flags over config files for small tools).

## Catalogue {#scripts-catalogue}

### `repo_map.py`

Pure-Python repository indexer. Produces
`sdlc-studio/.local/repo-map.json` with per-file symbol lists, imports,
and an in-degree score. Queried by the Agent Prompt Template and
`code plan` workflow to derive `READ THESE FILES FIRST` lists.

- `build`: walk the repo and write the index
- `query`: rank files against a story or free-text query
- `stats`: print index size and top-10 hub files

Full workflow: `reference-repo-map.md`. User-facing help:
`help/repo-map.md`.

### `complexity.py`

Cognitive (SonarSource) + cyclomatic complexity per function from Python's
`ast` (pure stdlib; `lizard` soft-dep for other languages, unscored without
it). Advisory signal for estimation and refactor-first (RFC0009); `repo_map`
emits the same per-function scores into the map.

- `scan`: list functions over the cognitive threshold (`complexity.cognitive_high`, default 15)
- `assess --files ...`: a change's blast-radius difficulty band + refactor-first hotspots (used by `code plan`)

### `provenance.py`

Artifact provenance (CR0052). Makes deterministic creation the *checkable* path: `new`
stamps every artifact (`> **Created-by:** sdlc-studio ...`); `check` flags artifacts past
the `provenance.adopt_after` id cutoff that lack the stamp (hand-authored), with
remediation - advisory by default, `provenance.enforce: true` to block; `remake` content-
preservingly backfills the stamp into un-stamped artifacts (idempotent, dry-run-able,
stamp-only - never re-lays-out content). Standalone + advisory by design (not wired into
the gate); adopting it is a project choice.

### `telemetry.py`

Run telemetry recorder (CR0050, RFC0014 WS1). `record` appends a per-unit run outcome
(id, type, iterations, wall-time, stages, critic verdict, complexity, churn, reopened,
tokens-when-supplied) to the gitignored `sdlc-studio/.local/telemetry.jsonl`. Local-only,
no network, no upload; advisory (a write failure is swallowed, never raised into the loop);
only whitelisted non-None fields are written; `read_all`/`show` skip malformed lines. Feeds
the deferred calibrate step (WS3) and RFC0009 WS5.

### `artifact.py`

Deterministic artifact create + close cascade (CR0045). `new --type <any of the 8 numbered
types> --title ...` allocates a collision-free id, renders a valid scaffold (vocab-correct
status; a story gets a populated AC section), appends the index data-table row (built
generically from that index's own header, so it works for every type), recomputes counts,
and wires a story into its parent epic's Story Breakdown. `close --id` terminal-transitions
by id-prefix with the per-type terminal status (reusing transition). Replaces the ~10-step
hand cascade. Shares `file_finding.append_index_row`.

### `product_reconcile.py`

Cross-repo feature-map traceability (CR0049, RFC0015 WS3). Verifies every product feature
`PF####` in the PVD's §3 table maps to a feature actually DECLARED (a table cell or heading,
not free-text) in its owning repo's PRD, resolving repos via the manifest. Findings:
orphan-feature + unknown-repo + missing-path (blocking); repo-absent + empty-feature-map
(advisory, with an un-verified count so a degraded run is not mistaken for full coverage).
Never silently reads the wrong PRD; exits non-zero on a blocking inconsistency.

### `pvd.py`

PVD projection + drift (CR0048, RFC0015 WS2). `sync` projects the one writable master
Product Vision Document into a child repo read-only (copy in dev, symlink in prod);
`drift` compares a projected copy against the master (in-sync / stale / behind / missing /
error) via sha256 + version. An unreadable/missing master reports `error`, never a vacuous
in-sync. `read_manifest` parses `product-manifest.yaml` (no PyYAML). See `reference-pvd.md`.

### `gate.py`

Portable, ecosystem-neutral CI quality gate (CR0046). Aggregates the deterministic checks
(conformance, reconcile drift, validate, constitution, integrity) into one consolidated
pass/fail and exits non-zero only when a blocking check fails. `--only` / `--skip` select
checks; constitution blocks only when `constitution.enforce` is set. No network, no CI
assumption - runnable in any CI or a pre-commit hook (see `help/gate.md` for wiring). The
check registry is injectable, so the aggregation logic is unit-tested without a full repo.

### `version_check.py`

Skill version check + self-update signal (CR0044). Compares the installed version
against the latest GitHub release; `status`/`hint` print a one-line notice when newer.
On by default, opt-out (`version_check.enabled`), TTL-cached, silent offline, per-version
snooze. Drives the `skill-update` action via `scope`.

- `check`: report {installed, latest, status, scope}
- `snooze`: dismiss the current latest until a newer release
- `scope`: print the install scope (user / project / agents)

Action workflow: `reference-skill-update.md`.

### `transition.py`

Deterministic status transition + cascade (CR0042). `set --id <ID> --status <new>`
sets the artifact's `Status`, syncs its index row + summary counts (reusing
`reconcile.apply_type`), and ticks/unticks a story's checkbox in the parent epic's Story
Breakdown. `index_synced` is the true post-state (warns if a row is archived or the new
status has no summary row). Replaces the hand-edited "mark it Done + update the index"
cascade.

### `archive.py`

Index archival for large boards (RFC0012). `archive --type <t> --release <r>` moves a
type's terminal master-table rows into `<type>/archive/{release}/{type}.md` and leaves a
bullet pointer in the live index - rows move, artifact files stay. `parse_index` unions
the archive sub-indexes so the census stays correct. Explicit, idempotent per release.

- `archive`: move terminal rows of one type by release (`--dry-run` to preview)

Convention: `reference-outputs.md#index-archival`.

### `constitution.py`

Project-constitution principle gate (RFC0005). Asserts the machine-checkable
principles declared in `sdlc-studio/constitution.md` - each `rule:` maps onto an
existing detector (integrity/conformance/validate/reconcile). Advisory by default;
`constitution.enforce: true` makes a violation exit non-zero.

- `check`: report (and, when enforced, fail on) principle violations

Full methodology: `reference-doctrine.md#constitution`.

### `file_finding.py`

Deterministic Bug/CR/RFC filer for audit findings (RFC0002). Allocates a
collision-free ID, renders a STRUCTURED artifact (required sections enforced - it
refuses a hollow stub), appends the index row, and recomputes the index counts
(reusing reconcile's pass).

- `file --type bug|cr|rfc --title ... <fields>`: write one artifact
- `rebuild --type <t>`: recompute a type's index summary counts

Full methodology: `reference-audit.md`.

### `verify_ac.py`

Executes AC verifiers defined in story files and updates each AC's
`Verified:` line. Drives `/sdlc-studio reconcile --verify`.

- `run`: walk stories, run verifiers, write report
- `report`: print the latest verification report

Full workflow: `reference-verify.md`. User-facing help:
`help/verify.md`.

### `github_sync.py`

Two-way sync between local CR/Story/Epic files and GitHub Issues via
the `gh` CLI.

- `pull`: fetch issues with `sdlc:*` labels and create local files
- `push`: create or update issues from local files
- `cascade`: walk merged PRs and trigger Story Completion Cascades
- `state`: print sync state

Full workflow: `reference-github-sync.md`. User-facing help:
`help/github-sync.md`.

### `reconcile.py` (read-only)

Builds the artifact-file census and reports `_index.md` drift as JSON.

- `detect`: census + drift report (`--scope`, `--write-report`)

Drift kinds: `status-mismatch`, `missing-row`, `orphan-row`, `count-mismatch`,
`missing-index`. Claude consumes the report, applies the edits, and handles the
checkbox/dependency/PRD-feature and CR-cascade drift that needs judgement.
Full workflow: `reference-reconcile.md`.

### `status.py` (read-only)

- `pillars`: four-pillar census (Requirements/Code/Tests/Reviews) as JSON
- `hint`: the next mechanical action

Live metrics (lint, type-check, coverage) are left to Claude to run. Help:
`help/status.md`, `help/hint.md`.

### `validate.py` (read-only)

- `check`: lint artifact structure (ID, Status vocabulary, title, AC presence)
- `instructions`: hygiene-check the project's `AGENTS.md` / `CLAUDE.md` (AGENTS.md
  canonical, CLAUDE.md a `@AGENTS.md` pointer, operating-doctrine + `LATEST.md`
  pointers present, pre-release gate + compaction rule present, no per-ship-narrative
  bloat). Used by `/sdlc-studio init` (seed-or-check) and `/sdlc-studio review`.

Exits non-zero when any error-severity violation is found. Used by Ready-status
checks (`reference-decisions.md`) and as a reconcile pre-step.

### `next_id.py` (read-only)

- `allocate`: next free ID for a type (`--remote` also scans `origin/main`)
- `scan`: list IDs in use

Read-only; runs `git ls-tree` (no fetch - the caller fetches first per the
contract). Backs ID assignment in `reference-cr.md` and doctrine rule 13.

### `review_prep.py` (read-only)

- `prep`: deterministic inputs for the five-leg review (artifact staleness,
  persona definition-vs-PRD usage, count and AC-verification inputs)

Gathers inputs only; the review verdict stays with Claude. Full workflow:
`reference-review.md`.

### `plan.py`

Claude Code plan-file manager for `~/.claude/plans/`.

- `list`: table of active plans (slug, modified date, age, first heading);
  `--all` includes the archive, `--stale` filters by `--days` (default 30)
- `archive`: move `<slug>.md` to `archive/<yyyy-mm>/`; errors on a missing
  slug, an already-archived plan, or an existing archive target

Contract note: this is the one script that writes outside `.local/` - the
`archive` subcommand moves files under `~/.claude/plans/`, an operator-owned
directory. It never deletes and never overwrites; `list` is read-only.
Full workflow: `reference-plan-files.md`. User-facing help: `help/plan.md`.

### `lessons.py`

Lessons manager for both tiers: the project's `sdlc-studio/.local/lessons.md`
and the skill's own cross-project `lessons/` registry.

- `list`: project-tier entries newest first (`--global` for the skill tier)
- `add`: append a project-tier entry (L-NNNN allocation, top insertion,
  header upkeep); `--global` creates the next `LL{NNNN}-{slug}.md` from
  `lessons/_template.md` and appends the `_index.md` row
- `prune`: drop project-tier entries with Epic `<=` `--older` or `==` `--epic`
- `recall`: skill-tier lessons matching `--tags`/`--query` (case-insensitive
  substring); `--all` searches both tiers

`add --global` writes within the skill's own `lessons/` folder (the registry
ships with the skill); project-tier writes stay in `.local/`. Full workflow:
`reference-agentic-lessons.md#lessons-accumulation`. User-facing help:
`help/lessons.md`.

## See Also

- `best-practices/script.md` - Style rules for shell and Python scripts
- `scripts/README.md` - Directory overview for contributors
- `reference-repo-map.md`, `reference-verify.md`, `reference-github-sync.md` - Consumer workflows
