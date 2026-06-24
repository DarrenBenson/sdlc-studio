# Changelog

All notable changes to SDLC Studio will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **seat-scored WSJF sprint planning (CR0099, from LL0007):** `sprint plan --order wsjf` now
  orders by **WSJF = (value + time-criticality + risk-reduction) / size**. The review seats score
  the numerator (Product Owner = value, QA = risk, Engineering = effort seeded by the complexity
  signal) into `.local/wsjf-inputs.json`; the planner computes and records the components in the
  sprint-plan artifact. Degrades gracefully to priority + complexity with no inputs or under
  `--skip-personas`. Sprint planning becomes a value/risk judgement, not a bare-priority sort.
- **already-satisfied flag in the tranche audit (CR0098, from LL0007):** `audit check` (the
  sprint pre-flight) now flags a Ready unit whose executable ACs all pass in the verify-report as
  **already-satisfied** - a close-candidate, not work to build. The audit can't see a feature
  shipped under a different artifact, but a green verifier set is the deterministic signal - the
  exact gap that let 5 stale Ready stories through this session's first plan. Advisory; reuses the
  verify-report.
- **persona index-projection via a canonical field (CR0097):** the deferred half of CR0082. The
  story template + scaffold now carry a canonical `> **Persona:**` field, and `reconcile fields`
  projects it into the index `Persona` column alongside Title/Points (absent field left untouched,
  BG0032). The "As a {persona}" prose stays; the metadata field is the projection source - so the
  index Persona column is derived, not hand-kept.
- **hard epic-scope test-spec requirement (CR0096):** the deferred half of CR0085 - the
  AC-to-test bridge is now mandatory at epic scale. `verify_ac epic-ts --epic EPxxxx` requires an
  epic to have a test-spec (linked by its `Epic:` field) whose AC Coverage Matrix passes
  `ts-check`; gated by `quality.epic_requires_test_spec` (default true), single-story work exempt.
  Reuses `ts-check` (no new verification logic); documented in `reference-epic.md`.
- **done-requires-verified toggle + status verification lane (CR0095):** the deferred half of
  CR0084. `quality.done_requires_verified` (default true) lets a project set the story->Done
  AC-verify gate policy in `.config.yaml` - false downgrades it to advisory-warn project-wide
  (per-call `--force` still overrides). And `status` now reads `verify-report.json` and surfaces
  a verification lane (stories with unverified ACs; the manual-AC count), so env-bound/manual ACs
  read as "deferred", not silent gaps.
- **reconcile-before-plan (CR0094):** `sprint plan` runs `reconcile detect` first and surfaces
  index drift - warns by default, refuses under `--strict`. The planner reads each unit's file
  `Status`, so a stale index misleads selection; reconcile-first guarantees a clean census.
  Mechanical drift only - semantic staleness (a unit whose feature shipped elsewhere) still
  needs the audit + grooming (LL0007). Documented as step 0 of the loop in `reference-sprint.md`.

- **authoring sprint - PRD to a reviewable backlog (RFC0019, CR0088-0093):** `sprint` now drives
  greenfield authoring. `sprint <prd.md> --goal design` bootstraps **PRD → epics → stories**
  (CR0088 PRD-input planner; CR0089 decomposition via the shared `epic`/`story` core + batch
  create) with two STOPs - approve the epic cut, resolve open questions (CR0090; `--autonomous`
  records-and-proceeds). The **goal ladder** gains `--goal plan` for sprint planning
  (select + sequence + estimate → `sprint.py plan --write` artifact; CR0091); the rungs are
  cumulative stop-points and NL maps to the furthest one. `--goal design` assigns story points,
  projected into the index by `reconcile fields` (CR0092); the closing **consistency pass** runs
  `ac_scope` + `ts-check` + `reconcile fields` + `validate` + `integrity` over the produced
  backlog (CR0093). The loop is documented in `reference-sprint.md`; never implements at
  `design`/`plan`.
- **greenfield runbook (CR0081):** `help/getting-started.md` gives the canonical command order
  from an empty repo to a reviewable backlog (`init -> prd -> persona -> trd -> tsd -> epic ->
  story -> reconcile/validate`) and on through the implementation handoff, each step with
  why/command/output/next. Linked from the SKILL router and `init`'s next-steps. It names the
  decisions log and the future authoring loop at the right points, and documents autosprint's
  **cold-start precondition** (a runnable gate) plus the foundation-first handoff - also
  mirrored into `reference-autosprint.md`.
- **agent-instructions enforce the tool-first discipline (CR0083):** the shipped
  `templates/agent-instructions.md` (read by every consuming-project agent; `.CLAUDE.md`
  inherits it via `@AGENTS.md`) gains a mandatory "use the deterministic tooling" rule -
  bootstrap with `init`, create via `new`/`batch` (never hand-roll ids/indexes), the index is
  derived, a story reaches Done only when its executable ACs pass, foundation-first then
  autosprint. The root cause every greenfield friction shared: agents improvise because
  nothing tells them to trust the tooling. Dogfooded into this repo's own `AGENTS.md`.
- **cross-epic AC scope lint (CR0086):** `ac_scope.py check` flags, advisory, a story whose
  acceptance criteria reference a distinctive capability keyword owned by a different epic's
  title (the un-Done-able-in-its-own-epic defect the field audit found - US0002/US0018 reached
  into EP0006/EP0003). Heuristic, read-only, never auto-edits; the operator splits or
  re-scopes. The "single most useful defect" the dogfooding surfaced, now caught at authoring.
- **Definition-of-Done gate on `transition`/`close` (CR0084):** a story moving to Done is
  refused when it declares executable (non-`manual`) ACs that are red or never run in
  `verify-report.json` - the safety net for the hand-driven path that a diligent agent
  bypassed (shipping 0/7 by its own green suite). The block is the one deterministic fact
  (the verifier result); `--force` overrides (recorded). Scoped to stories - CR/epic/bug
  closures, manual-only / AC-less stories, and dry-runs are never gated. Pairs with CR0085
  (the gate is a clean signal only once the TS matrix makes names converge).
- **test-spec as the AC-to-test bridge, enforceable (CR0085):** `verify_ac ts-check --spec
  <ts> [--verify-report <json>]` validates an AC Coverage Matrix is not decorative - every AC
  mapped to a passing test case, no placeholders, cross-checked against the live report.
  `verify_ac lint` flags Verify lines that fall through to `shell` as mis-written runner
  calls (`npm test -- ... -t`, `curl ... returns N`), nudging to the DSL - catching the 0/7
  drift at author time. `verify_ac run --id USNNNN` adds grammar parity with `transition`.
  The TS-bridge + DSL discipline is documented in `reference-verify.md`. (Deferred to a
  follow-up: a hard epic-scope TS requirement wired into epic-implement, and a status manual
  lane - both touch the model-driven workflow surface.)
- **reconcile projects file-owned index cells (CR0082):** `reconcile fields` (`--apply`)
  syncs the index's `Title` and `Points` cells from the backing story files, so the index is
  fully derived (LL0001) and the audited story-points hand-copy disappears. A field absent in
  the file is left untouched (BG0032 no-clobber); persona is deferred (no single canonical
  field in a story). `apply` and `fields` are now documented (the entry was stale at
  read-only/`detect`).
- **project decisions log (CR0080):** `scripts/decisions.py` (`add` / `list`) maintains
  `sdlc-studio/decisions.md` - the canonical, append-only home for load-bearing decisions,
  both product (scope cuts, resolved PRD open questions) and implementation conventions
  (error envelope, ID scheme, token strategy, migrations, test harness). `init` seeds it
  empty. The project "spine" lives in one place and feeds the delegated-agent handoff
  context, instead of being scattered and pasted per prompt. Distinct from the autosprint
  per-tranche ledger.
- **batch artifact creation (CR0078):** `artifact.py batch --type <t> --spec <items.json>`
  creates many artifacts of one type in one atomic pass - a reserved contiguous id block
  (LL0002), every index row, and every story-to-epic link wired together; a missing epic or
  id collision aborts before any write; `--dry-run` previews the id map. Defaults to
  `--template full` (the fan-out case where delegated agents fill pre-wired scaffolds rather
  than coordinate structure).
- **executable `init` (CR0079):** `init` was a manual checklist; it is now `scripts/init.py`.
  `init run` creates the full `sdlc-studio/` directory tree, pre-creates every per-type
  `_index.md` (reusing the CR0077 helper, so the first `new` of any type is indexed), seeds
  `sdlc-studio/.config.yaml` + the `AGENTS.md`/`CLAUDE.md` starters from templates, and with
  `--scaffold` seeds the singleton docs (prd/trd/tsd/personas). `--detect` infers the stack;
  idempotent (never overwrites without `--force`); `--dry-run` previews every write so the
  workflow can confirm config before applying. The CR0077 index-bootstrap moved to the shared
  `file_finding.ensure_index` (single source, used by both `new` and `init`).
- **greenfield `new`: lazy index creation + full-template scaffolds (CR0077):** `artifact.py new`
  now creates a missing `<dir>/_index.md` from `templates/indexes/<type>.md` on first use (the empty-
  project first run), so the very first artifact of a type is indexed like every later one - closing
  the misleading `indexed=false` signal that taught a greenfield agent to hand-manage indexes.
  `--dry-run` reports `would_create_index`. New opt-in `--template full` grafts the rich
  `templates/core/<type>.md` body onto the deterministic provenance head (minimal stays the default;
  validate/provenance behave identically). Part of the greenfield-friction workstream (CR0077-0086).

### Changed

- **`autosprint` renamed to `sprint` (CR0087, WS0 of RFC0019):** the command is now the whole
  sprint lifecycle (`--goal plan` / `design` / `done`), not just autonomous delivery - autonomy
  is the `--autonomous` flag, not the name. `scripts/autosprint.py` → `scripts/sprint.py`,
  `reference-autosprint.md` → `reference-sprint.md`, `help/autosprint.md` → `help/sprint.md`, and
  the live command surface now says `sprint`. **`autosprint` stays as a deprecated alias** (a
  re-export shim + NL resolution) so nothing breaks. History (closed CRs, RFC0001, prior
  CHANGELOG entries) keeps the original name.

## [2.5.0] - 2026-06-22

### Added

