# Script Catalogue - Upgrade, deploy & version

<!-- Load when: you need the full detail for a script in this group. The lean
     index with all groups is reference-scripts.md. -->

Detail pages for the **upgrade, deploy & version** scripts. See
[reference-scripts.md](reference-scripts.md) for the full index across all groups.

## Scripts

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

### `migrate.py`

The upgrade ORCHESTRATOR: one command that reviews every artefact and upgrades
where it safely can. Runs `project_upgrade` (conventions + version) and `migrate_v3 sizing`
(container Effort/Points -> a T-shirt `Size`) in order, then the artefact-review sweep, and emits ONE
report split into **deterministic** (what it auto-applied - version, config, sizing conversions) and
**needs a human** (each item with the exact command: an accepted childless request -> `refine`, a
childless Issue -> `triage`, a delivery unit sized in legacy Effort -> a re-size). The honesty rule:
it auto-applies only the deterministic, reversible set and never guesses a judgement (there is no
honest Effort->Points map). Dry-run by default; `--apply` writes the deterministic set only. Reuses
`project_upgrade`, `migrate_v3` and `reconcile` - it adds the aggregation and the sweep, not a
parallel implementation.

### `migrate_v3.py`

One-shot schema v2 -> v3 migration (sequential ids -> type-prefixed short ULIDs):

- `plan`: preview the old-id -> new-id map, write nothing
- `apply`: rewrite ids to ULIDs, retain each old id as an alias (`> **Aliases:**`), rewrite
  every intra-workspace link, and regenerate index counts

Preserves creation order (each ULID's timestamp is derived from the file's date), is dry-run
first, and is idempotent (an already-migrated file is skipped). After `apply`, set
`schema_version: 3` in `.config.yaml` so new artefacts mint ULIDs too. `sdlc_md.alias_map`
resolves a pre-migration id to its current ULID, so `--id US0001` still works afterwards.

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

### `lite_profile.py`

Promotion for the lite profile (`profile: lite` collapses the pipeline to PRD ->
story -> implement; reader `sdlc_md.profile`). `promote` inserts one umbrella epic
above the epic-less stories, wires each in, flips to full, and reconciles (`--dry-run`).

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

### `resume.py`

Resume an interrupted sprint from the persisted ledger + loop-state, so a context reset or crash continues the tranche from disk rather than a lost transcript.
