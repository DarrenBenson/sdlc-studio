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
Grep, Bash, Edit). Three capabilities need
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
it). Advisory signal for estimation and refactor-first; `repo_map`
emits the same per-function scores into the map.

- `scan`: list functions over the cognitive threshold (`complexity.cognitive_high`, default 15)
- `assess --files ...`: a change's blast-radius difficulty band + refactor-first hotspots (used by `code plan`)

### `provenance.py`

Artifact provenance. Makes deterministic creation the *checkable* path: `new`
stamps every artifact (`> **Created-by:** sdlc-studio ...`); `check` flags artifacts past
the `provenance.adopt_after` id cutoff that lack the stamp (hand-authored), with
remediation - advisory by default, `provenance.enforce: true` to block; `remake` content-
preservingly backfills the stamp into un-stamped artifacts (idempotent, dry-run-able,
stamp-only - never re-lays-out content). Standalone + advisory by design (not wired into
the gate); adopting it is a project choice.

### `telemetry.py`

Run telemetry recorder. `record` appends a per-unit run outcome
(id, type, iterations, wall-time, stages, critic verdict, complexity, churn, reopened,
tokens-when-supplied) to the gitignored `sdlc-studio/.local/telemetry.jsonl`. Local-only,
no network, no upload; advisory (a write failure is swallowed, never raised into the loop);
only whitelisted non-None fields are written; `read_all`/`show` skip malformed lines. Feeds
the deferred calibrate step.

### `artifact.py`

- `new --type retro|review`: the meta-artifacts are tool-created too
  (allocated id, template scaffold, index row where a meta index exists) - they stay
  outside the status machinery (`transition` refuses them by design).

Deterministic artifact create + close cascade. `new --type <any of the 8 numbered
types> --title ...` allocates a collision-free id, renders a valid scaffold (vocab-correct
status; a story gets a populated AC section), appends the index data-table row (built
generically from that index's own header, so it works for every type), recomputes counts,
and wires a story into its parent epic's Story Breakdown. `close --id` terminal-transitions
by id-prefix with the per-type terminal status (reusing transition). Replaces the ~10-step
hand cascade. Shares `file_finding.append_index_row`. On the empty-project first run it
creates a missing `<dir>/_index.md` from `templates/indexes/` (via
`file_finding.ensure_index`), so the first artifact of a type is indexed like every later
one; `--template full` grafts the rich `templates/core/` body onto the deterministic head.
`batch --type <t> --spec <items.json>` creates many artifacts of one type in a single
atomic pass: a reserved contiguous id block, every index row, and every story-to-
epic link wired in one go; a missing epic or id collision aborts before any write;
`--dry-run` previews the id map. Batch defaults to `--template full` (the fan-out case).

### `init.py`

Deterministic greenfield initialiser - `init` is now an executable, not a manual
checklist. `run` creates the full `sdlc-studio/` directory tree, pre-creates every per-type
`_index.md` (reusing `file_finding.ensure_index`), seeds
`sdlc-studio/.config.yaml` and the agent-instructions starters (`AGENTS.md`/`CLAUDE.md`)
from templates, and with `--scaffold` seeds the singleton docs (prd/trd/tsd/personas).
`--detect` infers the stack; idempotent (never overwrites without `--force`); `--dry-run`
previews every write so the workflow can show the config and confirm once before applying.
It also seeds an empty `sdlc-studio/decisions.md`.

### `ac_scope.py`

Authoring lint (advisory): `check` flags a story whose acceptance criteria mention a
distinctive capability keyword owned by a **different** epic's title (e.g. an EP0001 story
asserting an "account token" when accounts are EP0006) - such a story is un-Done-able in its
own epic and should be split or re-scoped. Heuristic and read-only; false positives are
expected (the operator decides); never auto-edits. Run by the authoring loop's closing
consistency pass.

### `decisions.py`

Project decisions log - the canonical home for load-bearing decisions, both
product (scope cuts, resolved PRD open questions) and implementation conventions (error
envelope, ID scheme, token strategy, migrations, test harness). `add --decision ...
--rationale ...` appends an auto-numbered, dated row to `sdlc-studio/decisions.md`; `list`
prints it (filterable by status); `promote --from PRD-OQ3 ...` records a resolved PRD open
question with a back-link (one record, two views). Append-only and greppable, so the spine lives
in one place and feeds the handoff context delegated agents read - distinct from the
sprint per-tranche ledger (`ledger.py`).

