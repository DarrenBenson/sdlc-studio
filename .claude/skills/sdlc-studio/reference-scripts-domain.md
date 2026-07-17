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

### `changelog.py`

Per-unit CHANGELOG fragments (the towncrier pattern, stdlib). A unit's entry lives in
`changelog.d/<unit>.md` (first line `<!-- section: Added -->`, then the entry), committed
with the unit - no shared-file contention. `compose` folds all fragments into
`## [Unreleased]` under their sections and consumes them (idempotent by consumption;
all fragments validate before any write, so a malformed one refuses the whole run by
name). `check` lists strays; the release gate's `changelog-fragments` lane fails a cut
while any exist. Direct CHANGELOG editing remains valid for non-adopters.

### `flow.py`

Deterministic flow metrics - the zero-token SCHEDULE instrument (the cost instrument,
points x a measured tokens-per-point rate, is a different axis). `compute` reports per-unit
cycle time (Created -> delivered, resolved from git history anchored on the status header
line, with a revision-history-row fallback at day precision), weekly throughput counting
DELIVERED terminal statuses only (a Superseded unit closed without delivering - no metric),
and work-item age for every non-terminal unit. Honesty contract: a unit whose dates cannot
be resolved is NAMED unmeasurable with the reason, never guessed or silently skipped.
Advisory only; nothing here feeds a gate.

### `telemetry.py`

Run telemetry recorder. `record` appends a per-unit run outcome
(id, type, iterations, wall-time, stages, critic verdict, complexity, churn, reopened,
tokens-when-supplied) to the **committed** evidence log `sdlc-studio/retros/evidence/actuals-*.jsonl`;
`forecast` records the plan-time prediction beside it (`forecasts-*.jsonl`). Both are project
evidence, not runtime state - no tool can regenerate an observation, and evidence the team
cannot read on a fresh clone is not evidence - so they live beside the velocity history they
are the rows of, and never in `.local/`. Sharded one file per UTC day, so two branches closing
sprints on different days merge cleanly and a same-day clash is a conflict a human resolves,
never a silent loss. No network, no upload; `record` is advisory (a write failure is swallowed,
never raised into the loop); only whitelisted non-None fields are written; `read_all`/`show`
skip malformed lines. `migrate` moves a pre-existing `.local/` log into the evidence dir
without loss (a project that upgrades keeps its history; the old log is read until it does).

A record can carry an `attempts` list of `{model, tokens}` - one entry per model invocation on a
unit, in order - so an escalation is visible AND priceable (`attempts_of` reads it; a legacy record
with only the flat `model`/`tokens` reads as ONE implicit attempt, so no migration is needed).
`unit_cost` sums the TRUE cost over the attempts (rework included) using `model_price`, which reads
`pricing.<family>` from `.config.yaml` (offline, no network) or a rough ESTIMATE default, and reports
a model with no price as UNPRICED - its tokens counted, its dollars never guessed.

### `sprint_report.py`

The end-of-sprint report: what a sprint delivered, what it cost, and whether the estimate held.
Mostly COMPOSITION - the retro holds Delivered, lessons and tickets; `retro.accuracy` holds the
estimate-vs-actual and the velocity; `telemetry` holds cost. `show --id RETROxxxx [--tokens N]
[--elapsed-hours H]` lays them out as one deterministic page (a script, so it costs no model tokens).
Actual spend is a MEASUREMENT priced from `pricing.*` with rework summed over attempts; there is no
avoided-cost / savings headline (a counterfactual is a model, not a measurement - the confusion this
project has been burned by). RENDERING is gated by `report.enabled` (a token-conscious project turns
the page off), but RECORDING is never gated - telemetry keeps recording, because a report not drawn
can be drawn later while a measurement not taken is gone.

### `pvd.py`

PVD projection + drift. `sync` projects the one writable master
Product Vision Document into a child repo read-only (copy in dev, symlink in prod);
`drift` compares a projected copy against the master (in-sync / stale / behind / missing /
error) via sha256 + version. An unreadable/missing master reports `error`, never a vacuous
in-sync. `read_manifest` parses `product-manifest.yaml` (no PyYAML); the parser itself lives in
`lib/xrepo` beside the cross-repo id resolver that reads it, so the manifest has one reader.
See `reference-pvd.md`.

### `blocker_sweep.py`

The inverse of `audit`'s `unmet-deps`: finds units whose blockers have **cleared**. `sweep`
collects every blocker signal (Status `Blocked`, a `Depends on:` field, an epic `Blocked By`
row), resolves each referent's current status - in-repo by the file census, cross-repo across
the sibling repos in `product-manifest.yaml`, both through the shared `lib/xrepo` resolver that
`audit` also uses - and classifies each genuinely-blocked unit as now-unblocked (every referent
terminal/delivered) or still-blocked (outstanding referent named). Fail-loud per LL0008: a
missing/unreadable/unknown-status referent is reported still-blocked, never silently
cleared. Read-only - it
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
  header upkeep), stamped `Added:` + `Review-by:` (the validity horizon;
  `--validity-days`, or the `lessons.validity_days` config key, default 90);
  `--global` creates the next `LL{NNNN}-{slug}.md` from `lessons/_template.md`
  and appends the `_index.md` row