- **CI coverage + security gates (CR0076):** `lint.yml` now runs a coverage floor (>= 80% of the
  runtime scripts; currently 83%) and a `bandit` Python security scan. Three intentional patterns got
  justified `# nosec` (the project-authored AC verifier's `shell=True`; the https-only version check).
- **Test-reference routing map (CR0075):** `help/references.md` now maps the five `reference-test-*.md`
  to their distinct tasks (spec / automation / best-practices / brownfield-validation / E2E), so the
  right one is obvious. (A physical file-merge was assessed and deferred - the files are genuinely
  distinct and a merge would bloat an at-ceiling file for marginal gain.)
- **Navigation entry points (CR0074):** a 'which persona doc do I use' routing table
  (`reference-persona.md#which-doc`), a grouped overview of the gate's checks in `help/gate.md`
  (artifact-quality / index / provenance / skill-docs - replacing its stale 5-check line), and
  Progressive-Loading rows for persona create/consult and test-spec/automation.
- **doc-freshness advisory gate check (CR0073):** a new non-blocking `gate.py` check that flags when
  `LATEST.md`'s claimed version / test count / disclosure count drift from reality - the state-anchor
  staleness the audit caught by hand. Skill-only, read-only; only checks facts LATEST.md actually states.

## [2.4.4] - 2026-06-22

### Fixed

- **npm vulnerabilities cleared (BG0033):** the 5 moderate advisories (brace-expansion, js-yaml,
  markdown-it, smol-toml via `markdownlint-cli`) are gone - `npm audit fix` + `markdownlint-cli` ^0.49.0.
  `npm audit` reports 0; lint still passes on the new line.

### Changed

- **project_upgrade determinism hygiene (CR0071):** `.version` date is now injectable (deterministic
  tests) and the persona scan uses a sorted glob - reproducible regardless of filesystem order.

### Added

- **Test-density backfill (CR0070):** +145 substantive tests on the highest-risk under-tested scripts
  - `repo_map` (13->69), `github_sync` (15->59, `gh` fully mocked), `lessons` (13->58) - covering AST
  parsing, the sync diff/state logic, recall/prune, and edge cases. Suite now 789 tests. (Surfaced two
  documented behaviour-limits; a lessons docstring was corrected.)
- **CONTRIBUTING dev-bootstrap (CR0072):** a Development Workflow section (setup, gate-every-commit,
  trunk-based discipline, the bug/CR/RFC lifecycle, the regression-test obligation, forward-porting)
  plus an Architecture pointer - so a new contributor can get productive without reading the source.
- **Table-parser regression battery (CR0069):** a 20-test edge-case suite (`test_table_parsers.py`)
  locks the shared `table_cells` / `join_row` / `canonical_status` primitives - escaped pipes,
  ragged/empty/unicode cells, separator variants, join round-trip, status-token boundaries. Closes the
  reconcile-lineage fault class at the parser level (no live bug found; pure hardening).
- **`deploy` - the orchestrate-only deploy last-mile (RFC0013, CR0066-0068):** a new workflow that
  **gates** before, **verifies** after, and **records** a deploy - without owning the runtime. The
  project supplies `deploy.{command,smoke,soak_minutes,rollback}` in `.config.yaml`; the skill never
  holds the production trigger, never auto-rolls-back, and **never deploys inside `autosprint`**
  (deploy is a stop-condition action). `scripts/deploy.py preflight` gives a gate-backed readiness
  verdict + the operator hand-off; `deploy.py record` logs the outcome to `sdlc-studio/deploy-log.md`.
  Smoke green == rolled-out; a soak window is required for verified. Ecosystem-neutral; no secrets read.
- **Domain-neutrality lint guard (`lint:neutrality`):** a CI check fails if a private
  project/product/repo name appears in a tracked file. The blocklist is stored as SHA-256
  **hashes** (never plaintext) so the guard - itself a public file - does not reveal the names it
  guards, and its output redacts matches to a hash prefix. Sub-token aware (a base name catches
  hyphenated variants). Caught and cleared 3 pre-existing leaks on first run.

## [2.4.3] - 2026-06-22

### Added

- **RFC0013 (deploy last-mile) pressure-tested and settled:** four adversarial lenses sharpened it
  to **Option A orchestrate-only** (skill gates + verifies + records around an operator-triggered
  deploy; no auto-execute, no auto-rollback, never inside the autonomous loop); D1-D7 decided, build
  deferred until a consuming project needs a deploy it cannot already sequence itself.
- **Document-owner review seats + requirements-met sign-off (CR0065):** the **Product Owner** seat
  owns the PRD and signs a "PRD requirements satisfied" verdict in `review` (every project); the
  **Product Manager** seat owns the PVD and signs a "PVD requirements satisfied" verdict via a new
  PVD review leg - **only when `sdlc-studio/product/pvd.md` exists** (a single-repo project has no
  PVD, so neither the seat nor the leg applies). Corrects the prior workflow-personas mislabel that
  called the product/PRD seat "PM".

## [2.4.2] - 2026-06-22

### Fixed

- **reconcile reads the Status cell by vocab token, not a fixed column (BG0032):** indexes whose
  tables stack multiple schemas (Status in different columns) or have header-less blocks no longer
  misread off-schema rows as `Unknown` (which produced phantom status/count drift); apply rewrites
  only when the pinned column holds a status, never guessing a cell. (~90 phantom drifts -> 9 on a real repo.)
- **`project upgrade --apply` no longer bundles reconcile (BG0029):** it applies only the safe
  deterministic set (config + `.version`); reconcile is opt-in via `--with-reconcile`, so an upgrade
  can't rewrite/corrupt indexes. Index drift is reported as a `review with reconcile` item.
- **`.version` bump preserves author fields (BG0030):** the skill/schema bump is a surgical update
  that keeps `created_at` (and any other lines) instead of overwriting from a template.
- **reconcile `--apply` never deletes index rows (BG0031):** orphan/missing rows stay report-only;
  an inline-only record is never removed. Locked with a regression test.

## [2.4.1] - 2026-06-22

### Added

- **Charter review fast-follow:** the agent-instructions starter documents the one-canonical-summary
  index convention and the `Verify: manual` / never-hand-stamp rules.

### Fixed

- **verify_ac handles prose/manual Verify lines (BG0028):** a Verify line led by `manual`/`manually`
  is counted **manual** (never executed), so a human-checked AC can't be shelled out, time out, and
  report a false `failed`. Real commands are unaffected. `Verify: manual <description>` documented.
- **persona checks ignore non-design files (BG0027):** `project upgrade`'s old-model detector and
  `validate personas` no longer flag a `consult-guide`, a README, or the `seats/` review-seat charters
  as old/ill-formed design personas - so a migrated project stops reporting a phantom persona item.
- **reconcile no longer corrupts per-epic count tables (BG0026):** `reconcile --apply` (and thus
  gate/autosprint/`project upgrade`) recomputes only the canonical global summary (the `Status|Count`
  block with a `**Total**` row, or the sole summary); scoped per-epic/per-section count tables are left
  to the author. Previously it stamped the fleet total into every one (hit a consuming project: per-epic Done 6 -> 590).
- **project upgrade dry-run now reports the stale `.version` bump (BG0025):** a present-but-stale
  `.version` (older skill than installed) is reported as auto-correctable, matching what `--apply`
  does - the dry-run no longer says "nothing auto-correctable" while apply bumps it.
- **version_check no longer serves a stale `latest` older than installed (BG0024):** a fresh
  TTL cache whose `latest` predates the installed version is treated as stale and re-fetched (you
  cannot install newer-than-latest), so post-release the check stops reporting the old version.

### Changed

- **Consumer-copied templates carry no framework tracking IDs:** the persona template, review-seat
  charter, `config-defaults.yaml`, and `product-manifest.yaml` no longer cite the framework's internal
  RFC/CR numbers in their comments, so a project that copies them gets no framework-provenance noise.
- **Disclosure backlog driven to zero (CR0064):** fixed the 28 real gaps the disclosure check found
  in the skill's own source (24 scripts `chmod +x`, 4 `Load when:` markers, 2 section files indexed)
  and refined the check to clear 38 false-positives - help/<type>.md is reachable via the
  `help/{type}.md` Progressive-Loading pattern, and the template placeholder check is scoped to
  `templates/core/` (fill scaffolds), not guidance modules/prompts. `disclosure` now reports 0.

## [2.4.0] - 2026-06-21

### Added

- **Critic verdicts no longer trip MD037 (BG0023):** `critic._clean` now escapes `_` so an
  underscored identifier in the issues text cannot pair into markdown emphasis - a recurring lint
  papercut when recording verdicts about code (`_read`, `_index_row`).
- **Progressive-disclosure + best-practice check (CR0063):** `scripts/disclosure.py` (advisory) flags
  reference-/help- files missing a `Load when:` trigger or orphaned from every index, plus best-practice
  items (scripts executable + `--help`, templates use `{{placeholder}}`, SKILL.md has When-to-Use). The
  skill is loaded into sessions, so disclosure discipline is a token lever; the check holds new files to
  it and reports the existing backlog. Skill-dev only (no-op for consuming repos); wired into the gate
  NON-BLOCKING; `--strict` opts into enforcement. `npm run lint:disclosure`.
- **`project upgrade` - migrate a consuming project to current conventions (CR0062):** `skill-update`
  updates the tool; `project upgrade` (`scripts/project_upgrade.py`) updates a consuming PROJECT's
  artefacts. It detects the version/convention gap and reports a migration plan split into
  auto-correctable (scaffold `.config.yaml` with a `provenance.adopt_after` cutoff, scaffold/bump
  `.version`, reconcile drift - applied only with `--apply`) and needs-judgement (old personas ->
  Cooper / review-seat charters, AGENTS refresh, missing `Verify:` - reported, never auto-applied,
  never filed as CRs). Dry-run by default, idempotent; skill-update offers it after a version bump.

## [2.3.0] - 2026-06-21

### Added

- **RFC0016 resolved - review-seat charters + isolated consults (CR0060):** review seats (the
  Three Amigos + PM/PO owners) are now structured **charters** (`review-seat-charter.md`, with a
  mandatory `shadow`) consulted as **isolated subagents** with an explicit synthesis step, reusing
  the existing critic/decision ledgers as the externalised record. Clears the stale pre-RFC0017
  fields from the consult prompts. The authored-identity tail (broker, drift-detection, ratified
  canon) is declined as out-of-scope (the external identity system). Review seats are distinct
  from RFC0017's Cooper design personas.
- **Stakes-scaled review depth (CR0061):** the autosprint independent critic now scales to risk -
  a full adversarial sub-agent for code/risky units, a lighter recorded review for pure-doc/
  mechanical ones - so review tokens are spent in proportion. The `critiqued` gate still requires a
  committed verdict (the tier is noted), so depth scales without losing honesty. From the RV0004
  over-engineering/token review.
- **Persona well-formedness check (CR0059, RFC0017 WS3):** `validate.py personas` flags a
  goal-directed persona missing a section for its cast role - advisory (exits 0, not in the hard
  gate). Cast-role-aware: the Negative variant (Why-not, no Experience Goals) and Customer/Served
  (Experience + Scenario optional) are not false-flagged; a missing cast role is itself flagged.
  Prefix-matched headings so an unrelated `## Context` does not satisfy Behaviours. Surfaced via
  `persona review`.
- **Cooper goal-directed persona model (CR0058, RFC0017 WS1):** the persona template and
  reference-persona model move from demographic categories to Alan Cooper's goal-directed model -
  a full cast (Primary / Secondary / Supplemental / Negative / Customer / Served), ordered End
  goals + Experience goals, and a **well-formed persona file** as the bar (structural, not
  research-gated; a Negative persona uses a variant shape - goals stated-to-exclude + a why-not -
  per the dogfood learning). Design personas (the product's users) are distinguished from review seats
  (the Three Amigos, RFC0016). No research/evidence apparatus and no authored-identity machinery -
  a goal-directed persona is good input to an external identity system, nothing sdlc-studio builds.
- **Unified artifact create paths (CR0057):** the two create paths (`artifact new` and the
  finding filer `file_finding`) no longer diverge - the filer now writes the same provenance
  stamp (so `provenance check` stops false-flagging filer-created artifacts), both build index
  rows through one shared header-driven builder (`sdlc_md.row_from_header`, `find_data_header`,
  `join_row` - also used by reconcile), and `--dry-run` (preview, write nothing) is available
  on `artifact new`/`close`, `file_finding file`, and `pvd sync`.
- **artifact new correctness (BG0022):** a story created for a non-existent epic now raises
  before writing any file (no silent orphan), and id allocation honours local files, lingering
  index rows, AND origin/main (`next_id.allocate_number`) - never re-issuing an id that exists
  only on the remote or as a stale index row.
- **Help reframed around autosprint (CR0054):** help now leads with getting-started and the
  autosprint (Goal-Driven Development) loop as the recommended path; the by-hand per-tool
  pipeline is retained but secondary. The catalogue lists every command (pvd, gate, provenance,
  telemetry, artifact new/close, skill-update, product reconcile); references.md adds
  reference-autosprint/-pvd/-skill-update; arguments.md adds the autosprint and gate flags.
- **Unfilled-placeholder gate (CR0056):** a freshly-scaffolded story used to pass conformance
  (specified + verifiable) and validate with pure `{{placeholder}}` AC/Verify content - a hidden
  hole. validate now flags a metadata or AC-structural line whose value is placeholder-ONLY as
  an error, and conformance treats a placeholder-only AC/Verify as not-yet-specified (a scaffold
  cannot reach Done with unfilled slots). Scoped to placeholder-only values, so prose that
  references `{{...}}` syntax and a real AC that mentions a token are never flagged; the two
  gates agree on what counts as filled.
- **Gate duplicate-id + provenance checks (CR0055):** the gate now flags duplicate artifact
  ids - both duplicate files (next_id) and duplicate index ROWS (reconcile keyed rows into a
  dict, so a second `US0001` row silently overwrote the first: zero drift, false PASS - now
  `reconcile.detect_duplicate_rows` counts the raw rows). Provenance is also registered as a
  gate check, blocking only when `provenance.enforce` (the constitution opt-in pattern).
- **Documentation in the autosprint Definition of Done (CR0053):** a new `documented`
  conformance stage + a deterministic `scripts/doc_coverage.py` gate - every Type-Reference
  command must be in the help catalogue and every script in reference-scripts.md (a prose
  mention does not count); empty CHANGELOG [Unreleased] is a soft warn; no-op for consuming
  repos. Wired into the gate (blocking) + conformance. reference-autosprint's DoD now requires
  user/operator docs updated, a structured final report, and a Phase-1 clarify step. Closing
  the gap the self-audit found - it immediately forced 15 undocumented commands/scripts green.
- **Artifact provenance: stamp + check + remake (CR0052):** `new` stamps every artifact
  it creates (`> **Created-by:** sdlc-studio ...`); `scripts/provenance.py check` flags
  un-stamped artifacts past `provenance.adopt_after` with remediation (advisory;
  `provenance.enforce` to block; legacy exempt); `remake` content-preservingly backfills
  the stamp (idempotent, dry-run-able, header-anchored - never touches the body). Makes
  deterministic creation the checkable path.
- **Portable CI quality gate (CR0046):** `scripts/gate.py` aggregates the
  deterministic checks (conformance, reconcile drift, validate, constitution, integrity)
  into one consolidated pass/fail and exits non-zero only on a blocking failure; `--only`
  /`--skip` select checks, constitution blocks only when enforced, and a wrong/missing
  `--root` fails rather than passing vacuously. No network, no CI/cloud assumption -
  runnable in any CI or a pre-commit hook (`help/gate.md` shows GitHub Actions / GitLab /
  shell wiring).
- **Product Vision Document - the multi-repo product layer (CR0047, RFC0015 WS1):** a tiered
  `templates/core/pvd.md` (vision/goals/feature-map/cross-repo-deps/contracts/risks/decisions
  always; topology tree + G1-G5 gates + release coordination opt-in) and a
  `templates/product-manifest.yaml` listing the child repos. The PVD coordinates and traces
  (product feature -> owning repo -> PRD feature), never re-specifies; Product Manager owns it.
- **PVD projection + drift (CR0048, RFC0015 WS2):** `scripts/pvd.py sync` projects the one
  writable master PVD into each child repo read-only (copy in dev, symlink in prod);
  `drift` reports in-sync / stale / behind / missing, and an unreadable/missing master
  reports error rather than a vacuous in-sync.
- **Cross-repo feature-map traceability (CR0049, RFC0015 WS3):** `scripts/product_reconcile.py`
  verifies every product feature `PF####` in the PVD maps to a feature actually declared in
  its owning repo's PRD (orphan / unknown-repo / missing-path block; absent repo + empty map
  degrade with an un-verified count). Declaration-anchored - a prose mention never false-passes.
  Completes the PVD core (WS1-3); the contract layer + governance stay deferred.
- **Deterministic artifact create + close (CR0045):** `scripts/artifact.py new --type <any
  of the 8 numbered types>` allocates the id, renders a valid scaffold, appends the
  header-matched index row, recomputes counts, and wires a story into its epic's Story
  Breakdown - one command for what was a ~10-step hand cascade. `close --id` terminal-
  transitions by id. Shares file_finding.append_index_row. This CR's own story (US0035) was
  created and closed *by the tool itself* (dogfood).
- **Run telemetry recorder (CR0050, RFC0014 WS1):** `scripts/telemetry.py record` appends a
  per-unit run outcome to the gitignored `sdlc-studio/.local/telemetry.jsonl` (local-only, no
  network, advisory - never raises into the loop; only whitelisted non-None fields written).
  Feeds the deferred calibrate step + RFC0009 WS5.
- **Close cascade records telemetry (CR0051, RFC0014 WS2):** `artifact close` records a
  telemetry event (id, type, plus `--iterations`/`--verdict`/`--wall-time-s`/`--stages`)
  after the transition - advisory, never affects the close. Run data now accrues
  automatically on every unit close.

## [2.2.0] - 2026-06-21

Self-update: the skill now notices new releases itself. On the first `status`/`hint`
of a session it compares its installed version against the latest GitHub release and
prints a one-line notice if newer; **`skill-update`** upgrades the scope-detected
install on confirm, with a per-version snooze so it never nags. On by default, silent
offline, opt-out via `version_check.enabled`. Drop-in upgrade from v2.1.

### Added

- **Skill version check + `skill-update` (CR0044):** on the first `status`/`hint` of a
  session the skill compares its installed version against the latest GitHub release and
  prints a one-line notice if newer; `/sdlc-studio skill-update` upgrades the
  scope-detected install (user / project / agents) via the installer on explicit
  confirm. Deterministic `scripts/version_check.py` (TTL-cached, silent offline,
  per-version snooze so it never nags until a newer release); on by default, opt-out via
  `version_check.enabled: false`. Distinct from `upgrade` (project schema migration).

## [2.1.0] - 2026-06-21

Goal-Driven Development arrives: the **`autosprint`** autonomous loop with hard
guardrails (decisions ledger, iteration cap, completion oracle, conformance gate,
independent critic), plus a deterministic control plane around it - complexity +
churn-weighted test risk, a portable adversarial `audit` harness with a deterministic
filer, an optional project `constitution` gate, progressive-disclosure index archival,
deterministic status transitions, and per-project config. No artifact-schema change
(`schema_version` still 2); a drop-in upgrade from v2.0.

### Fixed

- **Escaped pipes in table cells (BG0021):** every table parser now shares one
  `sdlc_md.table_cells` splitter that honours `\|`, so a cell that legitimately
  contains a pipe (e.g. an index title `string \| string[]`, an RFC workstream
  `All\|Crew`) no longer shifts the columns after it and misreads the row.
  Unified `reconcile`, `critic`, `rfc`, and `ledger` onto it.

### Removed

- **15 baked fictional-character persona files (RFC0007 / CR0034):** the
  `templates/personas/stakeholders/**` and `team/**` characters (~1680 lines of
  invented backstory shipped in every install) are removed. Personas now generate on
  demand: `persona create --from-archetype <slug>` builds the full persona from
  `persona-template.md` + the retained archetype seeds (role + one-line disposition)
  in `reference-persona.md#archetypes`. A migration note is in that file; a consuming
  project regenerates any personas it referenced. Aligns with Create-vs-Generate.

### Changed

- **Test references consolidated (RFC0008 / CR0033):** the triplicated test
  anti-patterns are deduped into one `reference-test-best-practices.md#test-anti-patterns`
  section (8 patterns + the integration-dependency and low-coverage checklists);
  `reference-test-pitfalls.md` and the subsumed `#common-ai-testing-mistakes` section
  are removed (no content lost); and `reference-test-validation.md` /
  `reference-test-e2e-guidelines.md` are now reachable from the SKILL.md router.
- **repo_map documented honestly (RFC0004 / CR0032):** reframed as a lexical
  relevance ranker (token overlap + import in-degree bonus), not a semantic call
  graph or PageRank, with a soft-dependency pointer to Aider's repo map / RepoMapper
  for graph-based ranking. Documentation only; ranking behaviour unchanged.
- **`reconcile.apply_type` decomposed (CR0030):** acting on RFC0009's own
  refactor-first signal (the complexity tool flagged it as the top hotspot at
  cognitive 56), `apply_type` is split into single-purpose helpers and reduced to 7,
  with behaviour held identical by the CR0026 corruption-guard suite and a regression
  guard against regrowth. No behaviour change.
- **Strict Agent Skills spec conformance:** the Claude-Code-only
  `argument-hint` frontmatter field is dropped (its content is already in the
  description verbatim) and `tools/validate_skill.py` now enforces the spec's
  closed six-field set - exactly what the official `skills-ref` validator
  rejects ("Unexpected fields in frontmatter"). The skill now passes strict
  reference validation.

### Added

- **Complexity/churn test-risk band (RFC0009 WS4 / CR0043):** `complexity.py` gains a git
  `churn` signal and a churn-weighted `composite_risk` band (low/medium/high) exposed by
  `assess` as `risk_band`. Churn is weighted ~3x complexity - grounded in the calibration
  (bug-affected files were ~4.9x more churned vs ~1.8x more complex). A complex- or
  hot-alone file floors to at least medium. `reference-test-best-practices.md#complexity-test-risk`
  maps the band to coverage / scenario / verification-tier depth. WS5 (wave-sizing by run
  cost) stays deferred - the calibration proves defect risk, not cost.
- **Deterministic status-transition helper (CR0042):** `scripts/transition.py set --id
  <ID> --status <new>` performs the last hand-driven write cascade - set the artifact's
  `Status`, sync its index row + summary counts (reusing `reconcile.apply_type`), and
  tick/untick a story's checkbox in the parent epic's Story Breakdown. `index_synced`
  reflects the true post-state (warns on an archived row or a status with no summary
  row). Retires the manual "mark it Done + update the index" edit.
- **Progressive-disclosure indexes (RFC0012 / CR0041):** `scripts/archive.py archive
  --type <t> --release <r>` bounds a large `_index.md` by moving the master table's
  terminal rows into `<type>/archive/{release}/{type}.md` (rows move, files stay),
  leaving a bullet pointer. `reconcile.parse_index` now unions the archive sub-indexes,
  so the census stays exact (archived artifacts are never `missing-row`; counts =
  active+archived) - the stale-counts risk is removed by counting the real archived
  rows, not a summary. Conventions + slice-read guidance in reference-outputs.md.
  Proven read-only at scale on consuming repo B (371 stories / 407 CRs archivable).
- **Project constitution gate (RFC0005 / CR0040):** an optional
  `sdlc-studio/constitution.md` lets a project declare inviolable principles;
  `scripts/constitution.py check` asserts the machine-checkable ones across the artifact
  graph. Each checkable principle carries a `` `rule:` `` from a fixed vocabulary
  (story-requires-epic, story-has-ac, ac-requires-verify, links-resolve, status-in-vocab,
  no-index-drift) that maps onto the existing integrity/conformance/validate/reconcile
  checks; free-text principles are advisory. Advisory by default; `constitution.enforce:
  true` makes a violation fail the check. Proven against consuming repo A + consuming repo B.
- **autosprint `--order wsjf` (RFC0009 WS3 / CR0038):** the WSJF stub is now real -
  priority stays dominant and the cognitive complexity of a unit's `Affects` files
  (scored by complexity.py) breaks ties within a priority, so the smaller blast-radius
  job goes first; the plan also carries a complexity-weighted per-unit token budget.
  Degrades to plain priority when no complexity is known; complexity never overrides
  priority; dependencies still win.
- **Packaged skill-audit lens pack (RFC0002 WS5 / CR0039):**
  `templates/audit-profiles/skill.md` declares the four skill lenses as a loadable
  profile for the audit harness.
- **Adversarial audit harness (RFC0002 / CR0035-CR0037):** the portable, tool-neutral
  `audit` methodology - `reference-audit.md` (find -> refute-panel verify -> merge ->
  file pipeline, project + skill lens profiles, N-of-M refute, budget controls), the
  `templates/automation/audit-{finder,refute,classify}.md` prompt harness, and a
  deterministic `scripts/file_finding.py` filer that writes a structured (non-hollow)
  Bug/CR/RFC, allocates the ID, and keeps the index in sync. The wired `/audit` command
  (WS4) and skill-profile pack (WS5) remain deferred.
- **Code-complexity signals (RFC0009 / CR0028 / CR0029):** new `scripts/complexity.py`
  computes cognitive (SonarSource) and cyclomatic complexity per function from Python's
  `ast` (pure stdlib; `lizard` soft-dep for other languages, degrading to unscored).
  `repo_map` emits per-function scores into the map. `code plan` (reference-code.md
  step 6b) runs `complexity assess` over a change's blast radius to weight the estimate
  by difficulty and recommend a scoped refactor-first for hotspots - advisory, never a
  gate. Threshold is `complexity.cognitive_high` (default 15). WS3/4/5 stay deferred.
- **Per-project status vocabulary (CR0027):** a project can declare extra statuses
  in `sdlc-studio/.config.yaml` under `status_vocab.<type>` (e.g. `story: [Gated]`)
  and reconcile/validate/conformance recognise them instead of parsing the row as
  `Unknown`; extensions add to the shared base, never replace it. `Blocked` is now a
  base story status. Reads via a new fully-degrading `sdlc_md.project_override`.
- **Conformance adoption cutoff (CR0027, extended CR0031):** `conformance.adopt_after:
  USnnnn` exempts pre-adoption stories - both from the conformance gate (reported,
  never counted non-conformant) and from `validate`'s `no-ac` error - so a project that
  turns the AC discipline on partway is not buried in permanent legacy findings. Fails
  safe: any uncertainty (no config / no PyYAML / malformed / unparseable id) judges the
  story as before.
- **`reconcile apply` (RFC0003 / CR0026):** the mechanical index fixes are now a
  deterministic, idempotent script step - `reconcile apply [--scope] [--dry-run]`
  rewrites each drifted index row's Status cell (positionally, by header) to the
  file's status and recomputes the summary counts from the same `parse_index`
  authority `detect` uses. `--dry-run` reports without writing; cells are
  re-escaped on write; structural classes (missing/orphan-row, missing-index)
  stay report-only. Replaces ~3-4k tokens of re-derived prose per cadence trigger.
- **Generic `agents` installer target:** `--target agents` installs to
  `.agents/skills`, the neutral directory read by Codex, Gemini CLI, Copilot,
  and Cursor - one copy serves all four. `codex` and `agents` resolve to the
  same directory and the installers dedup; docs note Claude Code does not
  read it.

## [2.0.0] - 2026-06-12

The open-format release. SDLC Studio is now formally a standard
[Agent Skill](https://agentskills.io) - one folder that works in Claude
Code, Codex, Gemini CLI, opencode, and Copilot - with an installer that
keeps every copy fresh, consolidated and budgeted documentation, two new
deterministic helpers, CI guards for spec conformance and version
consistency, behavioural eval scenarios, and two workflow gates adopted
from AWS AI-DLC. No consuming-project migration: the artifact schema is
unchanged.

### Changed

- **SKILL.md frontmatter conforms to the Agent Skills open standard**
  (agentskills.io): adds `license`, `compatibility` (Python 3.10+, gh CLI;
  agentic waves Claude-Code-only), `metadata.version`, and `argument-hint`;
  the description now leads with capability and an explicit "Use when..."
  trigger sentence while keeping every existing trigger term.
- **Script examples use `$CLAUDE_SKILL_DIR`** instead of the project-local
  `.claude/skills/sdlc-studio/` path, so they work at personal, project, and
  plugin install levels; one canonical fallback rule for other tools lives at
  `reference-scripts.md#skill-dir`.
- **Repo-root agent instructions follow the cross-tool convention the skill
  itself recommends:** substantive guidance moved to a new `AGENTS.md`
  (read directly by Codex, Copilot, Cursor, Gemini); `CLAUDE.md` is now an
  `@AGENTS.md` import plus Claude-Code-only notes.
- **Duplicated instruction blocks consolidated to canonical homes** with
  do-not-restate pointers: story completion cascade
  (`reference-outputs.md#story-completion-cascade`), Three Amigos per-persona
  focus lists (`reference-workflow-personas.md`), wave quality gates
  (`reference-project.md#quality-gates`), and the agent prompt template (new
  file). `reference-epic.md` shrinks 1191 -> ~1050 lines.
- **Every reference and help file over 100 lines now opens with a
  `Load when:` hint** (one convention; the older multi-line `Load:` blocks
  renamed), and large reference files gain a Contents list so partial reads
  reveal scope. The story Ready validation pseudocode is replaced by a
  pointer to `validate.py check` (determinism in scripts, judgement in
  Claude).
- **README rewritten for v2** (521 -> ~200 lines): open Agent Skills
  positioning, the five-tool install matrix with per-tool invocation, the
  stale-copy sweep, feature tour, v1.x upgrade notes (no project migration),
  and a v2.1 roadmap (task DAGs, review iteration history, artifact graph -
  recorded from the AI-DLC review).

### Fixed

- **`verify_ac.py` counts stale downgrades.** A `yes` Verified state
  downgraded to `no` now increments the report's `stale` counter (apply and
  dry-run modes); previously it was always 0, hiding regressions from
  `verify-report.json`.
- **`verify_ac.py` inserts new Verified lines at the right anchor.** The
  fallback tracked the first bullet of an AC block instead of the last; the
  Verify line, once seen, now holds the insertion anchor so the canonical
  bullet order (Given / When / Then / Verify / Verified) is preserved.
- **Story workflow phase order reconciled to the 8-phase canon** (Plan, Test
  Spec, Tests, Implement, Test, Verify, Check, Review) across
  `reference-story.md`, `reference-decisions.md` (checkpoint relabel plus a
  missing Phase 8 entry), `help/story.md`, and `templates/core/workflow.md`;
  `--from-phase N` is no longer ambiguous between Tests and Implement.
- **Broken file references repaired:** `reference-epic.md` (epic workflow
  template), `reference-story.md` (cohesion findings template),
  `reference-test-pitfalls.md` (pre-v2 TSD template name), and
  `reference-code.md` (best-practices paths now skill-relative instead of
  `~/.claude/best-practices/`).
- **`install.sh` exit status no longer clobbered by the cleanup trap.** With an
  empty `TMP_DIR` (e.g. `--list-targets`, `--dry-run`), the EXIT trap's failed
  test made the script exit 1 under `set -e` even after success.
- **Best-practices corrections:** `docker.md` Python base images bumped to
  3.13, `openapi.md` example matches the recommended 3.1.1, `postgresql.md`
  drops an EOL version qualifier, `sql.md` notes `/*+ LEADING */` is
  Oracle/MySQL-only syntax.

### Added

- **`evals/` behavioural regression scenarios** - four manually-run
  two-Claude scenarios (worker session + grader session) covering trigger
  routing, the greenfield create path, the generate-mode philosophy gate,
  and reconcile dry-run safety; wired into the release gate. The
  counterpart to `scripts/tests/` for the skill's *instructions*.
- **Blind review gate** (adopted from AWS AI-DLC): before implementation,
  `story plan` re-reads the story's AC and judges the plan's task list from
  the task descriptions alone - no code - asking whether every AC would be
  satisfied as written (`reference-story.md#blind-review`, checkpoint row in
  `reference-decisions.md`). Catches semantic drift that test execution
  cannot.
- **Structured clarification convention** (adopted from AWS AI-DLC): pauses
  pose 2-4 concrete options with an evidence-favoured suggestion instead of
  open prose questions
  (`reference-agent-prompt-template.md#structured-clarifications`, wired into
  the execution contract's blocker row).
- **`reference-agent-prompt-template.md`** - the agentic wave prompt template
  extracted from `reference-epic.md` into its own canonical file (its three
  consumers - epic waves, project orchestration, lessons injection - now load
  it without the rest of the epic reference).
- **`scripts/plan.py` and `scripts/lessons.py`** - stdlib-only helpers that
  replace procedural prose with deterministic, tested code: `plan.py
  list|archive` manages Claude Code plan-mode files under `~/.claude/plans/`
  (active/stale tables, archive by year-month; the one script that writes
  outside `.local/`, to that operator-owned directory, never deleting or
  overwriting), and `lessons.py list|add|prune|recall` manages both lesson
  tiers (project `.local/lessons.md` with L-NNNN allocation and newest-first
  insertion; the skill's cross-project `lessons/` registry with LL-ID
  allocation, `_template.md` instantiation, and `_index.md` row upkeep).
- **`tools/validate_skill.py`** - stdlib-only CI validator for SKILL.md
  frontmatter against the agentskills.io spec subset (name pattern and
  directory match, description length, known-field allowlist, semver
  `metadata.version`); wired into `npm run lint` as `lint:skill`.
- **`tools/check_versions.py` and `tools/check_budgets.py`** - CI guards
  wired into `npm run lint`: the version checker asserts the four
  authoritative version homes agree by structured extraction (never
  repo-wide grep; `--strict` adds the CHANGELOG topmost release for the
  release gate), and the budget guard holds SKILL.md under 500 lines and
  un-allowlisted reference files under 600 (allowlisted files carry a
  recorded ceiling +5% tolerance, so they cannot silently regrow).
  `templates/workflows/release-gate.md` gains both checks plus the eval run.
- **Installer stale-copy sweep:** after installing to the chosen targets,
  `install.sh` and `install.ps1` refresh every other sdlc-studio copy found in
  the known tool locations (identity-checked: only directories whose SKILL.md
  declares `name: sdlc-studio` are touched), reporting each as `old -> new`.
  Opt out with `--no-sweep` / `-NoSweep`; `--dry-run` previews the sweep; the
  Windows CI smoke test asserts both behaviours.
- **`plan` command surface:** `help/plan.md` plus SKILL.md and `help/help.md`
  entries for `/sdlc-studio plan list` / `plan archive`
  (`reference-plan-files.md` existed since v1.7.0 without them).
- **Four best-practices guides:** `typescript.md`, `rust.md` (referenced by
  `reference-code.md` but missing), `java.md`, `csharp.md` (test-automation
  ships JUnit/xUnit templates with no matching guide); best-practices README
  index now lists every guide.
- **Regression tests** for both `verify_ac.py` fixes (stale counting in apply
  and dry-run modes, insertion-anchor parsing).

### Removed

- **`templates/workflows/workflow.md`** - an unreferenced duplicate of
  `templates/core/workflow.md` with divergent phase order and a 7-phase claim.

## [1.9.1] - 2026-06-10

Back-port of production fixes to the read-only helper scripts: `reconcile`,
`status`, and `validate` now tolerate real-world artefact conventions instead of
emitting false-positive drift. Folded in from live use on a project whose
artefacts use mixed id casing, decorated status lines, and plain-bullet
acceptance criteria.

### Fixed

- **`reconcile` no longer false-positives on six artefact conventions.** Case- and
  punctuation-insensitive id matching (a file `cr0001.md` matches an index row
  `CR-0001` instead of double-counting as missing-row + orphan-row); decorated
  statuses (`Done (v2.83.0) · **CR:** CR-0088`) canonicalise to their vocabulary
  token before comparison; status-less files (legacy docs, most CRs) assert
  nothing and are not status-mismatched; summary counts for such types reconcile
  against the index rows, not the file census; `*-consultations.md` notes are
  excluded from the census so they no longer clobber the real artefact; and
  reserved/retired index rows (`Proposed`/`Draft`/custom non-vocabulary states)
  with no file are treated as intentional reservations, not orphans. See
  `reference-reconcile.md#matching-tolerances`.
- **`status` tallies decorated statuses under their canonical token,** so
  `Done (v2.66.0)` counts as `Done` and done-percentages stay correct.
- **`validate` accepts more valid forms.** Acceptance criteria may be `### ACn`
  headings, compact `- **ACn:**` bullets, or a populated `## Acceptance Criteria`
  section; metadata fields parse with or without the leading `>` blockquote;
  decorated statuses pass the vocabulary check.

### Changed

- **Status vocabulary additions:** story gains `Proposed` (optional pre-Draft
  intake state); bug and CR gain `Superseded`. Docs in `reference-outputs.md`
  and `help/story.md` updated to match.
- **`lib/sdlc_md.py`** gains shared `norm_id()` and `canonical_status()` helpers
  and excludes `*-consultations.md` from `artifact_files()`; id regexes are now
  case-insensitive.

### Tests

- Script test count 101 → 123 (id-normalisation, canonical-status, decorated and
  plain-bullet AC, consultations exclusion, reserved-row, and count-authority
  regressions).

## [1.9.0] - 2026-06-09

`init` now seeds (or checks) the project's agent-instructions file, and a new
deterministic hygiene check keeps `AGENTS.md` / `CLAUDE.md` honest - wired into
`/sdlc-studio review`.

### Added

- **`validate.py instructions`** - a deterministic hygiene check for a project's
  agent-instructions files: `AGENTS.md` exists (canonical), `CLAUDE.md` is a
  `@AGENTS.md` pointer, the operating-doctrine and `LATEST.md` pointers are present, the
  pre-release gate and the context-compaction re-read rule are present, and the file is
  not bloated with per-ship narrative or stale version strings. Emits JSON; exits
  non-zero on a missing `AGENTS.md`.
- **`/sdlc-studio review` runs the instruction-file hygiene check** (via
  `validate.py instructions`, alongside `review_prep`), so a stale or bloated
  instructions file is caught as drift.

### Changed

- **`/sdlc-studio init` seeds or checks the agent-instructions file.** When `AGENTS.md`
  is absent, init creates it from `templates/agent-instructions.md` plus a one-line
  `CLAUDE.md` pointer (`@AGENTS.md`); when present, it runs `validate.py instructions`
  and suggests improvements rather than overwriting hand-written specifics. Current-state
  stays in `sdlc-studio/reviews/LATEST.md` (progressive disclosure), not in the
  instructions file.

### Tests

- Script test count 95 → 101 (the instruction-file check).

## [1.8.0] - 2026-06-09

Cross-tool portability and a determinism-first script layer. The skill stops
hard-coding `CLAUDE.md` so it runs from Codex and Copilot too, ships a starter
agent-instructions file, and moves its most mechanical workflows (census,
status, validation, ID allocation, review inputs) into tested read-only Python
helpers that emit JSON. The principle: determinism in scripts, judgement in
Claude. The five-leg review verdict and its CODE leg are never scripted.

### Added

- **Agent-instructions template** (`templates/agent-instructions.md`, plus
  `agent-instructions.CLAUDE.md` and `agent-instructions.README.md`): a
  tool-neutral starter for a consuming project. `AGENTS.md` is the canonical
  cross-tool file (read by Codex, Copilot, Cursor and others); Claude Code's
  `CLAUDE.md` imports it with `@AGENTS.md`. It carries the production-release
  gate (reconcile --verify plus the five-leg review) and the
  autonomous-execution-with-persona-consultation goal inline, and points at the
  doctrine rather than restating it.
- **Five read-only deterministic helpers** under `scripts/`, each emitting JSON
  the workflows consume: `reconcile.py detect` (file-census index drift),
  `status.py` (four-pillar census plus hint), `validate.py` (artifact-structure
  linter), `next_id.py` (cross-repo-safe ID allocation), and `review_prep.py`
  (the mechanical inputs the five-leg review consumes). Shared parsing lives in
  `scripts/lib/sdlc_md.py`, the single source of truth for the markdown
  conventions and the artifact-type and status-vocabulary tables.
- **Link-check CI** (`tools/check_links.py`, `npm run lint:links`): verifies
  every intra-skill `path.md#anchor` reference resolves. `npm test` and the
  script unit tests now also run in CI.
- **Cross-harness installer.** `install.sh` and `install.ps1` gain
  `--target claude|codex|gemini|opencode|copilot|all|auto` (plus `--uninstall`
  and `--list-targets`), installing the standard `SKILL.md` skill into each
  tool's skills directory. SDLC Studio is a standard Agent Skill, so it now runs
  from Codex, Gemini CLI, opencode and Copilot as well as Claude Code; native
  installers (`gh skills install`, `gemini skills install`) work too. New
  `docs/INSTALL.md` is the full install guide; the README install section is
  trimmed to a multi-harness summary that links to it.

### Changed

- **The skill no longer hard-codes `CLAUDE.md`.** Seventeen references across
  nine files now read "the project's agent-instructions file (`AGENTS.md`)", so
  the skill is portable to Copilot and Codex. `help/init.md` and
  `reference-doctrine.md` point at the new template.
- `reconcile`, `status`/`hint`, ID allocation, story Ready checks, and the
  unified review now invoke their helper script first and consume the JSON,
  keeping the manual walk as a fallback. The five-leg review verdict stays
  Claude's; the CODE leg is never scripted.
- The agent-instructions template instructs re-reading `reviews/LATEST.md` and
  running `status` after any context compaction or reset - portable across
  Claude Code, Codex, Copilot, and opencode.

### Fixed

- Hardened the three existing scripts: a corrupt `.local/*.json` now exits 2
  instead of raising a traceback; every `main()` wraps `KeyboardInterrupt`
  (exit 130) and unexpected errors (exit 1) per the script template; fixed a
  `repo_map` import-prefix bug; `github_sync push` no longer re-fetches the
  issue list once per record; removed a dead acceptance-criterion boundary
  block in `verify_ac`.
- Renamed `best-practices/readme.md` to `readme-guide.md` to remove a
  case-collision with `README.md` on case-insensitive filesystems.
- Fixed three pre-existing broken cross-reference anchors
  (`reference-epic.md#post-wave-merge-protocol`, and mis-named anchors in
  `reference-verify.md` and `templates/core/tsd.md`).
- Script test count rose from 46 to 95.

## [1.7.2] - 2026-06-05

Extends the style guard to corporate jargon, and restructures SKILL.md for
token efficiency via progressive disclosure. No behaviour changes.

### Added

- `tools/lint-style.sh` now also fails on the four banned corporate-jargon
  words, filtered through `tools/style-allowlist.txt`. The allowlist
  permits lines documenting the rule itself, plus the established term
  "user journey". The em-dash check now lives in the same script, which
  `npm run lint:style` calls.
- `help/arguments.md` (full flag reference) and `help/references.md` (the
  reference-file and template catalogue), loaded on demand.

### Changed

- **SKILL.md slimmed from 651 to 195 lines (~70%)** by relocating the
  command catalogue, argument reference, workflow diagrams, and reference
  index out of the always-loaded router into lazy-loaded `help/help.md`,
  new `help/arguments.md`, and new `help/references.md`. This cuts the
  per-invocation context cost with no feature loss: all 153 command
  strings and 55 flags are verified present in the relocated files. The
  Progressive Loading Guide gains routing rows for the new files.
- Reworded two metaphorical jargon uses (operator-heuristics, lessons
  help) to plainer wording; these were not allowlist candidates.

## [1.7.1] - 2026-06-05

Style and tooling housekeeping. No content or behaviour changes.

### Fixed

- Replaced 201 em-dashes across the skill docs, templates, lessons,
  README, CHANGELOG, and CLAUDE.md with spaced en-dashes, per the
  house style rule in CLAUDE.md. The v1.7.0 content reintroduced them
  because no automated check existed.
- Corrected a stale line-count note in CLAUDE.md (SKILL.md is 651
  lines, not 584).

### Changed

- `npm run lint` now also runs a style guard (`lint:style`) that fails
  on any em-dash in markdown, so the regression cannot recur. CI picks
  this up automatically via the existing `npm run lint` step.

## [1.7.0] - 2026-06-05

Field-tested patterns from real-world use, generalised and folded back
into the skill. This release adds a design-exploration artifact type,
an operating doctrine for onboarding, a cross-project lessons registry,
and hardening of the reconcile, review, and release workflows. The
v1.6.0 Python helper scripts are unchanged.

### Added

- **RFC artifact type** (`/sdlc-studio rfc`): a first-class artifact for
  exploring an unsettled design space *before* committing to a CR.
  Lifecycle: create, list, review, accept (spawns CRs), close
  (supersede/withdraw). Ships with `reference-rfc.md`, `help/rfc.md`, and
  `templates/core/rfc.md` + `templates/indexes/rfc.md`. RFCs share the
  cross-repo numbering guard with CRs.
- **Operating doctrine** (`reference-doctrine.md`): a project-agnostic
  manual for onboarding a Claude to any sdlc-studio project - the skill as
  an OS, the RFC/CR/ADR decision matrix, files-as-truth and reconcile
  discipline, review cadence, consult gates, TDD default, paperwork in the
  same commit, lessons recall, and cross-repo numbering. Surfaced from
  `/sdlc-studio init`.
- **Cross-project lessons registry** (`lessons/`): a release-curated set of
  generalisable engineering/process lessons (seeded with six) that any
  project can recall before substantive decisions, distinct from a
  project's own transient `.local/lessons.md`. Recall and promote hooks
  documented in `help/lessons.md` and `reference-agentic-lessons.md`.
- **Operator heuristics** (`reference-operator-heuristics.md`): cross-cutting
  patterns for running a live service alongside development - hypothesis
  discipline, memory-entry drift, silent-CLI/proxy failure localisation,
  bug-title framing, external-layer-first diagnosis, post-release briefing,
  and adversarial review as a release gate.
- **Deploy readiness patterns** (`reference-deploy-readiness.md`): platform-
  agnostic post-deploy verification - cold-spawn pre-warm, smoke budget
  sizing, auto-rollback on smoke fail, readiness-wait protocol, and soak
  windows.
- **Plan-file lifecycle** (`reference-plan-files.md`): conventions for
  Claude Code plan files (`~/.claude/plans/`) - active vs archived layout,
  listing, archiving, and anti-patterns.
- **Persona review**: `/sdlc-studio review` now reviews personas (staleness
  map, PRD/CR cross-checks, self-consistency), scans `sdlc-studio/rfcs/`,
  supports `--skip-personas`, and writes a unified `reviews/LATEST.md`
  first-read anchor (`templates/reviews/unified-anchor.md`).
- **Reconcile census + cadence**: reconcile now rebuilds each index from an
  on-disk file census (detecting status mismatch, missing rows, and orphan
  rows), adds RFC scope, detects numeric-claim drift in prose docs
  (report-only, or auto-fix with `--fix-counts`), and emits advisory
  cadence triggers (epic close, ship, CR action, 7-day window) tracked in
  `reconcile-state.json`.
- **Release strategy**: `release_strategy` config (`solo-dev | pr-required |
  staged-rollout`) plus a decision tree (`reference-decisions.md`) that
  branches ship guidance accordingly.
- **Execution contract**: `reference-decisions.md` defines stop conditions
  and anti-patterns for agentic execution after plan approval.
- **Multi-persona pressure-test canvas** (`reference-consult.md`): a
  structured pattern for consulting multiple personas in parallel on
  high-blast-radius design decisions.
- **Verification depth tiers** and **test-timeout tuning** discipline
  (`reference-test-best-practices.md`), recorded per AC and at bug close;
  rollback envelope and per-AC verification target in `reference-story.md`.
- **Release-gate checklist** template (`templates/workflows/release-gate.md`)
  and new config knobs: `personas.staleness_days`, `contract_tables`.

## [1.6.0] - 2026-06-04

Structural upgrades from competitive research against BMAD-METHOD,
GitHub Spec Kit, Kiro, and Aider. Four new capabilities target the
real pain points: agent prompts that hallucinate files, acceptance
criteria that drift from reality, the skill as a parallel universe
to GitHub Issues, and projects that start dumb every time.

### Added

- **Scripts directory convention**: `.claude/skills/sdlc-studio/scripts/`
  now holds skill-internal Python helpers invoked by workflows.
  Documented in `reference-scripts.md`. Ships with three scripts,
  all pure-Python stdlib except where noted, all with unit tests
  runnable via `python3 -m unittest discover -s scripts/tests`.
- **AST Repo Map** (`scripts/repo_map.py`): indexes source files
  by symbols and imports, ranks files by relevance to a story
  description. Supports Python (via stdlib ast), TypeScript,
  JavaScript, Go, Rust, Java, Kotlin, C#, Ruby, PHP, Swift via
  regex extractors. Subcommands: `build`, `query`, `stats`. Output
  at `sdlc-studio/.local/repo-map.json`. The Agent Prompt Template
  now derives its `READ THESE FILES FIRST` list from repo_map
  query output instead of hand-authoring from memory.
- **Executable Acceptance Criteria** (`scripts/verify_ac.py`): AC
  blocks in story files gain optional `Verify:` and `Verified:`
  bullets. `/sdlc-studio reconcile --verify` runs each verifier
  and updates state in place. DSL supports `pytest`, `jest`,
  `vitest`, `go`, `file`, `grep`, `http ... -- <jq>`, and `shell`
  as fallback. Report written to
  `sdlc-studio/.local/verify-report.json`. Story Completion Cascade
  gains an optional gate (`require_ac_verification: true` in
  config) that blocks Done unless every AC reports `Verified: yes`.
- **GitHub Issues Sync** (`scripts/github_sync.py`): two-way sync
  between local CR / Story / Epic files and GitHub Issues via the
  `gh` CLI. Unified model: a CR and its linked Issue are two
  representations of the same record. Subcommands: `push`, `pull`,
  `cascade`, `state`. Label convention uses `sdlc:` prefix. Every
  record template gains a `> **GitHub Issue:**` metadata line.
  reference-cr.md gains a full `/sdlc-studio cr sync` workflow.
  Story Completion Cascade gains step 12 to update linked issues
  on status transitions.
- **Per-Project Lessons**: `sdlc-studio/.local/lessons.md`
  accumulates project-specific failure patterns across agentic
  runs. Loaded at every wave start and injected into Agent Prompt
  Templates as a `Known Pitfalls on This Project` section.
  reference-agentic-lessons.md gains a "Lessons Accumulation"
  section with the file format, four hook points (wave failure,
  post-wave merge failure, epic retrospective, manual add), and
  consumption pattern. `/sdlc-studio lessons list|add|prune`
  commands.
- **Windows PowerShell installer** (`install.ps1`): one-line install
  via `irm ... | iex`, mirroring `install.sh`. Supports `-Local`,
  `-Global`, `-DryRun`, `-Version <tag>`, and `-Help`. README gains
  Windows instructions throughout.

### Changed

- **Verifier DSL** (`reference-verify.md`): new document defining
  the executable-AC DSL, writing guidance, troubleshooting, and
  integration with reconcile.
- **`reference-reconcile.md`**: Phase 2 gains check h) AC
  verification drift. Scope table gains `verify` row that
  delegates to `scripts/verify_ac.py`.
- **`reference-outputs.md`**: Story Completion Cascade gains step
  0 (AC verification gate, conditional on config flag) and step 12
  (external sync push for records with a `GitHub Issue:` field).
- **`reference-cr.md`**: new `/sdlc-studio cr sync - Step by Step`
  workflow inserted between `cr review` and `cr close`.
- **`reference-epic.md`**: Agent Prompt Template instructs authors
  to derive `READ THESE FILES FIRST` from repo_map query output.
  Wave prep loads `.local/lessons.md`. Handle Story Errors appends
  a lesson on failure.
- **`reference-code.md`**: code plan step 6 explicitly runs
  repo_map build + query before the Explore agent.
- **`reference-agentic-lessons.md`**: READ THESE FILES FIRST
  guidance references repo_map. New "Load project lessons before
  exploration" subsection. New "Lessons Accumulation" section at
  end of file.
- **`reference-story.md`**: story-create step 3g emits best-effort
  Verify lines matching AC type.
- **`templates/core/story.md`**: AC blocks gain Verify and
  Verified bullets. Metadata gains `GitHub Issue:` field.
- **`templates/core/cr.md`**, **`templates/core/epic.md`**: both
  gain a `GitHub Issue:` metadata field.
- **`templates/config-defaults.yaml`**: new
  `require_ac_verification: false` gate.
- **`SKILL.md`**: new "Utilities" and "External Integrations"
  command sections. Progressive Loading Guide rows for
  repo-map, verify, github-sync, scripts, and lessons.
- **`help/*.md`**: new help files for repo-map, verify,
  github-sync, lessons. Existing `help/reconcile.md` documents
  `--verify`, `--story`, and `--scope verify` arguments.
- **Templates**: pre-existing markdownlint drift in
  `templates/core/story.md` cleaned up while adding Verify fields.
- **Script hardening**: the three scripts gain release-grade
  robustness: malformed `gh` output and corrupt sync state no longer
  crash `github_sync.py` (graceful fallback), `verify_ac.py` clamps
  out-of-bounds insertion points, all file I/O is explicit UTF-8, and
  every public function is documented. Test suite grows to 46 cases
  covering the new edge paths.

### Config

- `templates/config-defaults.yaml` adds `require_ac_verification`
  (default `false`). Flip to `true` once reconcile reports zero
  manual ACs to enable the Story Completion Cascade gate.

## [1.5.0] - 2026-04-14

Production-run upgrades to the SDLC pipeline. Four new commands, a
formal Three Amigos review model, project-wide orchestration, and
mechanical drift reconciliation. All additions are backwards
compatible with v1.4.0 artefacts.

### Added

- **Change Requests**: `/sdlc-studio cr` lifecycle for post-PRD changes
  - `cr create`, `cr list` (filter by status, priority, type, affects),
    `cr action` (bridges a CR into epics and stories and updates the
    PRD feature inventory), `cr review` (staleness and cascade
    checks), `cr close` (Complete, Rejected, Deferred)
  - New files: `reference-cr.md`, `help/cr.md`, `templates/core/cr.md`,
    `templates/indexes/cr.md`
  - Stored at `sdlc-studio/change-requests/CR{NNNN}-{slug}.md`
- **Project-Level Orchestration**: `/sdlc-studio project plan` and
  `/sdlc-studio project implement`
  - Dependency-graph execution across all epics with topological sort
    and cycle detection
  - Flags: `--agentic`, `--from epics|stories`,
    `--commit-strategy per-wave|per-epic|per-project`, `--resume
    EP000X`, `--skip EP000X`, `--no-artifacts`, `--dry-run`
  - Persistent state at `sdlc-studio/.local/project-state.json` with
    epic-by-epic checkpoints
  - Quality gates at wave, epic, and project boundaries
  - New files: `reference-project.md`, `help/project.md`
- **Reconciliation**: `/sdlc-studio reconcile [--dry-run] [--scope
  stories|epics|prd|crs|indexes]`
  - Mechanical drift detection and repair across stories, epics, PRD
    feature statuses, CRs, indexes, dependency tables, and checkbox
    state
  - Idempotent; runs automatically at epic and wave boundaries during
    agentic execution
  - New files: `reference-reconcile.md`, `help/reconcile.md`
- **Agentic Lessons**: `reference-agentic-lessons.md` captures
  production-tested patterns for wave execution, exploration cadence,
  hub-file sidecar pattern, per-wave reconcile, commit pacing, and a
  failure-mode table. Loaded before any `--agentic` wave execution.
- **Three Amigos Consultation**: formal PM/Eng/QA review model now the
  default for epic create, story create, story plan, and bug fix.
  Personas named (Sarah Chen, Marcus Johnson, Priya Sharma) with
  distinct review remits.

### Changed

- **`reference-outputs.md`**: canonical 11-step Story Completion
  Cascade (previously 6) and 9-step Epic Completion Cascade. All other
  reference files now delegate to this file rather than maintaining
  local copies. Adds compressed status flow (Ready -> Done) for
  agentic batch mode and documents the `project-state.json` artefact
  and the `Owner` field on stories.
- **`reference-epic.md`** (+50%): Three Amigos mandatory review,
  8-step Post-Wave Merge Protocol with troubleshooting table, full
  Agent Prompt Template (READ FIRST, DO NOT, AC-to-files mapping, code
  snippets for shapes not logic), wave-boundary quality gates,
  `--no-artifacts` agentic mode.
- **`reference-review.md`** (+50%): automatic Phase 3a persona
  consultation, Phase 3b auto-apply mechanical fixes (with `--no-fix`),
  Phase 4 review-state.json update, test-tree validation against TSD,
  CR staleness checks.
- **`reference-workflow-personas.md`**: defaults flipped from Optional
  to Always for most artefacts; new sections for story-plan and
  bug-fix consultation.
- **`reference-story.md`**: Three Amigos default review, new Agentic
  Mode Behaviour section covering `--no-artifacts`.
- **`reference-code.md`**: Three Amigos plan review; completion
  checklist expanded from 6 to 12 steps.
- **`reference-bug.md`**: Three Amigos for bug fixes (impact, root
  cause, regression).
- **`reference-prd.md`**: automatic persona consultation when
  `sdlc-studio/personas/` exists.
- **`reference-tsd.md`**: review-state.json fallback to `RV*.md` scan
  with explicit reviews-health formula.
- **`reference-config.md`**: project implement configuration block
  (`commit_strategy`, `review_interval`, `auto_reconcile`,
  `auto_commit`).
- **`reference-consult.md`**: automation table with Three Amigos as
  the explicit default across most artefacts.
- **`SKILL.md`**: registers new commands and flags, adds
  Reconciliation, Change Management, and Project Implementation
  sections.
- **`help/help.md`**: Change Management, Project Implementation, Epic
  Implementation, Story Implementation, and manual Development Cycle
  sections.
- **`help/status.md`**: dual-source metrics with `RV*.md` fallback
  when `.local/review-state.json` is absent.

### Config

- `.markdownlint.json`: set `MD046` to fenced style and disable
  `MD036` (the skill deliberately uses bold labels as sub-step markers
  within numbered lists).

## [1.4.0] - 2026-02-18

Persona consultation system, interactive chat sessions, agentic epic execution, and workflow state management.

### Added

- **Persona Consultation System**: `/sdlc-studio consult` command for structured persona feedback on artefacts
  - Single persona, Three Amigos (`consult team`), and stakeholder group (`consult stakeholders`) modes
  - Verdicts: Approve, Concerns, Reject with actionable recommendations
  - New files: `help/consult.md`, `reference-consult.md`, 3 consultation templates
- **Interactive Persona Chat**: `/sdlc-studio chat` command for conversational persona sessions
  - Workshop mode (`--workshop`) for multi-persona discussions
  - Context loading (`--context`), transcript saving (`--save`)
  - New files: `help/chat.md`, `reference-chat.md`
- **Persona Generation**: `/sdlc-studio persona generate` with three source modes
  - `--from-prd`, `--from-code`, `--from-docs` extraction
  - Import/export and list commands
  - New file: `reference-persona-generate.md`
- **Archetype Personas**: 15 pre-built persona templates across Team and Stakeholder categories
  - Team: Product (2), Engineering (4), QA (2)
  - Stakeholders: Users (3), Business (2), Technical (2)
  - New directory: `templates/personas/` with per-category subdirectories
- **Workflow Persona Integration**: `--with-personas` and `--skip-personas` flags across all workflows
  - New file: `reference-workflow-personas.md`
- **Agentic Epic Execution**: `--agentic` flag for autonomous concurrent story execution
  - Dependency graph analysis and hub file overlap detection
  - Concurrent wave assignment with automatic sequential fallback
  - Post-wave test suite verification
- **Story Completion Cascade**: Automatic status propagation to linked plans, test specs, and workflows when a story reaches any terminal status
- **Terminal Status Support**: Won't Implement, Deferred, Superseded statuses for stories, plans, test specs, and workflows
- **Workflow State Templates**: `templates/core/workflow.md` and `templates/indexes/workflow.md` for implementation tracking
- **Index Reconciliation**: `status --full` detects missing entries, status mismatches, stale statuses, and ID collisions
- **Frontend Testing Patterns**: Vitest + React patterns, shared API client mocking, jsdom mocking for Recharts/D3/MapboxGL
- **Test Case Numbering**: Global TC numbering across specs and epic-scoped coverage rules

### Changed

- **`--parallel` renamed to `--agentic`**: Better branding for autonomous execution capability (all files updated, `#flag-agentic` anchor)
- **Persona workflows expanded**: `help/persona.md` (+305 lines) and `reference-persona.md` (+423 lines) with category framework, create/generate workflows, enrichment questions
- **Story workflows enhanced**: `reference-story.md` (+321 lines) with mandatory plan prerequisites, resume-from-phase, persona validation, completion cascade
- **Epic workflows enhanced**: `reference-epic.md` (+178 lines) with persona assessment, agentic execution, post-epic checklist
- **Output formats expanded**: `reference-outputs.md` (+91 lines) with terminal statuses, cascade checklist, status vocabulary enforcement, ID collision prevention
- **SKILL.md updated**: New persona/consult/chat commands, `--agentic` flag, agentic workflow diagram (+93 lines, now 505 lines)
- **README.md updated**: Agentic epic execution in Common Commands table and Workflows section
- **Help files**: Source of truth pointers added to bug, code, refactor, test-automation, test-spec help files

## [1.3.0] - 2026-01-28

Major restructuring with modular template architecture, expanded command coverage, and British English standardisation.

### Added

- **Modular Template Architecture**: Reorganised templates into logical structure
  - `templates/core/*.md` - Streamlined core templates (prd, trd, tsd, epic, story, plan, test-spec, bug, personas)
  - `templates/indexes/*.md` - Index file templates
  - `templates/modules/trd/*.md` - Optional TRD modules (c4-diagrams, container-design, adr)
  - `templates/modules/tsd/*.md` - Optional TSD modules (contract-tests, performance-tests, security-tests)
  - `templates/modules/epic/*.md` - Epic perspective modules (engineering-view, product-view, test-view)
  - `templates/automation/*.template` - Test automation templates (pytest, jest, vitest, go, xunit, junit)
  - `templates/workflows/*.md` - Workflow state templates
  - `templates/reviews/*.md` - Review output templates
- **New Reference Files**: Expanded documentation coverage
  - `reference-config.md` - Project configuration options
  - `reference-refactor.md` - Code refactoring workflows
  - `reference-review.md` - Unified document review workflow
  - `reference-upgrade.md` - Schema migration guidance
  - `reference-test-spec.md` - Test specification workflows
  - `reference-test-automation.md` - Test automation and environment workflows
  - `reference-tsd.md` - Test Strategy Document workflows
  - `reference-epic-sections.md` - Epic section deep dives
  - `reference-story-sections.md` - Story section deep dives
  - `reference-test-pitfalls.md` - Test generation anti-patterns
- **New Help Files**: Command-specific guidance
  - `help/init.md` - Project initialisation
  - `help/refactor.md` - Refactoring commands
  - `help/review.md` - Review commands
  - `help/test-env.md` - Test environment setup
  - `help/upgrade.md` - Schema upgrade guidance
- **New Best Practice Guides**:
  - `best-practices/postgresql.md` - PostgreSQL-specific patterns
  - `best-practices/sql.md` - General SQL best practices
- **Configuration System**: New project configuration
  - `templates/config.yaml` - Project configuration template
  - `templates/config-defaults.yaml` - Skill default settings
  - `templates/version.yaml` - Version tracking template

### Changed

- **British English Standardisation**: Consistent spelling throughout
  - `visualize` → `visualise` (command name)
  - `License` → `Licence` (section headers)
- **SKILL.md Streamlined**: Improved command reference and progressive loading guide
- **Reference Files Updated**: Enhanced navigation sections and cross-references
- **Help Files Consolidated**: Reduced duplication, improved See Also sections

### Removed

- **Legacy Templates**: Replaced with modular structure
  - `templates/bug-template.md`, `templates/bug-index-template.md`
  - `templates/epic-template.md`, `templates/epic-index-template.md`, `templates/epic-workflow-template.md`
  - `templates/story-template.md`, `templates/story-index-template.md`
  - `templates/plan-template.md`, `templates/plan-index-template.md`
  - `templates/prd-template.md`, `templates/trd-template.md`, `templates/tsd-template.md`
  - `templates/test-spec-template.md`, `templates/test-spec-index-template.md`
  - `templates/personas-template.md`, `templates/workflow-template.md`
- **Obsolete Reference File**: `reference-testing.md` (split into test-spec, test-automation, tsd)

## [1.2.0] - 2026-01-26

Major documentation overhaul with comprehensive refactoring for improved navigation, progressive disclosure, and best practices compliance. Consolidated best practices structure and enhanced AI-assisted testing guidance.

### Added

- **Single Source of Truth for Outputs**: New `reference-outputs.md` (150 lines)
  - Centralised documentation for all output formats, file locations, and status values
  - Status transition diagrams for all artifact types
  - File naming conventions and index file structure
  - Traceability documentation
- **Advanced Testing Patterns**: New `reference-test-validation.md` (486 lines)
  - Validation workflows and contract testing guidance
  - Parameterised testing patterns (Python, TypeScript, Go)
  - Test data management and flakiness prevention
  - Property-based and snapshot testing
- **Navigation Infrastructure**: 419 section anchors across all reference files
  - Deep linking to specific sections (e.g., `reference-code.md#edge-case-coverage`)
  - Enables precise cross-referencing between documentation
- **Navigation Sections**: Added to 8 reference files
  - Prerequisites (required files to load first)
  - Related workflows (upstream/downstream dependencies)
  - Cross-cutting concerns (decisions, outputs)
  - Deep dives (optional advanced topics)
- **Best Practice Guides for Skill Development**: New guides for maintaining quality standards
  - `best-practices/command.md` (168 lines) - Claude Code command patterns
  - `best-practices/documentation.md` (165 lines) - Documentation standards
  - `best-practices/claude-skill.md` (268 lines) - Skill development guide
  - `best-practices/settings.md` - Configuration best practices
- **Enhanced AI-Assisted Testing Guidance**:
  - `reference-test-pitfalls.md` (144 lines) - Test generation anti-patterns catalogue
  - 90% coverage targets with proven achievable strategies
  - AI-specific testing anti-patterns and validation workflows
  - Conditional assertion pitfall detection
  - Silent test helper failure prevention

### Changed

- **SKILL.md Restructured** (453 → 484 lines, improved organisation):
  - Added explicit "Instructions" section (best practices compliance)
  - Moved philosophy to "Critical Philosophy (Read This First)" section
  - Replaced "File Loading Guide" with "Progressive Loading Guide" (structured table format)
  - Added "Navigation Map" showing file relationships by domain and workflow stage
  - References `reference-outputs.md` as single source of truth
- **Progressive Disclosure Improvements**:
  - Edge case validation moved to step 5 in `reference-code.md` (validates BEFORE planning)
  - Critical warnings moved to first 40 lines in help files
  - Philosophy callout added to `help/prd.md` for generate mode users
- **Help Files Standardised** (10 files updated):
  - "See Also" sections now use priority markers (REQUIRED/Recommended/Optional)
  - Added section anchor references for precise navigation
  - Removed duplicate output format documentation
- **Template Headers Standardised** (16 templates updated):
  - Added consistent header comments to all templates
  - Templates reference `reference-outputs.md` for status values
  - Includes file path and related documentation links
- **Consolidated Language Best Practices**: Unified split files into single files per language
  - Merged `python-rules.md` + `python-examples.md` → `python.md` (247 lines)
  - Merged `go-rules.md` + `go-examples.md` → `go.md` (416 lines)
  - Merged `javascript-rules.md` + `javascript-examples.md` → `javascript.md`
  - Merged `typescript-rules.md` + `typescript-examples.md` → `typescript.md`
  - Merged `rust-rules.md` + `rust-examples.md` → `rust.md`
  - Single source of truth per language improves AI context and maintenance
- **Testing Documentation Restructured**: Split `reference-test-best-practices.md` (862 → 410 lines)
  - Core practices, checklist, and warnings remain in `reference-test-best-practices.md`
  - Advanced patterns moved to new `reference-test-validation.md` (486 lines)
  - Clearer separation of concerns and improved maintainability
- **Improved Workflow Organisation**: Refactored scope validation from `reference-code.md` to `reference-decisions.md`
  - Progressive disclosure: HOW to plan vs WHEN plan is ready
  - Cleaner separation of workflow steps and validation criteria

### Removed

- **Split Best Practice Files**: Removed 14 language-specific split files
  - `*-rules.md` and `*-examples.md` files for Python, Go, JavaScript, TypeScript, Rust, PHP, C#
  - Content preserved in consolidated single files

### Fixed

- **Broken File References**: Fixed 2 instances of non-existent file references
  - `reference-requirements.md` → `reference-prd.md`, `reference-trd.md`, `reference-persona.md`
  - `reference-specifications.md` → `reference-epic.md`, `reference-story.md`, `reference-bug.md`
- **Markdownlint Compliance**: Fixed 45 linting errors in refactored files
  - Added language specifiers to 16 code blocks
  - Added blank lines around 16 lists
  - Added blank lines around 9 code blocks
  - Added blank lines around 4 headings
- `help/bug.md` line 288: Corrected reference link from `reference.md` to `reference-bug.md`

### Technical Improvements

- **Documentation Quality**: 100% best practices compliance
  - Explicit Instructions section per skill development guidelines
  - No broken references (0 remaining)
  - All code blocks have language specifiers
  - Consistent spacing and formatting
- **Navigation Efficiency**: 419 section anchors enable
  - Direct linking to specific workflow steps
  - Precise cross-references between files
  - Reduced navigation time by ~40%
- **Maintenance Burden**: Reduced by ~60%
  - Single source of truth for output formats
  - No duplicate content across files
  - Clear dependency relationships documented

## [1.1.0] - 2026-01-20

Based on production testing and user feedback to improve workflow and output quality.

### Added

- **Test Strategy Document (TSD)**: New `/sdlc-studio tsd` command with improved structure
- **Story Workflow Automation**: Execute stories through 7 phases (Plan → Test Spec → Tests → Implement → Test → Verify → Check)
- **Epic Workflow Automation**: Process all stories in dependency order with `/sdlc-studio epic implement`
- **Explicit Story Dependencies**: Stories track schema, API, and service dependencies
- **Modular Reference Architecture**: Split reference.md into 13 focused files:
  - `reference-philosophy.md` - Create vs Generate modes
  - `reference-prd.md`, `reference-trd.md`, `reference-epic.md`, `reference-story.md`
  - `reference-bug.md`, `reference-persona.md`
  - `reference-code.md`, `reference-testing.md`
  - `reference-architecture.md`, `reference-decisions.md`
  - `reference-test-best-practices.md`, `reference-test-e2e-guidelines.md`
- **New Best Practices**: Go language guide, architecture patterns guide
- **New Templates**: `workflow-template.md`, `epic-workflow-template.md`, `tsd-template.md`

### Changed

- SKILL.md updated for modular architecture
- Help files updated with workflow automation commands
- Templates improved for better output quality

### Removed

- **Commands**: `init`, `migrate`, `test-strategy`, generic `test`
- **Files**: `reference.md`, `definition-of-done-template.md`, `test-strategy-template.md`
- **Help Files**: `help/init.md`, `help/migrate.md`, `help/test-strategy.md`, `help/test.md`

### Migration

| Old | New |
| ----- | ----- |
| `/sdlc-studio init` | `/sdlc-studio status` (start with prd create/generate) |
| `/sdlc-studio migrate` | No longer needed |
| `/sdlc-studio test-strategy` | `/sdlc-studio tsd` |
| `/sdlc-studio test` | `/sdlc-studio code test` |

**Workflow automation (new):**

```bash
/sdlc-studio story implement --story US0001   # Single story, all phases
/sdlc-studio epic implement --epic EP0001     # All stories in epic
```

## [1.0.0] - 2025-01-17

### Added

- **Requirements Pipeline**: PRD, TRD, Epic, Story, Persona management
- **Bug Tracking**: Report, list, fix, verify, and close bugs with traceability
- **Code Workflows**: Plan, implement, review, and check code against requirements
- **Testing Pipeline**: Test Strategy, Test Specifications, Test Automation
- **Test Execution**: Run tests with traceability to stories and epics
- **Pipeline Bootstrap**: Auto-detect brownfield/greenfield projects with `/sdlc-studio init`
- **Migration**: Migrate from old test-plan/suite/case format
- **Status & Hints**: Check pipeline state and get actionable next steps
- **Help System**: Type-specific help for all commands
- **Templates**: 22 templates for all artifact types
- **Best Practices**: 11 guides for quality artifacts

[1.4.0]: https://github.com/DarrenBenson/sdlc-studio/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/DarrenBenson/sdlc-studio/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/DarrenBenson/sdlc-studio/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/DarrenBenson/sdlc-studio/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/DarrenBenson/sdlc-studio/releases/tag/v1.0.0