### `pvd.py`

PVD projection + drift. `sync` projects the one writable master
Product Vision Document into a child repo read-only (copy in dev, symlink in prod);
`drift` compares a projected copy against the master (in-sync / stale / behind / missing /
error) via sha256 + version. An unreadable/missing master reports `error`, never a vacuous
in-sync. `read_manifest` parses `product-manifest.yaml` (no PyYAML). See `reference-pvd.md`.

### `gate.py`

Portable, ecosystem-neutral CI quality gate. Aggregates the deterministic checks
(conformance, reconcile drift, validate, constitution, integrity) into one consolidated
pass/fail and exits non-zero only when a blocking check fails. `--only` / `--skip` select
checks; constitution blocks only when `constitution.enforce` is set. No network, no CI
assumption - runnable in any CI or a pre-commit hook (see `help/gate.md` for wiring). The
check registry is injectable, so the aggregation logic is unit-tested without a full repo.
`--require-retro RETROxxxx` adds a blocking close-gate check: the sprint/review close fails
loud until the named batch retro exists in `sdlc-studio/retros/` (the hard retro gate).

### `blocker_sweep.py`

The inverse of `audit`'s `unmet-deps`: finds units whose blockers have **cleared**. `sweep`
collects every blocker signal (Status `Blocked`, a `Depends on:` field, an epic `Blocked By`
row), resolves each referent's current status - in-repo by the file census, cross-repo by
reading the sibling repos in `product-manifest.yaml` (reuses `pvd.read_manifest`) - and
classifies each genuinely-blocked unit as now-unblocked (every referent terminal/delivered)
or still-blocked (outstanding referent named). Fail-loud per LL0008: a missing/unreadable/
unknown-status referent is reported still-blocked, never silently cleared. Read-only - it
proposes `Blocked -> Ready` candidates; the gated `transition` stays the actor. Runs before
`sprint plan` and as the `reconcile detect --blocker-sweep` advisory lane (which never
affects drift or the exit code). See `reference-sprint.md` and `reference-reconcile.md`.

### `deploy.py`

Orchestrate-only deploy last-mile. Read-only, ecosystem-neutral: it never deploys, never
rolls back, never reads secrets, and never runs inside `sprint`.

- `preflight`: read `deploy.*` config, run the pre-deploy gate, emit the readiness verdict + the
  operator hand-off (the deploy command to run, the rollback procedure to keep ready). Exit 0 when
  the gate is green, 1 otherwise. Never executes the deploy.
- `record --status <rolled-out|verified|rolled-back|failed> [--detail ...]`: append a timestamped
  outcome to `sdlc-studio/deploy-log.md` (the WS3 feedback loop).

Workflow: `reference-deploy.md`; schema: `reference-config.md#deploy`.

### `version_check.py`

Skill version check + self-update signal. Compares the installed version
against the latest GitHub release; `status`/`hint` print a one-line notice when newer.
On by default, opt-out (`version_check.enabled`), TTL-cached, silent offline, per-version
snooze. Drives the `skill-update` action via `scope`.

- `check`: report {installed, latest, status, scope}
- `snooze`: dismiss the current latest until a newer release
- `scope`: print the install scope (user / project / agents)

Action workflow: `reference-skill-update.md`.

### `transition.py`

Deterministic status transition + cascade. `set --id <ID> --status <new>`
sets the artifact's `Status`, syncs its index row + summary counts (reusing
`reconcile.apply_type`), and ticks/unticks a story's checkbox in the parent epic's Story
Breakdown. `index_synced` is the true post-state (warns if a row is archived or the new
status has no summary row). Replaces the hand-edited "mark it Done + update the index"
cascade. **A story -> Done is gated on its AC-verify result:** if it declares
executable (non-`manual`) ACs that are red or never run in `verify-report.json`, the
transition is refused - the Definition-of-Done safety net for the hand-driven path that the
sprint conformance gate already covers. `--force` overrides; manual-only / AC-less
stories and non-story types are never gated.

### `archive.py`

Index archival for large boards. `archive --type <t> --release <r>` moves a
type's terminal master-table rows into `<type>/archive/{release}/{type}.md` and leaves a
bullet pointer in the live index - rows move, artifact files stay. `parse_index` unions
the archive sub-indexes so the census stays correct. Explicit, idempotent per release.

