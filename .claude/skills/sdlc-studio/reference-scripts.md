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

Script examples use the form `python3 "$CLAUDE_SKILL_DIR/scripts/<name>.py"`.
Claude Code sets `$CLAUDE_SKILL_DIR` to this skill's directory at every install
level (personal, project, or plugin). If unset (another agent tool, or a shell
outside skill execution), substitute the directory containing this skill's
`SKILL.md` (e.g. `~/.claude/skills/sdlc-studio`, `~/.agents/skills/sdlc-studio`,
`.github/skills/sdlc-studio`). The quoted variable fails loudly when unset;
never guess between multiple installed copies.

## Rationale {#scripts-rationale}

SDLC Studio was Claude-native through v1.5.0: every workflow was a markdown
instruction executed with built-in tools. Three capabilities need
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
judgement in Claude** - to the highest-frequency mechanical workflows:

1. **Drift detection** (`reconcile.py`) – the file census and index-drift
   comparison doctrine rule 3 prescribes is a deterministic algorithm.
2. **Pipeline status** (`status.py`) – the four-pillar census and hint ladder.
3. **Artifact validation** (`validate.py`) – ID/Status/structure linting.
4. **ID allocation** (`next_id.py`) – cross-repo-safe numbering (rule 13).
5. **Review inputs** (`review_prep.py`) – the mechanical inputs the five-leg
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
9. Takes id lists the one documented way - a repeatable `--id` or a single
   comma-separated `--ids` (`sdlc_md.add_ids_argument` / `resolve_ids`), and the
   recorder subject id as `--unit` - so no verb needs a per-script `--help` probe
   (swept by `tests/test_cli_grammar.py`)

See `best-practices/script.md` for the shared style rules (shebang,
error handling, CLI flags over config files, and the CLI argument grammar).

## Catalogue {#scripts-catalogue}

The catalogue is grouped into detail pages (each under the reference budget). This index
lists every script with a one-line summary; open the linked page for the full entry.

### Creation & mutation - [reference-scripts-create.md](reference-scripts-create.md)

- `artifact.py` - `new --type retro|review`: the meta-artifacts are tool-created too
- `init.py` - Deterministic greenfield initialiser - `init` is now an executable, not a manual
- `decisions.py` - Project decisions log - the canonical home for load-bearing decisions, both
- `transition.py` - Deterministic status transition + cascade. `set --id <ID> --status <new>` sets `Status`,
  and the canonical one-call bug close is `set --id BGxxxx --status Fixed --depth "<tier (evidence)>" --verdict approve --reviewer <R> --author <A>` - depth stamp, independent verdict and gated transition in one call, every predictable refusal raised before any write,
- `archive.py` - Index archival for large boards. `archive --type <t> --release <r>` moves a
- `file_finding.py` - Deterministic Bug/CR/RFC filer for audit findings. Allocates a
- `persona_gen.py` - Deterministic floor of team/stakeholder generation: `stamp` marks a generated card provisional with a content hash, `classify` reports authored / generated-pristine / generated-edited (the never-clobber discriminator), `accept` clears provisional labels (batch-accept + persona review)
- `next_id.py` - `allocate`: next free ID for a type (`--remote` also scans `origin/main`)
- `ledger.py` - The append-only per-tranche decisions ledger. `record` appends a decision + rationale to `sdlc-studio/decisi...
- `rfc.py` - RFC helpers - the `rfc decide` multi-RFC decision digest (per-draft open-decision + workstream counts + read...
- `retro.py` - The retro spine. `validate --id RETROxxxx` is a CONTENT check (required sections, at least one real lesson, every finding dispositioned) and is what the close gate calls - a retro that exists but says nothing is not a retro. `dispose` reports each finding as filed / declined / undecided. `extract` lifts the retro's `## Lessons` bullets into the project lessons log, idempotently, so a lesson written in a retro reaches the digest the next sprint reads

### Reconcile, verify & checks - [reference-scripts-verify.md](reference-scripts-verify.md)

- `gate.py` - Portable, ecosystem-neutral CI quality gate. Aggregates the deterministic checks;
  `--release` is the pre-tag form (the same gate plus an executing AC-verify pass, one exit code);
  `--require-retro` is the sprint-close form (retro present + lessons re-validated + summary current)