- `prune`: drop project-tier entries with Epic `<=` `--older` or `==` `--epic`
- `recall`: skill-tier lessons matching `--tags`/`--query` (case-insensitive
  substring); `--all` searches both tiers
- `revalidate`: list open lessons with their horizon, or act on them - `--close
  L-NNNN` (no longer true), `--extend L-NNNN` (still true; the horizon moves out
  by the validity window), `--stamp` (give every horizon-less open lesson one:
  the backfill for a log written before horizons existed)
- `summary`: regenerate the committed `retros/LESSONS-SUMMARY.md` from the
  still-valid lessons - deterministic for a given log (no date in the output), so
  it is reproducible and the close gate can recompute it and compare

The close loop is mechanical, not doctrine: `gate --require-retro` (or
`--require-lessons`) fails loud on a **stale** summary - it recomputes the digest
from the log, so a lesson closed since the last regeneration fails it exactly as
an added one does - and on any open lesson past its validity horizon or carrying
none. `sprint plan` emits the still-valid digest into the plan itself, so the
sprint-start read is not something an agent can skip. See
`reference-agentic-lessons.md#close-loop`.

The project tier is the default; `--global` is the deliberate promotion, and it
writes **only where git actually holds the file**. Resolution order:
`--lessons-dir`, then the `skill_source_repo` config key read from `--root`
(default `.`), then the running skill's own `lessons/`. The destination must be
inside a git work tree, **not gitignored**, and its `_index.md` must be
version-controlled; the running-skill fallback must additionally be the skill
SOURCE checkout, since a commit into a vendored copy ships with no release. Any
of those failing is a refusal: non-zero exit, the reason, and the remedy.
Nothing is authored, and no success is reported. Project-tier writes stay in
`.local/`.

Full workflow: `reference-agentic-lessons.md#lessons-accumulation`. Config key:
`reference-config.md#skill-source-repo`. User-facing help: `help/lessons.md`.

### `sprint.py`

The Goal-Driven Development loop's planner. `plan <query> --order priority|wsjf` selects + dependency-orders the batch (the triage plan); priority dominates, complexity breaks ties. `plan --prd <path>` bootstraps greenfield authoring; `plan --write` persists the sprint-plan artifact; `plan` runs `reconcile detect` first and surfaces drift, refusing under `--strict` (reconcile-before-plan). The plan **emits the still-valid lessons digest** (`lessons.plan_digest`: the project log, else the committed `LESSONS-SUMMARY.md`), so the sprint-start read arrives inside the plan rather than as an instruction to open a file; a stale summary is warned about here and **fails** the close gate. `--order wsjf` orders by seat-scored WSJF = (value+time-criticality+risk-reduction)/size from `.local/wsjf-inputs.json`, degrading to priority+complexity without inputs or under `--skip-personas`. Every planned unit is stamped with a `difficulty` band (route.py, advisory); with `routing.enabled` it also carries the `tier`/`model` recommendation; an estimator failure degrades that unit's routing fields, never the plan. See reference-sprint.md.

`plan` **REFUSES an ungroomed batch** (the breakdown gate): a unit must declare `Affects:` and a size (`Effort:` / `Points:` / a seat score), or `plan` names it, says what it lacks, and exits non-zero **printing no plan** - a plan over unsized units cannot be sized or safely parallelised and looks authoritative anyway. The recorded opt-out is `sprint.breakdown: judgement` (the lane then reports); omission is not an escape. From the same `Affects` the plan derives **shared-file clusters** - units touching one file are not parallel, however the declared `Depends on:` graph waves them - and flags a large CR no story yet cites for decomposition (`cr action`), since only a story's Done is gated on executable ACs. `breakdown <query>` reports the same census read-only (never blocks, never writes).

`close --retro RETROxxxx [--goal-verdict achieved|partial|missed --note "..."]` runs the close
ceremony as ONE deterministic chain - goal-verdict (recorded here, reused when already judged,
refused when unjudged), retro validate + extract, lessons summary, `gate --require-retro
--require-review`, handoff generate (skipped when the run is already closed), reconcile detect -
STOPPING loudly at the first failing step with the remedy named; a re-run after repair resumes
idempotently. It ends by printing the sign-off decision brief composed from the committed
records (per-unit deliveries, verdict + REJECT history, gate and mutation results, forecast vs
measured telemetry spend); absent retro content, an unset goal, or an unjudged goal-verdict are
refusals with the command to run, never defaults. `goal-verdict` records the closing review's
Sprint Goal judgement on the run state.

### `backlog_triage.py`