- `archive`: move terminal rows of one type by release (`--dry-run` to preview)

Convention: `reference-outputs.md#index-archival`.

### `constitution.py`

Project-constitution principle gate. Asserts the machine-checkable
principles declared in `sdlc-studio/constitution.md` - each `rule:` maps onto an
existing detector (integrity/conformance/validate/reconcile). Advisory by default;
`constitution.enforce: true` makes a violation exit non-zero.

- `check`: report (and, when enforced, fail on) principle violations

Full methodology: `reference-doctrine.md#constitution`.

### `file_finding.py`

Deterministic Bug/CR/RFC filer for audit findings. Allocates a
collision-free ID, renders a STRUCTURED artifact (required sections enforced - it
refuses a hollow stub), appends the index row, and recomputes the index counts
(reusing reconcile's pass).

- `file --type bug|cr|rfc --title ... <fields>`: write one artifact
- `rebuild --type <t>`: recompute a type's index summary counts

Full methodology: `reference-audit.md`.

### `verify_ac.py`

Executes AC verifiers defined in story files and updates each AC's
`Verified:` line. Drives `/sdlc-studio reconcile --verify`.

- `run`: walk stories, run verifiers, write report (`--id USNNNN` resolves one story)
- `report`: print the latest verification report
- `lint`: advisory - flag Verify lines that fall through to `shell` as mis-written runner
  calls (`npm test -- ... -t`, `curl ... returns N`), nudging to the DSL
- `ts-check --spec <ts>`: validate a test-spec's AC Coverage Matrix is not decorative -
  every AC mapped to a passing test case, no placeholders; `--verify-report` cross-checks the
  matrix's claimed status against the live report
- `epic-ts --epic EPxxxx`: require an epic to have a test-spec (linked by its `Epic:` field)
  whose matrix passes `ts-check` - the hard epic-scope TS requirement, gated by
  `quality.epic_requires_test_spec` (default true; single-story work is exempt)

Full workflow: `reference-verify.md`. User-facing help:
`help/verify.md`.

### `mutation.py`

The executable mutation-check gate - the complement of `verify_ac.py`: verify_ac
confirms an AC's tests PASS; mutation asks whether they would FAIL if the feature
broke. Applies a declared, bounded set of textual mutations (invert-guard,
stub-return-null, unset-delivered-field, no-op-mapper) to a selected surface via
per-language pattern profiles, re-runs the test command per mutation, and reports
**killed vs survived** - a survivor is a finding. Deterministic (same code plus the
same set gives the same report); honest degrade (an un-mutatable file/class is
reported un-checked, a red baseline yields error verdicts, ceiling truncation is
counted, never silent).

- `run --test CMD` with a surface: `--files a.py ...`, `--since REF` (git diff),
  or `--story USxxxx` (the story's epic/CR `Affects`); `--max-mutations N`
  (default `quality.mutation_max`, else 25); writes
  `sdlc-studio/.local/mutation-report.json`; exits non-zero on survivors/errors
- `prefilter --tests <paths>`: advisory list of test files with no recognisable
  assertion - the cheap static signal for which tests to mutate first

The gate's `mutation` lane surfaces the report (advisory in v1; an absent report
reads not-run, never PASS). User-facing help: `help/mutation.md`.

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
- `apply`: mechanical fixes - status cells + summary counts, behind `--dry-run`
- `fields`: project file-owned cells (Title, Points, Persona) from the files into the index, so
  it is fully derived; `--apply` writes, default reports. A field absent in the
  file is left untouched. Persona reads the canonical `> **Persona:**` story field

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

Covers the 8 pipeline types plus the **meta-artifacts** `review` (RV####) and `retro`
(RETRO####), so review/retro ids are allocated, never hand-picked - run
`next_id.py allocate --type review` before writing a new review/retro, the same discipline as
`artifact.py new` for pipeline types. (Lessons `LL####` have their own manager in `lessons.py`;
personas are named, not numbered.) Read-only; runs `git ls-tree` (no fetch - the caller fetches
first per the contract). Backs ID assignment in `reference-cr.md` and doctrine rule 13.

### `migrate_v3.py`

One-shot schema v2 -> v3 migration (sequential ids -> type-prefixed short ULIDs):

- `plan`: preview the old-id -> new-id map, write nothing
- `apply`: rewrite ids to ULIDs, retain each old id as an alias (`> **Aliases:**`), rewrite
  every intra-workspace link, and regenerate index counts

Preserves creation order (each ULID's timestamp is derived from the file's date), is dry-run
first, and is idempotent (an already-migrated file is skipped). After `apply`, set
`schema_version: 3` in `.config.yaml` so new artefacts mint ULIDs too. `sdlc_md.alias_map`
resolves a pre-migration id to its current ULID, so `--id US0001` still works afterwards.

### `audit_check.py`

One CI-runnable command over the schema-v3 team-schema rules, emitting STABLE rule ids so the
output is a reference implementation the wider crew audit linter can consume:

- `check`: run all rules; exit 1 on any error-severity finding, 0 on a clean repo. `--format
  json` gives `{ok, rules, findings}` with `{rule, file, message}` per finding.

Rules (all era-gated to schema v3, so a v2 project reports nothing): `authorship-structured`,
`authorship-type`, `authorship-unresolved`, `evidence-present`, `duties-separated`,
`id-format`, `index-derived`. These same rules are enforced in the blocking `gate` via
`validate` and the `index-derived` check; `audit_check.py` is the focused, stable-id view.

### `backfill_authorship.py`

Backfills a structured `> **Raised-by:** Name; type; version` reference onto artefacts that
predate it, inferring the author from existing `Requester`/`Created-by`/revision-history
fields and marking an inferred attribution `(inferred)` so it never reads as first-hand:

- `plan`: count what would change, write nothing
- `apply`: write the raised_by lines (additive; idempotent - skips artefacts that already
  have one)

Run once when a project adopts schema v3; the `authorship-structured` validate rule then
holds new artefacts to a typed, resolvable author (`type` is one of human | persona | agent,
persona resolved against `sdlc-studio/personas/`).

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

## Orchestration, checks & helpers

### `disclosure.py`

Progressive-disclosure + Claude Code best-practice check, **advisory**. Flags reference-/
help- files missing a `Load when:` trigger or orphaned from every index (SKILL.md / help/references.md
/ help/help.md), plus best-practice items from `best-practices/claude-skill.md` (scripts executable +
expose `--help`, templates use `{{placeholder}}`, SKILL.md has a When-to-Use section). Skill-dev only
(no-op for consuming repos). Wired into the gate as NON-BLOCKING; `--strict` opts into a non-zero exit.
The token lever: a doc with no load-trigger and no index entry gets pulled in without discipline.

### `project_upgrade.py`

Migrate a CONSUMING project to the current skill conventions, the project-side complement
to `skill-update` (which updates the tool, not the project). `detect` reports the version/convention
gap (project `sdlc-studio/.version` vs the installed skill); the dry-run (default) prints a migration
plan split into **auto-correctable** (scaffold `.config.yaml` with a `provenance.adopt_after` cutoff
so existing artefacts are exempt, scaffold/bump `.version`, `reconcile` index/status drift) and
**needs-judgement** (old personas -> Cooper model / review-seat charters, AGENTS hygiene, missing
`Verify:`/AC - reported, never auto-applied, never filed as CRs). `--apply` performs only the safe
deterministic set; idempotent. Reuses reconcile/validate/next_id/version_check. `skill-update` offers
it after a version bump.

### `audit.py`

Adversarial audit / tranche pre-flight. `check` grooms a batch for readiness - weak-AC, unmet-deps, already-terminal, link-integrity, **already-satisfied** (a Ready unit whose executable ACs all pass in the verify-report - a close-candidate, not work to build), **weak-verify** (a non-executable Verify line, reusing `verify_ac lint`) and **cross-epic-ac** (an AC owned by another epic, reusing `ac_scope`) - before the triage STOP, so work never starts on a unit that would pass the gates vacuously or be reverse-engineered at implement time.

### `sprint.py`

The Goal-Driven Development loop's planner (renamed from `autosprint.py`). `plan <query> --order priority|wsjf` selects + dependency-orders the batch (the triage plan); priority dominates, complexity breaks ties. `plan --prd <path>` bootstraps greenfield authoring; `plan --write` persists the sprint-plan artifact; `plan` runs `reconcile detect` first and surfaces drift, refusing under `--strict` (reconcile-before-plan). `--order wsjf` orders by seat-scored WSJF = (value+time-criticality+risk-reduction)/size from `.local/wsjf-inputs.json`, degrading to priority+complexity without inputs or under `--skip-personas`. See reference-sprint.md.

### `autosprint.py`

Deprecated alias for `sprint.py` - re-exports it so `import autosprint` and the `autosprint.py` CLI keep working, emitting a deprecation pointer to `sprint`. Prefer `sprint`.

### `config.py`

Merged per-project configuration reader. Layers `templates/config-defaults.yaml` under the project's `sdlc-studio/.config.yaml` (degrading without PyYAML); the source of `status_vocab`, adoption cutoffs, `complexity`, `constitution`, `version_check`, `provenance`, etc.

### `conformance.py`

The lifecycle-conformance gate. `detect_conformance` reports per-story stages (decomposed -> AC -> verifiable -> verified -> reconciled -> critiqued -> documented) and hard-fails any terminal unit with a stage missing. Repo-global signals (reconciled, documented) apply to every Done unit.

A failure does not just print a count. The gate and `conformance check` name the two whole-batch remedies inline: set `conformance.adopt_after` (forward-only adoption - accepts a bare id `103` or prefixed `US0103`, and ids up to and including the cutoff are exempt), or run `verify_ac` and back-annotate `- **Verified:**` to clear per-unit debt. The output also distinguishes unadopted-discipline debt (most units mass-missing the same stage - pre-existing, forward-only) from scattered per-unit gaps that may be a regression, so a grown-but-accepted count is not mistaken for a fresh breakage. The cutoff is parsed by the shared `sdlc_md.parse_cutoff` (one parser for both gates), which raises a clear error on an unparseable value rather than silently disabling the cutoff.

### `critic.py`

The independent-critic verdict ledger. `record` writes a committed verdict to `sdlc-studio/reviews/critic-verdicts.md` stamping both the **reviewer and the author** (the authoring seat / delegation id); `verdict_for` reads it. `is_independent` proves `reviewer != author`; `is_pre_gate` flags units closed before the gate (the visible `pre-gate` marker, grandfathered). Conformance's `critiqued` stage requires a committed APPROVE that is independent or pre-gate.

### `persona_resolve.py`

Resolves the worker amigo for a delegated sub-agent, most-specific-first: a project-authored practitioner amigo (`sdlc-studio/personas/amigos/<seat>.md`), else the skill default (Dani / Sam / Lena), else generic. `resolve` prints the framing the orchestrator appends *after* the contract; `--skip-personas` emits nothing (byte-equivalent generic). The stance never overrides the concrete contract, and the worker is always a separate instance from its reviewer.

### `doc_coverage.py`

The documentation-coverage check - the `documented` DoD floor. Hard-fails when a Type-Reference command lacks a help/help.md catalogue entry or a script lacks a reference-scripts.md entry; warns on an empty CHANGELOG [Unreleased]. No-op for consuming repos (no SKILL.md). Wired into the gate + conformance.

### `doc_freshness.py`

Advisory freshness check for `sdlc-studio/reviews/LATEST.md` - the state anchor drifts silently. Compares the facts LATEST.md *claims* (version, script-test count, disclosure count) against reality (SKILL.md version, the `def test_` census, `disclosure.check`) and flags mismatches. Only checks a fact LATEST.md actually states; never blocks; no-op off the skill repo. Wired into the gate as advisory.

### `integrity.py`

Referential integrity. `detect_integrity` flags missing required links (e.g. a story with no epic) and dangling references across the artifact graph; errors vs advisories.

### `ledger.py`

The append-only per-tranche decisions ledger. `record` appends a decision + rationale to `sdlc-studio/decisions/<tranche>.md`; survives context compaction so a reset resumes from disk.

### `loop_guard.py`

The sprint deterministic guardrails. The iteration cap, the repetition-breaker (repeated failure signature), and the completion oracle (`is_complete`) - persisted to `.local/loop-state.json` so an unattended run cannot thrash or declare itself done early.

### `resume.py`

Resume an interrupted sprint from the persisted ledger + loop-state, so a context reset or crash continues the tranche from disk rather than a lost transcript.

### `rfc.py`

RFC helpers - the `rfc decide` multi-RFC decision digest (per-draft open-decision + workstream counts + ready flag) and RFC index/table helpers (escaped-pipe-aware via sdlc_md).