- `verify_ac.py` - Executes AC verifiers defined in story files and updates each AC's
- `mutation.py` - The executable mutation-check gate - the complement of `verify_ac.py`: verify_ac
- `reconcile.py` - Builds the artifact-file census and reports `_index.md` drift as JSON.
- `status.py` - `pillars`: four-pillar census (Requirements/Code/Tests/Reviews) as JSON
- `validate.py` - `check`: lint artifact structure (ID, Status vocabulary, title, AC presence, an optional
- `conformance.py` - The lifecycle-conformance gate. `detect_conformance` reports per-story stages (decomposed -> AC -> verifiabl...
- `doc_coverage.py` - The documentation-coverage check - the `documented` DoD floor. Hard-fails when a Type-Reference command lack...
- `doc_freshness.py` - Advisory freshness check for `sdlc-studio/reviews/LATEST.md` - the state anchor drifts silently. Compares th...
- `integrity.py` - Referential integrity. `detect_integrity` flags missing required links (e.g. a story with no epic) and dangl...

### Audit, review & critic - [reference-scripts-review.md](reference-scripts-review.md)

- `ac_scope.py` - Authoring lint (advisory): `check` flags a story whose acceptance criteria mention a
- `plan_review.py` - Plan-review gate (schema v3 only, dormant on v2). Before a story with spec-derived ACs is
- `spec_guard.py` - Spec-edit guard (schema v3 only, dormant on v2). A delivery must not silently falsify the
- `constitution.py` - Project-constitution principle gate. Asserts the machine-checkable
- `audit_check.py` - One CI-runnable command over the schema-v3 team-schema rules, emitting STABLE rule ids so the
- `review_prep.py` - `prep`: deterministic inputs for the five-leg review (artifact staleness,
- `review_generate.py` - Deterministic spine of the model-driven `review generate` on-ramp. `bootstrap`
- `disclosure.py` - Progressive-disclosure + Claude Code best-practice check, **advisory**. Flags reference-/
- `audit.py` - Adversarial audit / tranche pre-flight. `check` grooms a batch for readiness - weak-AC, unmet-deps, already-...
- `critic.py` - The independent-critic verdict ledger. `record` writes a committed verdict to `sdlc-studio/reviews/critic-ve...
- `persona_resolve.py` - Resolves the worker amigo for a delegated sub-agent, most-specific-first: a project-authored practitioner am...

### Upgrade, deploy & version - [reference-scripts-upgrade.md](reference-scripts-upgrade.md)

- `deploy.py` - Orchestrate-only deploy last-mile. Read-only, ecosystem-neutral: it never deploys, never
- `version_check.py` - Skill version check + self-update signal. Compares the installed version
- `migrate_v3.py` - One-shot schema v2 -> v3 migration (sequential ids -> type-prefixed short ULIDs):
- `backfill_authorship.py` - Backfills a structured `> **Raised-by:** Name; type; version` reference onto artefacts that
- `lite_profile.py` - Promotion for the lite profile (`profile: lite` collapses the pipeline to PRD ->
- `project_upgrade.py` - Migrate a CONSUMING project to the current skill conventions, the project-side complement
- `resume.py` - Resume an interrupted sprint from the persisted ledger + loop-state, so a context reset or crash continues t...

### Domain helpers & orchestration - [reference-scripts-domain.md](reference-scripts-domain.md)

- `repo_map.py` - Pure-Python repository indexer. Produces
- `complexity.py` - Cognitive (SonarSource) + cyclomatic complexity per function from Python's
- `provenance.py` - Artifact provenance. Makes deterministic creation the *checkable* path: `new`
- `telemetry.py` - Run telemetry recorder. `record` appends a per-unit run outcome
- `pvd.py` - PVD projection + drift. `sync` projects the one writable master
- `blocker_sweep.py` - The inverse of `audit`'s `unmet-deps`: finds units whose blockers have **cleared**. `sweep`
- `triage_noise.py` - Creation-time triage noise controls (schema v3 only, dormant on v2). A **session cap**
- `triage_sampling.py` - Triage-as-sampled-audit (schema v3). `sample(items, seed)` picks the findings a human audits:
- `github_sync.py` - Two-way sync between local CR/Story/Epic files and GitHub Issues via
- `digest.py` - Context tiering - mechanical, drift-checked digests of closed (terminal) artefacts so
- `plan.py` - Claude Code plan-file manager for `~/.claude/plans/`.
- `lessons.py` - Lessons manager for both tiers: the project's `sdlc-studio/.local/lessons.md`
  and the skill's cross-project registry; `revalidate` + `summary` are the gated sprint-close loop
- `sprint.py` - The Goal-Driven Development loop's planner. `plan <query> --order priority|wsjf` selects + dependency-orders...
- `autosprint.py` - Deprecated re-exporting alias for `sprint.py` (the old name); prefer `sprint`.
- `handoff.py` - The run-close handoff guide: a JOIN over the run's own evidence naming every
  remaining item with its pointer (file / AC / check) and a copilot-tail vs judgement tag; emits the
  worklist the next `sprint plan --worklist` reads. `lib/run_state.py` holds the run object it closes
- `route.py` - Difficulty-aware model-tier routing, **advisory - no gate reads a tier**, no model API ever called (ids are ...
- `config.py` - Merged per-project configuration reader. Layers `templates/config-defaults.yaml` under the project's `sdlc-s...
- `loop_guard.py` - The sprint deterministic guardrails. The iteration cap, the repetition-breaker (repeated failure signature),...

## See Also

- `scripts/README.md` - directory conventions
- `reference-*.md` - the workflow references