The backlog-coherence ceremony behind `plan`'s triage pass and the `status`/`hint` triage advisory
(distinct from `triage.py`, which triages an Issue into bugs - this asks whether the BACKLOG is
worth planning FROM). Breakdown asks if a UNIT is plannable; triage asks if the items are DISTINCT,
correctly sized, current, and still wanted. Deterministic lenses, each stating what it compares:

- **DUPLICATE / SUBSUMED** (report) - two open artefacts whose `Affects` overlap AND whose
  title+summary are similar (token Jaccard): likely one unit filed twice. SUBSUMED is the strong
  form (one's files a proper subset of the other's). Names the candidate; never auto-refuses.
- **OVERSIZED** (block) - a delivery unit above the 8-point ceiling nobody can size reliably: a
  triage failure whose answer is to decompose. (The `plan` breakdown gate owns this one; the plan's
  triage pass shows only the judgement lenses to avoid double-reporting.)
- **STALE** (report) - open, untouched for months, nothing depends on it: still wanted?
- **ORPHANED DEPENDENCY** (report) - a `Depends on:` naming a terminal or absent artefact.

`check [--stale-days N] [--format json]` runs every lens over the backlog and exits non-zero if any
lens blocks. Judgement lenses report (the human decides); the mechanical OVERSIZED lens blocks. The
same overlap primitives back `file_finding`'s filing-time duplicate warning, so the cheap
filing-time lens and the plan-time lens agree by construction.

### `autosprint.py`

Deprecated re-exporting alias for `sprint.py` (the old name); prefer `sprint`.

### `handoff.py`

The run-close handoff guide - the single "here is where you pick up" document a run that
stopped short of its goal owes a human. `show` prints the join; `generate --outcome
<goal-reached|budget-spent|blocked|stopped>` writes it. A **JOIN over evidence that already
exists**, not new instrumentation: quarantined units + failure signatures from
`.local/loop-state.json`, failing and unproven ACs from `.local/verify-report.json`, per-unit
issues from `audit.audit_unit`, the stalled lifecycle stage from `conformance`, and the
approved batch from `.local/run-state.json` (then `.local/sprint-plan.json`).

Every non-terminal unit is named with at least one pointer - the failing AC, the check it
stalled at, the blocker, or its own file - and a batch id with **no artefact on disk is
still listed** (remaining-and-missing), as is a unit the loop quarantined outside the
approved batch. Nothing is dropped. Each item carries a suitability tag, `copilot-tail` or
`judgement`, seeded deterministically from the difficulty band (`route.estimate`), the
quarantine reason, the stage reached and the audit issues, with the reasons attached; an
item with no signal reads `judgement`, never a confidently-wrong tail.

Created through the meta-artifact machinery (`artifact.meta_new` - tool-allocated `HO` id +
index row, like a retro), linked from the retro via `--retro RETROxxxx` (refused before any
write when that retro does not exist), and it **emits a worklist**
(`.local/handoff-worklist.txt`) that the documented `sprint plan --worklist` reads back as
the next batch - no fourth batch source. `gate --require-handoff HOxxxx` fails unless the
handoff exists **and** a retro links it. See `help/handoff.md`, reference-sprint.md.

### `lib/run_state.py`

The run-state object (`sdlc-studio/.local/run-state.json`): a run's id, start time, goal
rung, approved batch and outcome, in one place. The loop is executed by the model calling
discrete scripts, so a run had no identity at all - what it did was scattered across seven
files nothing joined. `sprint plan --write` opens it; `handoff generate` closes it with the
outcome. **Extensible by contract**: `update()` merges and never drops a key it does not
recognise, so a later capability adds its own fields without touching the module. A run
nobody opened records `run_id: null` / `started_at: null` rather than a fabricated start.
A library, not a command - the writers are `sprint.py` and `handoff.py`.

### `route.py`

Difficulty-aware model-tier routing, **advisory - no gate reads a tier**, no model API ever called (ids are opaque strings the orchestrator passes to its own spawn mechanism). `estimate --unit` scores 0-100 from blast-radius cognitive/risk (`complexity.assess`), file scope, unresolved-path novelty, ACs and points - an unresolved signal defaults its subscore to 0.5 (never 0) and lowers confidence. `pick --unit --role author|critic` applies band->tier, kind floors, the low-confidence upward bump, and the critic rule (never smaller than the author; code units floor the critic at medium). `escalate --tier` steps to the next declared tier; `tiers` prints the resolved map (upward-only sparse degradation). Config: `reference-config.md#routing`.

### `config.py`

Merged per-project configuration reader. Layers `templates/config-defaults.yaml` under the project's `sdlc-studio/.config.yaml` (degrading without PyYAML); the source of `status_vocab`, adoption cutoffs, `complexity`, `constitution`, `version_check`, `provenance`, etc.

### `loop_guard.py`

The sprint deterministic guardrails. The iteration cap, the repetition-breaker (repeated failure signature), and the completion oracle (`is_complete`) - persisted to `.local/loop-state.json` so an unattended run cannot thrash or declare itself done early.
