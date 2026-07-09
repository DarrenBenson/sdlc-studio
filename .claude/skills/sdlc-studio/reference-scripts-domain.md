# Script Catalogue - Domain helpers & orchestration

<!-- Load when: you need the full detail for a script in this group. The lean
     index with all groups is reference-scripts.md. -->

Detail pages for the **domain helpers & orchestration** scripts. See
[reference-scripts.md](reference-scripts.md) for the full index across all groups.

## Scripts

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

### `pvd.py`

PVD projection + drift. `sync` projects the one writable master
Product Vision Document into a child repo read-only (copy in dev, symlink in prod);
`drift` compares a projected copy against the master (in-sync / stale / behind / missing /
error) via sha256 + version. An unreadable/missing master reports `error`, never a vacuous
in-sync. `read_manifest` parses `product-manifest.yaml` (no PyYAML). See `reference-pvd.md`.

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

### `triage_noise.py`

Creation-time triage noise controls (schema v3 only, dormant on v2). A **session cap**
(`triage.session_cap`, default 20) refuses the N+1th finding of a session loudly (keyed by
`SDLC_TRIAGE_SESSION`, count in `.local/triage-session.json`). **Low-severity consolidation**
(`triage.low_consolidation`) folds a Low finding into a themed consolidation CR instead of its
own artefact; Medium+ stay individual. `file_finding` and `artifact new` both route here.

### `triage_sampling.py`

Triage-as-sampled-audit (schema v3). `sample(items, seed)` picks the findings a human audits:
every Critical, every raiser/triager severity disagreement, plus `triage.sample_rate` of the
rest, chosen by a stable hash of `(seed, id)` so a fixture is reproducible. `metrics(root)`
computes triage quality from the records (no hand-counting): the false-positive rate (a finding
triaged as real, later closed invalid), severity inflation (triager vs raiser), and
sampled-but-unreviewed findings as standing pending audit. Surfaced by `status triage-metrics`.

### `github_sync.py`

Two-way sync between local CR/Story/Epic files and GitHub Issues via
the `gh` CLI.

- `pull`: fetch issues with `sdlc:*` labels and create local files
- `push`: create or update issues from local files
- `cascade`: walk merged PRs and trigger Story Completion Cascades
- `state`: print sync state

Full workflow: `reference-github-sync.md`. User-facing help:
`help/github-sync.md`.

### `digest.py`

Context tiering - mechanical, drift-checked digests of closed (terminal) artefacts so
status/planning reads need not re-read the whole corpus as a repo ages:

- `build`: write `sdlc-studio/.local/digests.json` - one field-extracted entry per closed
  artefact (id, title, status, close outcome, cross-references). Originals are never
  summarised away; the digest is an access tier.

`digest.is_stale(root)` compares the on-disk digest to a freshly built one (a closed artefact
added/changed since -> regenerate), the same derived-and-drift-checked discipline as an index.
The read-path integration (status/hint reading digests) and the size threshold are the
remaining CR0179 workstream.

### `plan.py`

Claude Code plan-file manager for `~/.claude/plans/`.

- `list`: table of active plans (slug, modified date, age, first heading);
  `--all` includes the archive, `--stale` filters by `--days` (default 30)
- `archive`: move `<slug>.md` to `archive/<yyyy-mm>/`; errors on a missing
  slug, an already-archived plan, or an existing archive target

Contract note: the one script that writes outside `.local/` - `archive` moves files
under the operator-owned `~/.claude/plans/` (never deletes or overwrites; `list` is
read-only). Full workflow: `reference-plan-files.md`. Help: `help/plan.md`.

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

### `sprint.py`

The Goal-Driven Development loop's planner. `plan <query> --order priority|wsjf` selects + dependency-orders the batch (the triage plan); priority dominates, complexity breaks ties. `plan --prd <path>` bootstraps greenfield authoring; `plan --write` persists the sprint-plan artifact; `plan` runs `reconcile detect` first and surfaces drift, refusing under `--strict` (reconcile-before-plan). `--order wsjf` orders by seat-scored WSJF = (value+time-criticality+risk-reduction)/size from `.local/wsjf-inputs.json`, degrading to priority+complexity without inputs or under `--skip-personas`. Every planned unit is stamped with a `difficulty` band (route.py, advisory); with `routing.enabled` it also carries the `tier`/`model` recommendation; an estimator failure degrades that unit's routing fields, never the plan. See reference-sprint.md.

### `autosprint.py`

Deprecated re-exporting alias for `sprint.py` (the old name); prefer `sprint`.

### `route.py`

Difficulty-aware model-tier routing, **advisory - no gate reads a tier**, no model API ever called (ids are opaque strings the orchestrator passes to its own spawn mechanism). `estimate --unit` scores 0-100 from blast-radius cognitive/risk (`complexity.assess`), file scope, unresolved-path novelty, ACs and points - an unresolved signal defaults its subscore to 0.5 (never 0) and lowers confidence. `pick --unit --role author|critic` applies band->tier, kind floors, the low-confidence upward bump, and the critic rule (never smaller than the author; code units floor the critic at medium). `escalate --tier` steps to the next declared tier; `tiers` prints the resolved map (upward-only sparse degradation). Config: `reference-config.md#routing`.

### `config.py`

Merged per-project configuration reader. Layers `templates/config-defaults.yaml` under the project's `sdlc-studio/.config.yaml` (degrading without PyYAML); the source of `status_vocab`, adoption cutoffs, `complexity`, `constitution`, `version_check`, `provenance`, etc.

### `loop_guard.py`

The sprint deterministic guardrails. The iteration cap, the repetition-breaker (repeated failure signature), and the completion oracle (`is_complete`) - persisted to `.local/loop-state.json` so an unattended run cannot thrash or declare itself done early.
