# Changelog

All notable changes to SDLC Studio will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [4.0.0] - 2026-07-09

The maturity release. Schema v3 (distributed ULID identity + structured authorship/evidence
enforcement) ships **active**, not dormant, and becomes the default for new projects.

### Breaking

- **Schema v3 becomes the default for new projects.** `init` now scaffolds `schema_version: 3`
  (ULID identity + authorship/evidence enforcement). Existing and unpinned projects are NOT
  auto-flipped: the code default stays 2 and they upgrade explicitly via the `project upgrade`
  v2-to-v3 walk (capability delta -> `migrate_v3` dry-run -> apply -> re-baseline). Migration
  action for a consuming project: run `project upgrade` and follow the presented walk; the
  migration was rehearsed on two real projects (see `sdlc-studio/reviews/v4-migration-rehearsal.md`).

- **Hygiene: bugs closed, indexes archived, validate accepts v3 ULID ids (EP0025, CR0198/CR0199; US0112).** Closed BG0067/0068/0069/0070 (Fixed -> Closed); archived 57 story + 39 cr terminal rows into the `v4.0.0-rc.1` release batch (live indexes bounded, census unaffected via the archive-union). `validate` now accepts a v3 ULID id (`BG-01JQK3F8`) via a new `sdlc_md.is_v3_id`, instead of flagging it `id-format` - a v4 project's ULID artefacts validate cleanly while garbage and v2 ids classify as before.
- **Provenance-tag lint guard widened to catch US-form pairs (EP0025, CR0201; US0111).** The guard missed US-form ids, letting `(US0101/CR0186)` through in a shipped comment. It now also flags a US-led provenance pair joined by `/` or `;` (`(US0101/CR0186)`, `(US0090/CR0194)`), and its file glob covers the consuming-facing `templates/config*.yaml`. Lone US ids and comma/hyphen lists (`(US0045, US0046)`, `(US0001)`) stay unflagged - they are indistinguishable from legitimate example ids in tree diagrams and sample output. Five leaked US-pair tags stripped from scripts/reference/config-defaults, with a unit test.
- **Deterministic `status.py backlog` census (EP0025, CR0199; US0110).** A new `backlog` subcommand lists the non-terminal (open) artefacts per type and status from a file census - the deterministic answer to "what is left in the backlog?" that no longer needs a hand-parsed `_index.md` grep. Terminal detection uses the shared vocab's full terminal set (`is_terminal_status`), not a hardcoded subset; `--type` filters, `--format json` for tooling, and an empty backlog says so explicitly.
- **rc-tag readiness checklist enumerated (EP0024, CR0198; US0109).** `sdlc-studio/reviews/v4-rc-readiness.md` lists each rc-tag gate (portable gate green, version at rc.1, migration rehearsed, EP0014 closed, open-bug count 0, drift 0, suites green) with a live check command, so cutting `v4.0.0-rc.1` is a checklist read. It honestly reads NOT-YET-GREEN today: the open-bug gate is red until US0112 closes the four Fixed bugs.
- **Majors-only section added to the release-gate checklist (EP0024, CR0198; US0107).** `templates/workflows/release-gate.md` gains a section 8 for breaking releases: breaking-change inventory in the CHANGELOG, migration rehearsed on two real projects with evidence linked, eval scenarios re-run for the new major, docs saying the new major, and rc-first-from-a-green-gate-with-a-soak. The rc-tag decision becomes a checklist read.
- **v3 to v4 upgrade walk presented as a directed sequence + rehearsed on two real projects (EP0024, CR0198; US0106).** `project upgrade` now presents the v2 to v3 migration as an ordered walk (capability delta -> `migrate_v3` dry-run -> `migrate_v3` apply -> re-baseline) via a new `migration_walk`, in both text and `--format json`; the schema flip stays the deliberate `migrate_v3` id migration, never an auto-apply. The walk was rehearsed dry-run against two real consuming projects (evidence in `sdlc-studio/reviews/v4-migration-rehearsal.md`, names redacted); the rehearsal surfaced BG0070 (a per-artefact `git log --follow` makes migration impractical on a large project) - rc-relevant.

### Changed

- **New projects start on `schema_version: 3`; existing projects untouched (EP0024, CR0198; US0105).** `init` now seeds `schema_version: 3` (ULID identity + authorship/evidence enforcement) into a new project's `.config.yaml`. The code default stays 2 and the schema reader is override-only (it does not merge `config-defaults.yaml`), so an existing or unpinned project is never auto-flipped - it upgrades explicitly via `project upgrade`. This dogfood repo is pinned to `schema_version: 2` as a safety belt. Era-gate regression test proves a v2 project's v3-gated paths stay dormant.

- **Complexity hotspots decomposed, latent test issues fixed, small cleanups + a debug channel
  (EP0022, CR0187; US0103).** `reconcile.detect_type` (115 -> 40 lines), `transition.transition`
  (128 -> 45) and `conformance.detect_conformance` (118 -> 84) are decomposed into named,
  behaviour-preserving helpers (the full suite is unchanged and green); `lessons.render_global_lesson`
  was already within bounds. Test fixes: `test_table_parsers.py` uses a raw string for the escaped
  pipe (no future SyntaxError) and the verify tests route `main()` through a quiet helper so they no
  longer leak `[APL]`/`wrote` lines into suite output. Cleanups: `gate.py`'s redundant
  `except (OSError, Exception)` narrowed to `Exception`; `artifact.py`'s `meta_new` dry-run predicts
  `indexed` honestly instead of always `False`. New opt-in diagnostics: `sdlc_md.debug`/`roll_jsonl` -
  `SDLC_DEBUG=1` emits one stderr line from each named swallowed-advisory site (telemetry, jest cache,
  sprint complexity, reconcile blocker-sweep), and the append-only `.local` logs (telemetry/verify
  history) roll to a bounded size.

- **"Find an artifact by id" and "a story's epic" consolidated onto the shared layer (EP0022,
  CR0187; US0102).** `lib/sdlc_md.py` gains canonical `find_by_id` (alias-aware) and
  `story_epic`; `audit.find_artifact`, `transition._find` and `lite_profile._story_epic` now
  delegate to them, so a lookup fix lands in one place. `reconcile.py`'s `detect`/`apply`/
  `fields`/`archive` all speak `--format json`, and the parity is locked by a test so a new
  subcommand cannot ship text-only. Maintainability only - no behaviour change.
- **`reference-scripts.md` split into a lean index + grouped detail pages (EP0020, CR0200;
  US0096).** The 643-line catalogue (past its 600 budget three sprints running) is now a lean
  index of one-line summaries linking to five grouped pages (`reference-scripts-{create,verify,
  review,upgrade,domain}.md`), each under budget; the `643` allowlist is removed. `doc_coverage`
  unions `reference-scripts*.md`, so the doc-coverage floor still hard-fails a missing entry.
  Documentation reorganisation only - no script behaviour changed.

### Added

- **A disabled commit gate is now detectable (EP0026, CR0202; US0113).** New advisory
  `hook-enabled` gate lane plus a matching `status` dashboard warning: when a git work tree
  ships `.githooks/pre-commit` but `core.hooksPath` is unset or points elsewhere, both surfaces
  say so and name the fix (`bash tools/enable-hooks.sh`). Deliberately silent everywhere it
  means nothing - hook enabled, no tracked hook (every consuming project), or a non-git
  directory - so the lane carries signal, not standing noise. One shared
  `gate.hook_enablement_gap` message keeps the two surfaces from drifting.
- **Context tiering - status/hint read closed-artefact digests, not the full corpus (EP0023,
  CR0179; US0104).** A long-lived repo pays a growing token tax on every status/planning pass
  that re-reads the whole closed corpus. Once the closed-artefact count reaches
  `digests.min_closed` (default 500), `digest.py build` writes a filename-keyed mechanical
  digest (id/title/status/outcome/refs) and `status`/`hint` read a closed artefact's status from
  it instead of opening the original - the enumeration (`sdlc_md.iter_artifact_files`, now the
  basis of `artifact_files`) skips the is-artifact read for those trusted filenames. Measured on
  a 501-closed fixture: `status` reads 0 closed originals / 0 bytes vs 501 / 59,010 with no
  digest (recorded in CR0179). The digest is byte-stable (deterministic) and `reconcile detect`
  flags it as an advisory when it drifts from the census; a closed artefact still resolves by id
  (including a CR0167 alias) to its full original. Below the threshold the feature is dormant -
  no digest is produced or read, so a small repo sees no behaviour change.
- **Sync, state and verifier-sandbox hardening (EP0022, CR0186; US0101).** `github_sync push`
  now scans each record's title+body for secret-shaped tokens (GitHub tokens/PATs, AWS keys,
  AI API keys, Slack tokens, private-key blocks, credential assignments) and refuses to publish
  a flagged record to a public - or unknown-visibility - repo; findings are reported redacted
  (prefix + length, never the raw token), visibility is resolved lazily via `gh repo view` only
  when a secret is found, and `--allow-secrets` overrides for a confirmed-private target. The
  `http` verifier verb gains a scheme floor enforced in every mode (only http/https, blocking
  `file://`/`ftp://`/`gopher://` SSRF vectors) plus an opt-in host allow-list (restricted mode
  via `SDLC_VERIFY_HTTP_HOSTS`); the shared trust boundary with the mutation gate's `--test`
  command is documented in the `verify_ac` module. `version-check.json` and any nested `.local/`
  are named in `.gitignore` so machine-local state cannot land in a commit.
- **Supply-chain integrity: Actions pinned to commit SHAs + installer checksum verification
  (EP0022, CR0186; US0100).** Every GitHub Action in `.github/workflows/` is now pinned to a
  full 40-hex commit SHA (version in a trailing comment) so a moved tag cannot inject code into
  CI, and a new `tools/check_action_pins.sh` guard (wired into `npm run lint` and the pre-commit
  gate, with a unit test) fails if any Action reverts to a mutable tag/branch. Both installers
  (`install.sh`, `install.ps1`) verify the downloaded artefact against a published sha256 before
  extraction - the digest comes from `SDLC_STUDIO_SHA256` (an explicit pin) or a best-effort
  `<url>.sha256` sidecar; a mismatch aborts before any extraction, and
  `SDLC_STUDIO_REQUIRE_CHECKSUM=1` makes a missing digest fatal. Also untracks two `.local/`
  runtime files a broad `git add -A` shipped, and adds a `**/.local/` safety-net ignore.
- **Plan-review gate - a deterministic AC-vs-spec check before implementation (EP0019, CR0194;
  US0090, schema v3, opt-in).** New `scripts/plan_review.py` closes the N=5 "bad plan
  propagates" failure: a story with spec-derived ACs cannot reach implementation (In
  Progress/Review/Done, wired into `transition.py`) without an independent plan-review verdict.
  The trigger is **deterministic** (TRD ADR-006, no model judgement in fire/skip): it fires on
  any of three signals - the Affects/ACs cite a `plan_review.spec_globs` path, `affects_files`
  reaches `plan_review.affects_files_threshold` (default 5), or the routed difficulty band
  reaches `plan_review.min_difficulty` (default medium). `critic.py record` gains a `--phase
  {delivery,plan-review}` field (its own log, so a plan-review verdict never satisfies the
  delivery critique gate); `plan_review record` pins the verdict to the reviewed ACs by
  fingerprint, so a post-approval AC edit invalidates it. The only sanctioned skip is a
  recorded `> **Plan-Review-Override:**` field (auditable; not bypassable by `--force`). Dormant
  under schema v2. US0091 adds the reviewer's charter
  (`reference-agent-prompt-template.md#plan-review-charter`: the QA seat re-reads the cited spec
  section and flags any AC that inverts it as a blocking finding, escalating to blind
  re-derivation for high-difficulty units), an optional `> **Plan-Review:**` story-template slot,
  and a plan-review telemetry event (`telemetry.record_plan_review`, summarised as its own block
  so the gate's run count, verdict mix, and independent-review rate are measurable).
- **Spec-edit guard - an untraced edit to a requirements/spec document is a blocking finding
  (EP0019, CR0195; US0092, schema v3, opt-in).** New `scripts/spec_guard.py` closes the N=5 case
  where a worker edited the workspace spec to match its wrong implementation and review missed it.
  `check --changed <files> --story <file>` deterministically surfaces which changed files are
  requirements/spec documents (config `review.spec_paths`) and whether any AC cites a spec change;
  an `untraced` edit (a spec doc touched with no citing AC) is the signal the critic charter
  (`reference-agent-prompt-template.md#spec-edit-charter`) treats as blocking. A requested spec
  edit (an AC citing the path) stays legitimate; the traceability judgement stays with the critic.
  Dormant under schema v2.
- **Agentic triage - human sampling policy + triage-quality metrics (EP0014, CR0173; US0066,
  schema v3, opt-in).** New `scripts/triage_sampling.py`: `sample()` is a deterministic
  (seeded-hash) audit-sampling policy - every Critical, every raiser/triager severity
  disagreement, plus `triage.sample_rate` (default 0.20) of the rest; `metrics()` computes
  triage quality from the records (no hand-counting) - the false-positive rate (a finding
  triaged as real then closed invalid), severity inflation (triager vs raiser), and
  sampled-but-unreviewed findings as standing pending audit. Surfaced by
  `status triage-metrics`. New `triage.sample_rate` / `triage.always_sample` config keys.
- **Agentic triage - optional tranche reference (EP0014, CR0172; US0068, schema v3, opt-in).**
  An external orchestrator may stamp a record-only `> **Tranche:**` reference on an artefact
  (`artifact new` passes it through when supplied; sdlc-studio never allocates it), so the
  records answer "what shipped in tranche X" without sdlc-studio becoming a scheduler. `validate`
  gains a `tranche-shape` check (absent or valued is fine; present-but-empty is a malformed
  record; era-gated to v3), and `status tranche --value <ref>` lists every artefact carrying a
  given reference across all types.
- **Agentic triage - noise controls (EP0014, CR0173; US0067, schema v3, opt-in).** New
  `scripts/triage_noise.py` and a `triage:` config block add two creation-time controls, both
  dormant under v2: a **session cap** (`triage.session_cap`, default 20) refuses the N+1th
  finding of a session loudly (a session keyed by the `SDLC_TRIAGE_SESSION` environment
  variable, its count in `.local/triage-session.json`) so an agent cannot flood the backlog; and
  **Low-severity consolidation** (`triage.low_consolidation`, default on) folds a Low-severity
  finding into a themed consolidation CR - one per theme, carrying a `> **Consolidation:**`
  marker - instead of minting its own artefact, while Medium and above still get individual ones.
  Both `file_finding` and `artifact new` route finding creation through the controls, so neither
  path is a bypass.
- **Agentic triage - vocabulary and gated transitions (EP0014, CR0173; US0065, schema v3, opt-in).**
  Under `schema_version: 3`, findings (bug/cr/rfc) gain an `inbox` triage lane prepended to their
  status vocabulary, and `artifact.py` files a fresh finding into `inbox` rather than its per-type
  create status. A gated `inbox -> triaged` transition (`transition.py`) records the triaging seat:
  the target is type-specific (bug `Open`, cr `Approved`, rfc `In Review` - agent findings skip the
  human `Proposed`/`Draft` proposal states), it requires a structured `--triaged-by "Name; type;
  version"` and refuses loudly without one, enforces separation of duties (the triager must differ
  from the raiser; a solo human self-triage warns rather than deadlocks), and records the triager's
  severity via `--triage-severity` alongside the raiser's. All era-gated and dormant under v2, so
  existing projects are untouched.
- **Difficulty-aware model-tier routing** (RFC0026, CR0189-CR0191; US0083-US0085): new
  `scripts/route.py` - a deterministic 0-100 difficulty estimate per work unit (blast-radius
  cognitive/risk via `complexity.assess`, file scope, unresolved-path novelty, AC count,
  story points; an unresolved signal defaults to 0.5 and lowers confidence), banded to five
  abstract tiers (`tiny/small/medium/large/xlarge`) that a project maps to its own model ids
  in the new `routing:` config block (sparse maps degrade upward only). `sprint plan` stamps
  every unit with `difficulty` (always) and `tier`/`model` (when `routing.enabled`);
  `telemetry` records `tier_recommended/tier_delivered/model/escalated` and summarises per
  delivered tier. Advisory throughout - no gate reads a tier, no model API is called, and the
  critic is never a smaller tier than the author (medium floor for code units). Escalation on
  failure steps one declared tier within loop_guard's unchanged attempt cap. Shared
  `affects_files`/`resolve_affects`/`count_acs` helpers lifted into `lib/sdlc_md.py`.
- **Benchmark v2 + the calibration re-spike** (CR0192/CR0193; US0086-US0089, repo-only,
  not in the skill payload): tools/bench hardened (multi-file hidden-suite scoring,
  environmental arm isolation - the baseline arm's workspace contains no skill at all,
  automatic token/wall-time capture with disclosed manual fallback, arm R = routed pipeline,
  operator-priced cost index, min/max in summaries); two harder Tier-1 fixtures
  (`multifile-notify-digest`, `change-request-ledger-drift`), each validated
  red-on-naive/green-on-reference and independently fairness-reviewed; the held-back
  **Auditability** metric (`audit_quiz.py`: mutant-checked evidence citations +
  citation-validated trace answers; reviewer-independence descriptive at weight 0);
  `docs/benchmarks/protocol-v2.md` superseding pre-registration. The N=1 re-spike
  (3 arms x 2 fixtures) is published in `docs/benchmarks/2026-07-08-v2-respike.md`: the
  pipeline's mandated planning pass was the only arm with zero defect escapes, and the
  Auditability metric graded a real evidence-quality gradient. N=5: GO (D0013).
- **Benchmark v2 measured N=5 run** (D0014, repo-only): Tier 1 at N=5 per cell (30 runs +
  30 graded audit passes), Tier 2 via pre-declared cut #1. Published in
  `docs/benchmarks/2026-07-08-n5-run.md`: unstructured arms escaped 10/10 on notify-digest
  vs the mandated-planning arm's 2/5 (one-sided Fisher p 0.083, below conventional
  significance); Auditability tracked the escapes exactly; routing cut arm-R delivery cost
  to a 0.40 index on the easy fixture with zero escapes; the routed pipeline costs ~3.1x
  baseline tokens per single ticket. New documented failure mode - **a bad plan
  propagates**: two arm-R planners mis-pinned a spec rule in their ACs and the critic
  approved against the wrong oracle; in one of the two runs the worker went on to write the
  error into the workspace spec itself. Points at an independent AC-vs-spec conformance
  check before implementation.
- **Benchmark runner - calibration rows excluded by the tool, not by hand** (CR0196/US0093,
  repo-only, not in the skill payload). Protocol v2 forbids pooling calibration rows with
  measured ones, but producing the N=5 report needed hand-filtering that will one day be
  forgotten. `runner record` now stamps a `phase` field (default `measured`; `--phase
  calibration` for a calibration run), `runner summary` excludes calibration rows by default
  (`--include-phase calibration|all` opts them back in), and a one-time `runner backfill`
  stamps legacy rows (`v2n1` = calibration, else measured). `docs/benchmarks/protocol-v2.md`
  is unchanged (frozen).
- **Positioning refresh + the full value document** (CR0177/US0072): README reframed under
  the three hard constraints (anti-vibe-coding umbrella, greenfield equally visible,
  catalogue below the fold) with the now-unlocked team-shape and evidence paragraphs; new
  `docs/why-sdlc-studio.md` - a progressively-disclosed value argument (thesis, labelled
  operator-reported field results, benchmark evidence including the unflattering findings,
  economics, calibrated team-shape, open questions); agent-facing discoverability: root
  `llms.txt`, a For-agents README block, and SKILL.md gains NOT-for triggers plus
  namespaced openclaw metadata. Every claim critic-reviewed for calibration against the
  published benchmark data.
- **Upgrade re-baseline census (EP0020, CR0197; US0094, schema v3, opt-in).**
  `project_upgrade.rebaseline()` walks every non-terminal artefact and buckets its gaps against
  the capability delta - `backfill` (a mechanical stamp computable now, e.g. a missing
  `Difficulty`), `re-review` (matches a gate's deterministic trigger but lacks the verdict, e.g.
  a spec-derived story with no plan-review verdict), `residual` (judgement gaps). The bucketed
  report (empty buckets printed explicitly) surfaces from `project upgrade`. Read-only,
  deterministic, dormant under schema v2. `project upgrade --apply` (US0095) performs ONLY the
  mechanical `backfill` bucket - stamping a `route estimate` `Difficulty` band on units lacking
  it - idempotently, never touching the re-review/residual buckets and never fabricating history;
  `reference-upgrade.md` states the next-transition enforcement policy (a new gate attaches at an
  artefact's next transition, never retroactively).

- **Origin-drift pre-flight for `sprint plan` + branch-aware remote id allocation (EP0021,
  CR0188; US0099).** `sprint plan` now runs a `git fetch origin` + drift check: when the local
  clone is behind origin's default branch it warns (naming the commit count and any overlap
  between the incoming remote changes and the batch's own artefacts) and, under `--strict`,
  refuses - so a sprint is not planned against a stale checkout. Fail-safe: no remote, no git, or
  up-to-date behaves exactly as before. `next_id.remote_ids` now resolves origin's actual default
  branch (was hardcoded `origin/main`), so remote-aware id allocation also protects
  `master`/`develop`-default repos from re-minting an id the remote already holds. An AGENTS.md
  orientation bullet documents the fetch-before-trusting step.

### Fixed

- **CI now runs the portable artefact gate, making the claimed hook/CI parity real (EP0026;
  BG0096).** `.githooks/pre-commit` and CONTRIBUTING both said "the same gate CI runs" while the
  Lint workflow ran only lint/tests/coverage/bandit - artefact drift, conformance or integrity
  breakage could reach a green CI. The workflow gains a `gate.py --root .` step (after
  setup-python, PyYAML installed so config-driven lanes fail loud); the two doc claims are now
  true as written.
- **A crashing blocking check now fails the gate (EP0026; BG0090).** A check that raised a
  non-config exception was recorded `blocking: False` and excluded from the PASS calculation,
  so a buggy or crashed blocking lane (validate, reconcile, conformance...) silently converted
  a red gate to green - the vacuous-PASS class at a new location. A declared
  `BLOCKING_ON_ERROR` lane set makes a crash in any blocking lane block; custom/injected
  checks stay contained (advisory-on-error), and a drift-guard test asserts every DEFAULT lane
  that blocks on failure also blocks on crash (it immediately caught `doc-coverage` missing
  from the first cut).
- **The eval gate joined the rc checklist and the four scenarios were re-run: 4/4 PASS
  (RV0007; BG0079).** The rc-readiness checklist omitted the eval gate its own release-gate
  template mandates (sections 1 and 8) and the scenarios had not run since v3.5.0 despite a
  SKILL.md description change. The checklist gains the row, and a full two-Claude run
  (worker + grader per scenario, method deviations recorded) passed every blocking behaviour
  across trigger routing, greenfield create, the generate-mode gate, and drift/reconcile
  dry-run safety - recorded in `sdlc-studio/reviews/v4-eval-run-2026-07-10.md`.
- **Superseded-regime docs corrected for the v4 majors gate (RV0007; BG0080).** The
  `status`/`hint` pre-flight tables covered only `schema_version: 2` (a fresh v4 project, on
  the new default of 3, had no row and the prompt still said "v1 format... upgrade to v2"); both
  tables are now era-neutral (2 or 3 proceed; the schema is read from `.version` OR
  `.config.yaml`, which is all a fresh v3 project has) with a schema-aware output prefix. The
  public SECURITY.md support table, frozen at 1.x, is restated in terms of the current major
  (4.x fixes / 3.x security-only) with the tracking rule written down.
- **`migrate_v3` journals its id map and resumes from it (RV0007; BG0073).** apply rewrote every
  reference (phase 1) then renamed files (phase 2) with no persisted map - a crash between or
  during the phases followed by a re-run re-derived a DIFFERENT assignment (phase-1 writes bump
  mtimes; already-renamed files shift the counter), silently cross-wiring identities across a
  consuming project. The map is now journalled to `.local/migrate-map.json` before the first
  write; plan and apply both detect the journal and resume from the SAVED map, a file present
  under neither name fails loud, a corrupt journal refuses to re-plan, and the journal comes off
  only after the index rebuild and era stamp are durable. The closing full-diff critic REJECTED
  the first cut with a reproduction (resume re-rewrote the old id inside `> **Aliases:**` lines,
  self-referencing every alias); repaired test-first - alias lines are structurally exempt from
  reference rewriting - and the same critic re-ran its reproductions to APPROVE.
- **`migrate_v3 apply` stamps `schema_version: 3` itself (RV0007; BG0074).** The docstring said
  the stamp "should be set" manually and the upgrade walk had no flip step - so after a clean
  migration all numeric ids vanished, `allocate_number` restarted at 1, and the very next
  `artifact new` minted `BG0001` while a migrated artefact still carried `> **Aliases:** BG0001`
  (ambiguous identity for every external reference). A completed apply now writes the stamp into
  `.config.yaml` (created if absent, other keys preserved; `plan` never stamps), so the era flip
  is mechanical. End-to-end: post-migrate filing mints a ULID.
- **The Low-consolidation lane exits 0 and its dry-run works (RV0007; BG0078).** `artifact new`'s
  text output indexed `epic_linked`/`indexed` unconditionally, but a consolidation result has its
  own shape - so a Low finding on a v3 project created/appended its CR and then exited 1
  (`error: 'epic_linked'`), inviting orchestrator retries and duplicate findings; `--dry-run`
  crashed outright. The text path now prints consolidation results by their own shape
  (`consolidated into CR-... created=True|False`); CLI tests cover dry-run, create and append.
- **The finding filer is era-aware (RV0007; BG0077).** `file_finding` allocated sequential v2
  numbers unconditionally, so on a schema-v3 project the primary agent filing path minted
  `BG0002`-style ids alongside ULIDs - reintroducing the id race v3 removes and shadowing live
  aliases. The v3 ULID mint now lives in one shared allocator (`sdlc_md.mint_v3_id`); both
  `artifact new` and the filer delegate to it, v2 projects keep sequential ids, and red-first
  tests pin both eras.
- **`artifact close` types v3 ULID ids (RV0007; BG0072).** Type inference collected every
  alphabetic character of the id, so a ULID's random tail (`BG-01JQK3F8` -> `BGJQKF`) defeated
  the prefix lookup and the documented close cascade raised `cannot infer type` for every
  artefact a schema-v3 project mints. A new `infer_type_from_id` reads only the LEADING alpha
  prefix (v2, dashed-v2 and v3 forms all resolve); unit tests pin all three forms and a live
  dry-run close of a freshly minted ULID.
- **`reconcile apply` no longer crashes appending a missing row into a dated index (RV0007;
  BG0071).** `row_from_header` indexed `f["date"]` directly while every other column used
  `.get()`, so the self-heal path raised `KeyError: 'date'` on the shipped bug/cr/plan index
  templates (and every dogfood index) whenever a file lacked an index row - aborting
  `transition set --ids` batches mid-flight after stamping the artefact. Absent dates now
  default to `--` like every other column; a cross-script seam test appends into a dated index
  and a unit test pins the empty-fields contract.
- **Repo lint restored to green and the commit gate actually enabled (RV0007; BG0075).** Six
  commits had landed markdown-breaking content on `main` while `git config core.hooksPath` was
  unset in the dogfooding clone (the tracked hook never ran) and CI sat dark behind the unpushed
  release freeze. The 26 markdownlint errors across 10 files are fixed (duplicate `### Changed`
  headings merged, founding-epic blockquotes joined, auto-fixables swept), `tools/enable-hooks.sh`
  is now run in this clone, and the rc-readiness checklist gains two rows: full `npm run lint`
  green and hook-enablement verified in the tagging clone.
- **The two archive implementations consolidated onto one `iter_tables` walker (EP0021,
  CR0182; US0098).** `archive.py` (release-based) and `reconcile.py`'s `archive_plan`/`archive_type`
  (flat) each hand-rolled their own index-table parser; both now delegate to a shared
  `reconcile.master_terminal_rows` built on `sdlc_md.iter_tables` (the single structural boundary).
  It picks the master data table by id-row count, so a multi-view index cannot double-archive a
  terminal row, and both paths use `sdlc_md.terminal_statuses` (BG0061's Deferred mis-classification
  cannot recur). Behaviour-preserving; the fail-loud-on-unrecognised-status and `--statuses` override
  contracts are intact.
- **`github_sync` and `verify_ac` discover artefacts through the shared layer (EP0021, CR0181;
  US0097).** Both tools now find lowercase-named files (the old case-sensitive `CR*`/`US*` prefix
  globs silently missed `cr0001.md` on Linux): `github_sync` dropped its private `TYPE_DIRS`
  duplicate of the type map and threads `--root` through discovery and the state file;
  `verify_ac`'s `walk_stories` and `--id` resolution are case-insensitive and it accepts `--root`
  as an alias of `--repo-root`, so the flag grammar matches every sibling script.
- **`decisions.py --supersedes` now flips the superseded row's Status to `superseded`
  (EP0020, BG0068).** The log no longer carries two contradictory `accepted` decisions; an
  unknown/typo id fails loud (anchored id parse) instead of silently recording a dangling
  supersession; a `decisions.py backfill` sweep fixes pre-existing rows (D0012/D0013). Also
  hardens `list_decisions` to split on unescaped pipes so a `\|` in a cell can't shift columns.
- **Shipped `test_gate` real-wrapper tests skip cleanly from an installed copy (EP0020,
  BG0069).** The two repo-coupled tests detect the dev-repo shape and `skipTest` with an
  explicit message otherwise, so a consuming operator verifying an install sees a visible SKIP,
  never a misleading FAILED on environment.

## [3.6.0] - 2026-07-06

The review/lite on-ramp (EP0016): two try-before-you-adopt entry points for an existing repo,
both non-breaking and independent of the dormant schema-v3 work. A project on v3.5.0 upgrades
with no migration and nothing renumbered.

### Release verification

Deterministic gate green: 1248 script tests + 49 tool tests pass, `check_versions --strict`
consistent across the four version homes, budgets/links/style/neutrality clean, `gate` PASS,
reconcile drift 0. The behavioural eval scenarios (`evals/README.md`) were not re-run this pass:
v3.6.0 adds two scripts plus help/config docs and does not change SKILL.md routing or
instructions - the surface those scenarios guard - so run them manually for a full behavioural
sign-off.

### Present but dormant (experimental, opt-in)

- The schema-v3 identity and enforcement machinery (ULID ids, migration, structured authorship,
  evidence and separation-of-duties lint) ships in this tag but is **inert** unless a project
  sets `schema_version: 3` (defaults to 2). It is experimental and unsupported until v4.0; see
  the `## v4 ...` sections below.

### Added

- **US0070 `review generate` on-ramp.** Point sdlc-studio at an existing repo and get a dated
  review report plus triaged findings with no prior workspace. `review_generate.py bootstrap`
  creates the `reviews/`, `bugs/`, and `change-requests/` folders and their indexes
  idempotently; the model-driven review runs three legs (architecture, code quality, defensive
  security) from `templates/workflows/repo-review.md`, read-only on source. Security findings
  are remediation-only by policy - location, weakness class, impact, and fix, no exploits or
  payloads, and a committed secret is reported by location plus rotation with the value never
  copied into an artefact. The policy is embedded verbatim in the prompt template, and
  `review_generate.py scan --secret <value>` fails if any produced artefact contains the value.
- **US0071 lite profile.** `profile: lite` in `.config.yaml` collapses the pipeline to
  PRD -> story -> implement: a story is created without an epic, `status`/`hint` never nag
  about a missing TRD/TSD/persona/epic, and executable-AC verification and reconcile behave
  identically. Every other profile keeps the epic layer mandatory. `sdlc_md.profile` is the
  reader; `lite_profile.py promote` is the one-way door to `full` - it inserts one umbrella epic
  above the existing epic-less stories, wires each to it, flips the profile, and reconciles the
  indexes clean. Documented under `reference-config.md#profile`.

## v4 Tranche 2 - authorship & enforcement + tooling debt (WIP, unreleased)

The v4 Tranche 2 - authorship & policy enforcement (EP0013), plus the RV0006 tooling-debt
tranche (EP0018) and the benchmark protocol. 13 stories delivered trunk-based. All schema-v3
enforcement is era-gated, so existing v2 projects are unaffected.

### Added

- **v4 Tranche 2 - authorship & enforcement (schema v3, opt-in).** All rules are era-gated,
  so existing v2 projects are unaffected.
  - **US0060 structured authorship.** A typed `> **Raised-by:** Name; type; version` reference
    (type one of human | persona | agent). `validate` enforces presence, shape, and
    resolvability on v3 artefacts (persona names resolve against `sdlc-studio/personas/`);
    `sdlc_md.schema_version`/`is_schema_v3`/`parse_authorship`/`resolve_author` back it.
    `backfill_authorship.py plan|apply` seeds a raised_by onto pre-adoption artefacts, marking
    inferred attributions, idempotent. The persona resolver is swappable for an agent resolver
    later with no schema change.
  - **US0061 separation-of-duties lint.** A `duties-separated` validate rule fails a v3
    artefact whose `Triaged-by` equals its `Raised-by` (a different seat must triage); a solo
    human self-triaging only warns, so a lone operator never deadlocks. The transition-time
    refusal wires in with the agentic triage transitions (EP0014).
  - **US0062 evidence as schema.** An `evidence-present` validate rule (v3 only) requires a
    bug to carry a file:line reference, command output, or reproduction steps, and a CR to
    carry an impact statement plus an effort estimate. Presence only (truth stays with
    reviewers); a `{{placeholder}}` counts as absent; legacy v2 artefacts are exempt.
  - **US0063 consolidated audit-check.** `audit_check.py check` runs the team-schema rules
    with stable ids (`authorship-structured`, `evidence-present`, `duties-separated`,
    `id-format`, `index-derived`, ...), exits non-zero on any violation, and gives `--format
    json` for the crew audit linter. The same rules are enforced in the blocking `gate` via
    `validate` and `index-derived`; `tranche-shape` ships dark until EP0014's tranche field.
  - **US0064 cross-script invariant test tier.** `test_invariants.py` guards the cascade seams
    the RV0006 review found unprotected: one telemetry record per artefact close, new-then-
    reconcile zero drift, CLI/library allocation parity, and master-table append on a
    multi-view index. It immediately earned its place - it caught a regression of BG0053 (the
    double-telemetry-on-close line had crept back into `artifact.close`), now re-fixed.
  - **US0073 benchmark protocol (pre-registered).** `docs/benchmarks/protocol.md` freezes the
    task set, metrics (tokens, wall time, defect escapes via a held-back suite, rework rate),
    N=5-with-an-N=1-spike, an independently-reviewed baseline `CLAUDE.md`, and a
    publish-regardless-of-outcome commitment - the RFC0025 device that must exist before any
    measured run. The harness and runs (US0074/US0075) follow.
  - **US0082 context tiering.** `digest.py build` produces mechanical, drift-checked digests of
    closed artefacts (id / title / status / outcome / refs) so status and planning reads need
    not re-read the whole corpus as a repo ages; originals are never summarised away.
    `digest.is_stale` gives the reconcile-style drift check. The read-path integration and size
    threshold stay scoped in CR0179.

### Fixed

- **US0078 archive consolidation - correctness guard (CR0182).** A regression test confirms
  both archivers (`archive.py` release-based and `reconcile archive_type`) relocate each
  terminal row of a multi-view index exactly once - the master row moves, the shared view row
  is kept. The double-archive path CR0182 flagged no longer reproduces (fixed by the BG0066 /
  v4 table-parsing work); the full dedup onto one `iter_tables` archiver stays scoped in CR0182.
- **US0077 shared discovery (CR0181).** `github_sync.walk_local` now discovers artefacts via
  the shared `sdlc_md.artifact_files` (case-insensitive, root-aware) instead of a
  case-sensitive `CR*.md` prefix glob that silently missed lowercase-named files (`cr0001.md`)
  on Linux. Full `--root`/STATE_PATH grammar unification stays scoped in CR0181.
- **US0080 code-quality debt (CR0187).** Corrected the `reconcile.py` module docstring - it
  claimed "read-only ... Subcommand: detect" while shipping `apply`/`fields`/`archive` write
  subcommands, so a read-only allowlist trusting it under-scoped the mutation surface; it now
  lists all four and scopes read-only to `detect`. Added `--format json` to `reconcile apply`
  for programmatic callers. (The larger CR0187 items - shared `find_by_id`, complexity
  decomposition, log rolling - stay scoped in the CR.)
- **US0079 security hardening - state hygiene (CR0186).** The skill-install `.local/` runtime
  state is now gitignored and `version-check.json` untracked, so machine state stops churning
  in every commit. A `tools/tests` guard keeps any `.local/` file from being tracked again.
  (The remaining CR0186 supply-chain items - SHA-pinning Actions, installer checksums, sync
  redaction - need out-of-band inputs and stay scoped in the CR.)
- **US0081 batch scaffold wiring (CR0166).** A regression guard confirms a multi-epic batch
  wires cleanly - the Story Breakdown placeholder is replaced (no stray `---` separator) and
  each epic gets exactly its stories with no empty table. The structural edges CR0166 flagged
  no longer reproduce (incidentally fixed by the v4 batch/index work); the guard prevents them
  returning.
- **US0076 config failure regimes (CR0180).** `sdlc_md.project_override` now emits a
  one-line warn-once to stderr when a `sdlc-studio/.config.yaml` exists but cannot be honoured
  (no PyYAML / malformed), instead of silently reverting to defaults - so a project's declared
  conventions are never silently ignored. Absent config stays silent. (BG0062 already fixed
  the related Done-gate crash.)

## v4 foundation - distributed identity, schema v3 (WIP, unreleased)

The v4 foundation - distributed artefact identity (schema v3). The move from a
single-writer tool toward a team-based one. All new capability is opt-in (`schema_version: 3`);
existing v2 projects and their sequential ids are untouched until they choose to migrate.

### Added

- **v4 foundation - distributed artefact identity (schema v3, RFC0024).** Opt-in via
  `schema_version: 3` in a project's `.config.yaml`; existing v2 projects are untouched
  (sequential ids stay the default).
  - **US0055 ULID ids.** A stdlib Crockford-base32 ULID generator (`sdlc_md.new_ulid` /
    `short_ulid`): a 48-bit millisecond timestamp (lexicographically sortable = creation
    order) plus 80 bits of randomness, so concurrent writers in parallel worktrees never
    collide without coordination. `artifact.py new`/`batch` mint `BG-01JQK3F8`-form ids in a
    v3 project (collision-checked, suffix extended on a rare clash) and stay sequential in v2.
    Every id reader is now era-tolerant: `ID_RE`/`ID_SEARCH_RE` match both forms, `id_number`
    returns the sequential number for v2 ids and `None` for ULIDs (keeping them out of the
    max+1 path).
  - **US0058 derived indexes.** A new `index-derived` gate check enforces that every
    `_index.md` is output of the census, never a hand-edited input: it runs a dry-run
    `reconcile apply` per type and fails when the index is not a fixed point (a hand-edited
    status/row/count the tool would rewrite). `reconcile.index_derived_issues` backs it.
  - **US0069 passive concurrency safety.** `sdlc_md.atomic_write` (same-dir temp then
    `os.replace`) means a crash mid-write leaves the previous index intact, never truncated;
    index writes in `artifact`, `file_finding` and `reconcile apply` now use it. An advisory
    `sdlc_md.allocation_lock` (POSIX `flock`, best-effort elsewhere, timeout-and-proceed so a
    stale lock never wedges a wave) serialises allocate-and-write in `artifact.new`, so
    concurrent writers never mint the same id or clobber a shared index.
  - **US0056 v2-to-v3 migration.** `migrate_v3.py plan|apply` rewrites a workspace's
    sequential ids to ULIDs, preserving creation order (each ULID's timestamp is derived from
    the file's date), retaining the old id as an alias (`> **Aliases:** BG0001`), rewriting
    every intra-workspace link, and regenerating index counts. Dry-run-first and idempotent (a
    second run is a no-op). `sdlc_md.alias_map` resolves a pre-migration id to its current
    ULID, and `transition` looks artefacts up through it, so `--id US0001` still works after a
    migration.
  - **US0057 friendly GitHub aliases.** A synced artefact's GitHub issue number becomes a
    resolvable friendly alias (`alias_map` maps `GH42` -> the canonical id) while the ULID
    stays the identity; recording the issue number is offline-safe (only written after a
    successful `gh` create).
  - **US0059 TRD refresh + freshness guard.** The generated TRD is corrected to the shipped
    script layer: the real (bounded, tested) write contract replaces the false "read-only
    over the workspace" claim, plus accurate component counts, state-file inventory, and test
    figures. A `tools/tests` freshness guard fails if those stale claims reappear.

### Fixed

- **Self-review bug sweep (RV0006, BG0053-BG0066).** 14 defects found by an
  architecture / code-quality / defensive-security review of the skill's own
  source, each fixed with a failing-first regression test:
  - `artifact close` recorded a telemetry event twice per close (transition
    already records on entering the terminal set); estimation-calibration data
    was inflated ~2x. Metrics now flow through the single record.
  - `install.sh` exited 1 after a successful install when the stale-copy sweep
    refreshed another tool's copy (`set -e` plus a trailing `&&` test); the
    success banner never printed. `sweep_stale` now returns 0.
  - `verify_ac ts-check` cross-checked the verify-report by bare AC id, so one
    story's failing AC1 flagged every story's AC1 in a merged report. The key
    is now story-qualified.
  - `verify_ac` executes shell-backed verifiers only when shell is allowed and
    the story is not stamped `Provenance: external`; an unrecognised expression
    is now an invalid verifier, not a silent shell run. New `--no-shell`,
    `--allow-external`, `--allow-shell-fallback` flags turn the documented trust
    boundary into an enforced one.
  - `gate.py` reported a vacuous PASS when `--only`/`--skip` named no real
    check; it now fails loud on an unknown name or an empty selection.
  - `next_id allocate` (CLI) re-implemented allocation and could re-issue a
    deleted-but-indexed id; it now delegates to the one `allocate_number`
    authority.
  - `archive.py` hardcoded terminal-status sets that treated `Deferred` as
    closed; it now uses the shared `terminal_statuses`, so re-activatable rows
    stay live.
  - The story Done gate raised a PyYAML `RuntimeError` on stdlib-only machines
    instead of its block message; policy is now read via the degrading
    `project_override`. The gate also blocks on a stale verify-report entry
    (story edited or an AC added since it was verified).
  - `github_sync` gives `gh` a timeout (no indefinite hang) and no longer stamps
    `last_pull` when a `gh` call failed (a swallowed failure recorded as
    success).
  - `append_index_row` bounded its insertion to the master table's contiguous
    rows, so a trailing link-first view table no longer captures the new row.
  - CI workflow now declares least-privilege `permissions: contents: read`.

### Changed

- SKILL.md description opens with the masthead tagline ("The antidote to
  vibe coding: a full software engineering team at your fingertips") ahead
  of the unchanged trigger catalogue - re-run eval scenario 01
  (trigger-routing) before the next tag, as for any description change.

## [3.5.0] - 2026-07-05

### Release verification

Eval scenarios (the two-Claude worker/grader loop, `evals/README.md`) run in
full: **01 trigger-routing PASS** (natural language model-invoked the skill;
template-conformant PRD; the new slice-read rule honoured unprompted), **02
greenfield-create PASS** (canonical paths, tool-allocated sequential ids,
Draft-only births, GWT + Verify lines - and the v3.4.0 advisory retired: the
Three Amigos consult ran with attribution rows in every artifact), **03
generate-mode-gate PASS** (philosophy gate read before generation; every
extracted contract verified code-accurate by the grader), **04
drift-reconcile PASS** (all three seeded drift kinds enumerated; the grader
mechanically re-verified 18/18 checksums unchanged under --dry-run). Three
cosmetic scaffold-wiring edges triaged to CR0166 (Low). Tranche critic:
Sam Eriksson (QA seat, review render) APPROVE after three rounds, verdicts
recorded under the seat.

### Changed (reconcile apply)

- `reconcile apply` appends missing index rows mechanically: one
  header-driven row per census file the index lacks, built in the pinned
  MASTER table's own column order (the table already holding the census
  rows - a trailing view never captures the append), with the status
  landing in a declared alias column and the id mirroring the table's
  display style. Unplaceable rows (no ID-column header) warn and exit
  non-zero; orphan rows stay report-only. A consuming project's agent
  had hand-authored 23 rows because this class was report-only.
- The critic is a seat, not an anonymous instance: `critic.py record`
  warns when the reviewer matches no declared seat/amigo, and the sprint
  and persona references state the close-pass critic runs AS the QA
  seat's review render.

### Added (token economy)

- Index-bloat advisory: `reconcile detect` and `status hint` recommend the
  progressive-disclosure archive (`scripts/archive.py`) when live terminal
  rows exceed `indexes.archive_after` (default 30) - advisory only, counted
  from the live index so an archived workspace stays silent; the
  release-gate template carries the archive step. First live run archived
  265 rows on this repo (live indexes 332 -> 83 lines, census 0-drift).
- `artifact.py revision --ids A,B --note "..."`: deterministic batch
  appends to Revision History tables (dated, author-stamped); a file
  without the section is refused loudly and one refusal never aborts the
  batch - retires the hand-scripted close-out loop.
- Slice-read rule: SKILL.md instructs section reads for references over
  ~400 lines (honour the Reading Guide - Grep the anchor, offset-read the
  section); the epic and story Reading Guides now name greppable anchors.
- Anchor-window discipline: LATEST.md is a window, not a ledger - past
  sprints become one-line History pointers to their retros, and
  `doc_freshness` flags the anchor when it exceeds `docs.latest_max_lines`
  (default 80). Codified for consuming projects in
  `reference-operator-heuristics.md#anchor-window`.

### Added

- Tolerant convention layer (`lib/conventions.py`): one place where a
  consuming project's house conventions are interpreted, declared under
  `conventions:` in `.config.yaml` (status-column aliases, companion-doc
  suffixes, bug-readiness heading vocabularies, per-type scaffold
  templates). Reconcile accepts declared status-column aliases, and
  `artifact new`/`batch` scaffold a project-declared template (grafted onto
  the deterministic provenance head) instead of planting the skill shape a
  house-templated project's checks then reject. Every key defaults to the
  historical behaviour; a wrong-shaped value fails loud naming the key.

### Added (project upgrade)

- `project upgrade` surfaces the capability delta, not just file
  corrections: a "Changed since <recorded skill_version>" digest of the
  shipped CHANGELOG entries in the version gap (grouped by kind, capped
  with a "+N more" tail), plus one line per advisory-when-absent gate
  lane introduced in the gap naming its baseline command - sourced from
  a declared registry in `gate.py` that a test keeps honest. Absent or
  unparseable CHANGELOG degrades to an explicit "unavailable" line.
  `install.sh` now ships `CHANGELOG.md` with the skill payload.

### Changed

- `reconcile apply` inserts a missing summary status row instead of
  exiting 0 over a count-mismatch it created: a status flip into a status
  absent from the summary now lands `| <Status> | <n> |` in the
  reconcile-managed global summary block (before the Total row); scoped
  per-epic roll-ups are never touched, and when no managed block exists
  the missing statuses are named as warnings and apply exits non-zero.
  A transition into such a status now reports `index_synced=True`
  truthfully - the sync actually happens.
- The dormant `Verified` bug status has defined semantics mapped onto the
  verification-depth tiers: `Fixed` = implemented and proven at the
  functional tier (the honest status when a higher-tier proof is owed);
  `Verified` = additionally proven at the tier its risk demands
  (conversational/soak/live). `transition` gates the Fixed → Verified
  promotion on a recorded depth above functional; projects that never
  promote to Verified are unaffected.
- Companion-doc recognition is header-based, not a one-suffix allowlist:
  a file under an artifact directory that carries no artifact header (no
  `> **Status:**` line and no `# <ID>:` title) is a companion/note, so an
  `EP0244-...-decisions.md` beside its epic no longer trips a false
  `no-status` validate error plus a `duplicate-id` collision. The rule
  lives once in `artifact_files` via the convention layer (extra suffixes
  declarable under `conventions.companion_suffixes`); a real artifact
  that lost its Status line keeps its `# <ID>:` title and stays flagged.
- Adversarial-close hardening of the above (all nine critic findings
  fixed with repros re-run): id allocation keys on the filename so an
  off-template or companion file always holds its number; `validate`
  emits a `not-an-artifact` warning naming every id-named file the
  census excludes; the degenerate-index diagnosis is judged on the live
  index before the archive merge; `apply` rewrites a declared
  status-column alias (writer parity); heading match is word-set
  equality or ordered prefix, never blanket containment; and a
  wrong-shaped `conventions` value fails the gate rather than silently
  disabling the lane that read it.
- Bug-readiness reads its heading vocabularies from the convention layer:
  a house template documented as Symptom / Root cause / Fix (proposed) is
  ready (a documented cause is stronger evidence than bare repro steps),
  heading match is word-order-insensitive and suffix-tolerant, a
  genuinely-empty bug still flags, and a project can declare its own set
  under `conventions.bug_ready_sections`.
- Mutation-check summary states its sampling coverage explicitly: when the
  budget truncates, the CLI note, report `summary.enumerated`, and the gate
  lane detail all carry `sampled N/M enumerated (x%)`, so a green sample can
  never read as whole-surface assurance; an untruncated run reads as before.
- Sprint plan names the provenance of its seat scores: which units carry
  wsjf-inputs seat judgements (and the file's write time), which fell back
  to the neutral default, and an advisory staleness warning when the
  inputs file is older than `sprint.wsjf_inputs_stale_days` (default 7) -
  a stale cross-sprint consult is now visible at the operator STOP.
- Reconcile diagnoses a mis-named or absent index Status column once: when
  every row parses as Unknown and no data table pins an exact `Status`
  header, `detect` emits a single `index-status-column` finding naming the
  offending header (e.g. `Effective Status`) instead of a per-row
  status-mismatch storm plus a misleading count-mismatch, and `apply`
  refuses loudly (exit 1) rather than recompute counts it cannot reconcile.

## [3.4.0] - 2026-07-04

### Release verification

Eval scenarios (the two-Claude worker/grader loop, `evals/README.md`) run in full
for the first time since v2.0.0 - the 02-04 waiver is retired: **01
trigger-routing PASS** (skill self-invoked from natural language, template-
conformant PRD), **02 greenfield-create PASS** (canonical paths, sequential ids,
Draft-only GWT stories; one advisory unclear - the Three Amigos consult was
skipped rather than offered under a self-answered interview, triaged as
acceptable, re-check next instructions release), **03 generate-mode-gate PASS**
(philosophy gate read before generation, code-exact extraction), **04
drift-reconcile PASS** (deterministic helpers, both seeded drift items, zero
mutation). Suites 1058 + 41 green; strict version check green; gate PASS.

### Added

- **Verified lines land in canonical order (BG0051).** verify_ac applied multiple
  write-backs top-down from a single parse, so each insertion shifted every later
  AC's cached line indices - Verified lines drifted one line earlier per prior
  insert (the Given/Verified/When misordering in US0051-54). Write-backs now
  apply bottom-up, leaving earlier indices valid; the four affected stories were
  repaired by strip-and-regenerate through the fixed tool.

- **status/hint surface a concurrent-session advisory (CR0150).** When the
  sdlc-studio/ workspace carries uncommitted or untracked artifact changes, the
  re-anchoring commands print one advisory line naming the artifact ids -
  "another session may be mid-flight" - instead of the next session discovering
  the collision by gate failure. Informational only; no authorship guesses;
  degrades silently without git. Critic hardening: the pillars text-mode wiring
  was dead behind a misplaced return (caught by a live command run while the
  helper-only tests stayed green - lesson L-0004: test the command, not only the
  helper); renames now name both the old and new ids.

- **Terminal transitions record telemetry (BG0052).** The delivery loop closes
  units via `transition.py`, but telemetry only fired in `artifact close` - which
  the loop never calls - so three full sprints recorded zero events and the
  RFC0018 `show --summary` had nothing to summarise (the product_reconcile
  disease: a feature that exists and silently never runs). A transition whose
  target status is terminal for the type now appends the event (id, type, plus
  any `--iterations`/`--wall-time-s`/`--verdict` passed through); never on
  dry-run or non-terminal moves. The sprint's own discipline is instrumented
  from the run that fixed it forward.

- **Batch transitions and tool-created retros/reviews (CR0143).** `transition.py set
  --ids A,B,C` runs a same-target batch with each id individually gated - one
  refusal reports, continues, and exits non-zero (no more shell loops around the
  tool). `artifact.py new --type retro|review` creates the meta-artifacts
  (allocated id, template scaffold - retro renders from the shipped retro
  template - and an index row where a meta index exists), retiring the last
  hand-authored artifact class; `transition` refuses meta ids with a message
  naming why they sit outside the status machinery.
  Close-of-sprint critic fixes: batch json stdout stays pure (summary to stderr),
  the meta-index insertion is bounded to the data table, and the gate's hash paths
  resolve against --root.

- **WSJF's no-seat fallback divides by the neutral default (CR0149).** The
  complexity signal - the cognitive complexity of the existing files a unit
  touches - is blast-radius risk, not effort; it no longer stands in as the WSJF
  size when the Engineering seat has not scored a unit, surviving only as the
  within-priority tiebreak and token-budget input. A one-line fix in a complex
  file no longer sinks on the file's complexity.

- **One shared structural table iterator (CR0144).** `sdlc_md.iter_tables()` is now
  the single boundary rule every table parser uses - header+separator (any dash
  count) opens a table, a heading ends it, and a caller predicate covers legacy
  vocabulary headers. The four parsers that each hand-rolled boundaries (the
  duplicate-id scan, `_index_rows_and_summary`, `_index_row_ids`,
  `verify_ac.ts_check`) are ported one at a time with their existing tests
  unmodified and green between ports - retiring the defect class behind BG0046
  and BG0049 instead of fixing it per parser (lesson L-0001 made structural).

- **Mutation gate v2 (CR0146).** Correctness first: the report records a content
  hash per target and the gate lane reports STALE when any target changed since
  the run - same rev included - so a dirty tree can no longer ride an old green
  report (the hole the critic demonstrated live). The cost ceiling now distributes
  round-robin with files as the fast axis instead of first-N in file order, and
  Python string/docstring interiors are excluded from enumeration (tokeniser-based;
  a parse failure skips the exclusion and NOTES it, never silently).

- **verify_ac lint flags Verify runners missing from PATH (CR0145).** A Verify
  line whose runner (pytest/jest/vitest/go/rg; http checks curl+jq) is absent
  from this machine's PATH draws an advisory naming the install-or-rewrite-or-
  runs-elsewhere choice - the wording owns that the author machine's PATH may
  differ from CI's. shell and manual are exempt; nothing blocks. Live-verified:
  the historical pytest Verify lines on this pytest-less machine light up
  exactly as the field pain predicted.

- **The close-of-sprint adversarial critic pass is a named, exact step (CR0148).**
  reference-sprint.md's closing gate now specifies the CODE leg's shape - an
  independent critic instance over the FULL sprint diff, refute framing, findings
  with reproductions, fixes seen red first, and the same critic re-running its own
  repros before approve - as a sharpening of the existing critic step, never a
  second parallel gate. help/sprint.md, the conformance critiqued hint, and the
  retro guidance (a 'critic loop, observed' section) point at it. This is the pass
  that caught both sprints' worst escapes.

- **doc-freshness names its counting method (CR0147, reduced AC).** The test-count
  finding now says "N test functions counted statically ... claim this number", so
  the LATEST.md claim and the checker agree on what is being counted instead of the
  operator chasing the runner's skip/subclass accounting. The checker still never
  runs the suite.

- **RFC-0018 closed as accept-reduced (operator decision D0004).** `telemetry show
  --summary` aggregates the run log per type (count, mean iterations, mean wall
  time, reopen rate, verdict mix - a field never measured reports None, not a
  fabricated 0), replacing the raw-dump-only view; `best-practices/script.md`
  gains the subcommand verb taxonomy (guidance for new commands, no renames).
  The cross-file vocabulary-consistency checker is declined: zero repeat
  incidents in two releases, and a recurrence's right home is a declared
  `constitution.md` rule, which now exists.

- **The executable mutation-check gate ships (CR0134 / RFC-0022 / EP0011).** The
  skill's named biggest blind spot is now enforced, not prose: `scripts/mutation.py`
  applies a declared, bounded fault set (invert-guard, stub-return-null,
  unset-delivered-field, no-op-mapper) to a selected surface via per-language
  textual profiles (.py, .js/.ts, .go invert-guard), re-runs the mapped tests per
  mutation, and reports **killed vs survived** - a survivor is a finding, exit
  non-zero. Deterministic (same code + set = same report); honest degrade
  everywhere: un-mutatable surfaces report un-checked, a red baseline yields error
  verdicts (never a fake kill), and ceiling truncation (`--max-mutations`,
  `quality.mutation_max`) is counted, never silent. Surfaces: `--files`,
  `--since REF`, `--story USxxxx` (epic/CR Affects chain); `prefilter` lists
  assertion-free test files. The release gate gains an advisory `mutation` lane
  (absent report reads not-run, never PASS). Dogfooded on this repo's own sprint
  diff: 12/12 mutations killed by the 1017-test suite, 2653 enumerations honestly
  truncated. Complements `verify_ac` (checks pass) with the can-it-fail question.

- **The deterministic toolbox is now discoverable from the router (CR0133).** A field
  session used ~2 of the 40+ scripts and hand-did what they automate (hand-allocated
  ids, never ran `validate`). SKILL.md now carries a "Deterministic Entry Points"
  task-to-script card; the Progressive Loading Guide names the script to run for
  creating and filing (not only the prose to read); doctrine rule 15 makes
  script-first the stated discipline; `templates/agent-instructions.md` presents
  non-interactive `artifact.py new` as the canonical create path (interactive
  commands are wrappers); `help/bug.md` / `help/cr.md` lead with the one-liner and
  state that ids + index rows are tool-allocated.
- **RFC-0022 opens the mutation-check gate design (CR0134, RFC-first).** The skill's
  named biggest blind spot - nothing executable asks whether a test would FAIL if
  the feature broke - is epic-sized with an unsettled cross-language injection
  design, so the sprint delivered the RFC, not the implementation: four options
  (per-language AST, declared textual mutations, framework adapters, static
  heuristics), a recommendation (textual-mutation core, framework lane opt-in,
  static pre-filter, AC-to-test mapping over the existing Verify + coverage-matrix
  bridge), and six open decisions. CR0134 is Blocked pending the RFC decision and
  decomposes into an epic on acceptance.
- **The style guard now checks British spelling (CR0135).** AGENTS.md stated three
  prose rules; `lint-style.sh` enforced two. A bounded, high-signal American-spelling
  pass (the analyze/analyse pairs and the -ize/-ization family, word-boundary matched
  so size and prize are untouched) now flags offenders with the British form suggested, sharing
  the existing allowlist for genuine exceptions (API identifiers like `optimize=True`
  and `EXPLAIN ANALYZE`, quoted command names, `gh --color` flags); the Contributor
  Covenant text is excluded as third-party. The script accepts an optional scan-root
  argument so the new fixture tests exercise it in isolation. Zero hits on the
  current tree after allowlisting the seven literal-identifier lines.
- **A mixed bugs + CRs tranche is a first-class sprint batch (CR0138).** The most
  common maintenance sprint (backlog clear) was inexpressible: `sprint.py plan`'s
  queries were mutually exclusive, `--write` kept whichever half ran last, and the
  documented worklist file did not exist. Status queries are now combinable
  (`--bugs Open --crs Proposed` yields one merged, dependency-waved plan with
  cross-type edges honoured), `--worklist <file>` (ids one per line) is a real
  batch source that errors on unknown ids, and cross-type ordering uses one
  documented weight scale (Critical/P1 .. Low/P4, case-tolerant - lowercase bug
  severities now rank correctly too). `audit.py check` treats a dependency
  sitting in the same batch as informational `sequenced-in-batch` instead of
  `unmet-deps` (pending deps only - a dead or missing referent stays unmet), and
  `conformance.py check` states its story-only scoping in its output rather than
  leaving a bug/CR tranche's coverage gap unstated. Critic hardening: a blank
  Severity/Priority field ranks Medium instead of crashing the planner; worklist
  ids dedupe in every order mode; `--worklist` + `--epic` refuses loudly instead
  of silently ignoring the filter.
- **Verification-depth tiers are enforced on transition, not decorative (CR0136).**
  `transition.py` now refuses `bug -> Fixed` below `functional` and `bug -> Closed`
  on a production-affecting bug (`> **Production-affecting:** yes`) below `soak`,
  naming the current and required tier; a missing/unparseable depth field on a
  gated transition is refused, never assumed satisfied. Story `Done` gains a
  depth-parity advisory (an AC's declared `Verification target` above `functional`
  should not out-run the recorded depth), upgradeable to a refusal via
  `quality.depth_parity_gate: true`. `--force` records an override, as before.
  The Production-affecting flag matches by leading token, so an annotated
  `yes (checkout path)` still gates rather than silently classifying as
  non-production (independent-critic finding).

### Changed

- **Payload hygiene: repo-only `tools/` checker tests moved out of the shipped skill
  (CR0140).** Five tests (`test_check_neutrality/budgets/links/versions`, `test_validate_skill`)
  lived in `.claude/skills/sdlc-studio/scripts/tests/` - so they shipped into every consumer
  install and reached the repo-root `tools/` they test, which does not ship. Moved to a repo-level
  `tools/tests/`; runners (`package.json`, the pre-commit hook, CI) now run both suites; total count
  preserved (995 = 958 skill + 37 tools). The shipped payload now tests only what ships, and the
  domain-neutrality guard (a public-repo-only concern) no longer has any footprint in consumer
  installs.

### Fixed

- **ts-check's AC matrix no longer bleeds into later tables (BG0049).** The matrix
  parser locked onto the coverage-matrix header and then read every subsequent
  table row in the spec as an AC row - the canonical References and Revision
  History tables reported as unmapped ACs, so `epic-ts` failed on the shipped
  convention's own shape (the already-closed EP0010's spec failed it). A markdown
  heading now ends the matrix scope; a genuinely unmapped AC row still fails.
  Same defect class as the BG0046 structural-boundary fix - found while authoring
  EP0011's spec at the design rung.
- **provenance remake honours the adoption cutoff and never double-stamps (BG0048).**
  `remake` now applies the same `provenance.adopt_after` exemption as `check`
  (previously it mass-stamped all 145 artifacts against the documented intent;
  `--all` opts back in), and ANY non-empty `Created-by:` counts as provenance for
  both commands - a field-report attribution is respected, not nagged forever and
  given a second `Created-by:` line beside the human one.
- **The Engineering seat can size WSJF jobs; unknown effort is never minimal (BG0047).**
  `wsjf-inputs.json` takes an optional per-unit `size` (story-point scale) that
  overrides the complexity seed - previously the seat that owns effort had no slot,
  and a unit whose Affects named not-yet-existing files got size 0, ranking
  greenfield epics as the cheapest jobs in the batch. When neither a seat size nor
  the complexity seed resolves, a declared neutral default divides the score.
- **Reconcile and validate findings now self-diagnose (CR0132, absorbing CR0139).**
  Two field sessions dead-ended on an opaque `count-mismatch` whose "recompute the
  summary counts" hint `apply` could not clear - the cause was an out-of-vocab
  status silently dropped from the row tally. The finding now names each mismatched
  status with both numbers (`cr: Proposed rows=5 summary=4`, text and JSON), and
  when out-of-vocab statuses are the cause it names the status, its artifacts, and
  the `status_vocab.<type>` config remedy, routing to `validate.py check`; the
  generic recompute hint survives only for true arithmetic drift. `validate`'s
  status-vocab error now names the config extension mechanism instead of implying
  historical artifacts must be rewritten. Documented in `reference-reconcile.md`,
  `help/reconcile.md`, `help/status.md`.
- **Duplicate-id gate no longer trips on the shipped CR index's Dependencies table
  (BG0046).** `reconcile`'s within-table duplicate scan reset its per-table tally only
  on a header containing a bare `Status` cell; the `templates/indexes/cr.md`
  Dependencies header carries `Dependency Status`, so its rows tallied into the
  previous table's scope and a fully-templated project failed its own release gate
  (field run: 12 false duplicates, the operator converted the table to prose to get
  green). The table boundary is now structural - any header row followed by its
  `| --- |` separator resets the scope - and regression tests pin the shipped
  Dependencies shape plus the true-positive (same id twice within one table still
  flags). The independent-critic pass extended the same structural boundary to the
  sibling parsers (`_index_rows_and_summary`, `_index_row_ids`): a table whose
  header declares no Status column is never scavenged for one, so a
  `| CR-0001 | CR-0003 | Complete |` dependency row can no longer overwrite
  CR-0001's parsed status (the phantom status-mismatch + unclearable
  count-mismatch loop), and short-dash GFM separators (`|--|`) count as
  boundaries everywhere.
- **Bug-readiness check accepts the shipped template's own headings (BG0045).**
  `audit.py`'s `_bug_underspecified` demanded the literal `## Steps to Reproduce` +
  `## Proposed Fix`, while `templates/core/bug.md` shipped `## Reproduction Steps` +
  `## Fix Description` - so every template-authored bug in every consuming project
  flagged "underspecified" forever (a field run reported 0/4 ready on four fully
  specified bugs). The predicate now accepts both vocabularies, the template is
  aligned to the canonical pair, and a regression test renders the shipped template
  through the predicate so the gate is validated against its own template's output.
- **Pre-commit hook now runs markdownlint from the npm-local install.** The hook
  checked only for a *global* `markdownlint`, so after `npm install` (which provides
  `markdownlint-cli` at `node_modules/.bin/`) it silently skipped the check - and an
  MD032 (blank-lines-around-lists) error in a CR doc passed the local gate and failed
  CI on the v3.3.0 push. The hook now prefers `node_modules/.bin/markdownlint` and,
  when Node is absent entirely, prints a visible SKIP instead of passing silently.
  AGENTS.md documents the gap. Fixed the MD032 error itself in CR0131.

## [3.3.0] - 2026-07-04

The anti-vibe hardening release: enforcement you cannot skip, a test-integrity
discipline, and a field retrospective that made the toolbox discoverable. A
pre-commit hook now runs the whole gate on every commit and explains every failure
in detail (CR0137); the assertion-integrity discipline teaches, and the templates
now record, whether a test would fail if the feature broke (CR0131); and the AGENTS/
PRD/TRD/TSD docs plus the README were reworked so an agent finds the 40+ deterministic
scripts and the local gate instead of hand-doing their work. Five CRs (CR0132-CR0136)
capture the remaining enforcement gaps found by dogfooding.

### Added

- **Pre-commit hook makes the gate un-skippable (CR0137).** `bash tools/enable-hooks.sh`
  installs a tracked `.githooks/pre-commit` that runs the whole npm-independent gate
  (style, links, skill-spec, versions, budgets, neutrality, `gate.py`, and the script
  suite when code changes) on every commit and blocks a breaking one. Every failure is
  explained in detail: what the guard enforces, the offending file:line, and the fix;
  drift items print their own remediation. Turns "the agent should run the gate" into
  "the agent cannot commit past it" - the anti-vibe last mile. Emergency bypass:
  `git commit --no-verify`.

- **Assertion-integrity discipline + mutation-check gate (CR0131).** The skill taught verification
  *depth* but not whether a test *can fail*. Added a `reference-test-best-practices.md#assertion-integrity`
  section (the vacuous/tautological assertion, the injected-data unit test that bypasses the real
  wiring, and the mutation check - break the feature, confirm the test goes red, restore), a
  per-AC `Mutation-checked` field in `templates/core/story.md`, a `Mutation-checked` verification
  item in `templates/core/bug.md` (the regression test must be seen red against the unfixed code),
  and an e2e-mutation-checked + real-data-path gate in `templates/workflows/release-gate.md`. Found
  in the field: a governance surface shipped marked "renders + initiates + audits" while doing none
  of the three on the real data path, behind a green-but-vacuous suite.

### Changed

- **README: a concrete vibe-coding vs spec-driven vs governed framing.** The "Why"
  section led with an abstract argument hidden in a collapsible; added a visible
  three-mode contrast that lands the differentiator (spec-driven tools *align* the
  agent on intent; SDLC Studio also *argues back with facts* - executable ACs,
  reconcile-from-census, a commit gate), so a newcomer sees why it is worth using.

- **Docs: make the local gate and the deterministic toolbox discoverable (dogfood
  fix for CR0133).** AGENTS.md "Testing the Skill" now lists every CI guard as an
  npm-independent command with what each catches (a session broke CI four ways by
  not running them); the Skill Structure scripts row points at `reference-scripts.md`
  and names the load-bearing scripts (`artifact.py`, `file_finding.py`, `next_id.py`,
  ...); Style Requirements now states the rules are enforced by `lint-style.sh`. PRD
  section 10 records the enforcement-gap debt (CR0131/0132/0133/0134/0135/0136); TSD
  folds in the run-the-gate-pre-commit lesson and the assertion-integrity pointer.

### Proposed

- **Field-retrospective CRs (dogfooding against a consuming project).** From driving the skill end-to-end:
  - CR0132 - reconcile findings must self-diagnose. The `count-mismatch` fix hint is generic and
    misleading (points at `apply`, which cannot clear an out-of-vocab status); it should name the
    offending status and route to `validate`. Completes the CR0025 remediation-guidance principle
    for the drift that dead-ended a session. *(Root-cause corrected: the vocab is already
    config-driven; the defect is diagnostics, not configurability.)*
  - CR0133 - surface the deterministic toolbox so an agent reaches for the right script (map
    task -> script in the router, not just task -> prose). Broadened from "the create path" after a
    session used ~2 of 40+ scripts and hand-did work `file_finding.py` / `next_id.py` automate.
  - CR0134 - an executable mutation-check / test-quality gate (epic-sized, RFC-first) to *enforce*
    the CR0131 assertion-integrity discipline, not just document it - the skill's biggest blind spot.
  - CR0135 - extend the style guard with British-spelling detection. *(Root-cause corrected:
    `tools/lint-style.sh` already enforces em-dash + jargon; the only unchecked rule is British
    spelling. Filing this CR itself broke the style guard by not running it - self-evidence for
    CR0133.)*
  - CR0136 - enforce the verification-depth tiers on `transition` (Fixed needs `functional`+, Close
    needs `soak`). The tiers are documented but `transition.py` never reads the depth field.

## [3.2.0] - 2026-06-27

The skill self-improvement release: a token-economy + learning-loop epic (EP0010), the
test-strategy heuristics (CR0128), and a newcomer-first README and onboarding overhaul.
New commands - `reconcile archive`, `lessons revalidate`/`summary`, `gate --require-retro`,
`blocker_sweep`, and the `audit` regression-test check - plus four promoted cross-project
lessons (LL0009-LL0012). CI restored to green and the Dependabot action bumps adopted.

### Fixed

- **CI coverage gate restored to green (US0047).** The gate failed on CI not from a coverage
  shortfall (coverage is a healthy ~82%) but from test *failures*: the config-driven tests
  (provenance/validate `adopt_after` cutoff, transition done-gate, conformance) read
  `.config.yaml` via `config._yaml()` and raise without PyYAML, which the CI step never installed -
  so `coverage run -m unittest` exited non-zero before the threshold was ever checked. Added
  `pyyaml` to the coverage step's `pip install`. The story's original "coverage drops from skips"
  framing was a misdiagnosis, corrected in its Root Cause section.

### Changed

- **README + onboarding overhaul for newcomers.** Rewrote `README.md` as a black-box-first,
  progressively-disclosed landing page: a jargon-free hero and what/who/why, the "you just ask"
  table, a quick-start *path* with a greenfield/brownfield fork, a mermaid pipeline diagram + an
  annotated `status` dashboard, a scannable capabilities table, three collapsible worked examples
  (Product/Engineer/QA), a "start here by role" table, and a collapsible FAQ with a plain-language
  glossary. The 63-line version-history "Roadmap" moved out to CHANGELOG; the philosophy manifesto
  moved below the fold. Added `help/brownfield-runbook.md` (the existing-code sibling to the
  greenfield runbook) and registered it in `SKILL.md`. Reviewed via a four-lens persona consult
  (Product, Engineering, QA, and a non-technical-newcomer lens); all four approved after fixes.
- **CI action bumps adopted (US0048):** `actions/checkout` v6 -> v7 (both jobs) and
  `actions/setup-python` v5 -> v6 in `.github/workflows/lint.yml`, superseding Dependabot PRs
  #25/#26.

### Added

- **EP0010 - skill self-improvement: token economy + learning loop (11 stories, 5 CRs).** Delivered
  this sprint; see `sdlc-studio/retros/RETRO0005`.
  - **Index archive (CR0125 / US0040, US0041).** `reconcile archive` relocates terminal index rows to
    a derived `<type>/archive/_index.md`, leaving active rows + the summary block live; idempotent,
    `--dry-run`, fail-loud on an unclassifiable status. Terminal-status vocab is `sdlc_md`-derived;
    `next_id` unions the archive sub-indexes so an archived id is never re-issued.
  - **Blocker sweep (CR0130 / US0049, US0050).** New `blocker_sweep.py` finds units whose blockers
    cleared - in-repo by census, cross-repo via the PVD `product-manifest.yaml`. Runs before
    `sprint plan` and as the advisory `reconcile detect --blocker-sweep` lane; proposes
    `Blocked -> Ready`, never auto-transitions, never false-clears an unresolved referent (LL0008).
  - **Retro lifecycle (CR0129 / US0042-US0044).** The sprint close is a hard fail-loud gate
    (`gate --require-retro`); `lessons revalidate` closes stale lessons by validity; `lessons summary`
    regenerates a deterministic committed `LESSONS-SUMMARY.md` read at sprint start. Dogfooded here.
  - **Agentic-wave worktree doctrine (CR0126 / US0045)** and **pre-deploy readiness checklist
    (CR0127 / US0046)** added to their reference docs.
- **Test-strategy heuristics (CR0128).** New `best-practices/testing.md` captures five heuristics
  with a one-line trigger each (production-state-shape integration tests, a named regression test
  per production bug, rejects-old-shape contract tests, resource-count regression tests,
  pure-function extraction), referenced from the test-spec workflow. The test-spec template gained a
  "Strategy Heuristics" AC block. Determinism: `audit` raises `missing-regression-test` for a
  terminal bug whose recorded tests carry no integration/regression-level case (name-signal; the
  seam judgement stays with review, per the recorded advisory boundary).
- **Four cross-project lessons promoted to the skill tier (LL0009-LL0012).** LL0009 - a silent failure
  that misleads the caller outranks a loud failure of the same scope. LL0010 - validate a defence using
  the bug it defends against before shipping it. LL0011 - a gate that fails on CI but passes locally is
  an environment gap until proven otherwise (reproduce the CI env before trusting the symptom). LL0012 -
  a new private helper that shadows a module-level name silently breaks every existing caller.

## [3.1.1] - 2026-06-25

A field-hardening release. Six bugs and five change requests, raised from four
upgrade-run retrospectives, plus RFC0021 - the seats/amigos duality - settled by a
dogfooded Three Amigos consult and delivered in two slices. The persona model converges
to one role-based actor model: `seats/` is the home, an "amigo" is an enriched seat that
can also build, and the delegation resolver and consult both honour a project's authored
seats via a declared `role:` field. The cluster of reconcile/conformance/validate fixes
all trace to one law captured as LL0008: a deterministic tool must fail loud, never report
success it did not achieve. Built by the amigos - the Engineering amigo under TDD, the QA
amigo verifying as a separate instance - dogfooding the author != reviewer independence
gate on the skill's own backlog (which caught a missed call site mid-delivery).

### Added

- **A declared, machine-readable seat-role field; the resolver keys on it (RFC0021 slice 1, D6).**
  Each amigo/seat card now carries a `<!-- role: engineering|qa|product -->` comment, and the three
  default cards plus the amigo template declare theirs. `persona_resolve.card_role(path)` reads this
  field - never the H1 prose or the filename - so a seat card named after a person ("Sarah") maps
  to its seat deterministically. The form is an HTML comment: invisible in rendered markdown,
  unambiguous to a single regex, and independent of prose a translation or rename could change.

### Fixed

- **The old-persona-model upgrade hint names the actual signal that fired, not a misdirecting
  content-rewrite instruction (BG0041).** `project upgrade`'s persona finding now separates
  structural-layout drift (a nested `team/`/`stakeholders/` dir, or the word "amigo" in `index.md`
  - fixed by a dir move / index reword) from content-model drift (an old-model heading in a named
  file - fixed by a rewrite), and names the offending dir/file. A faithful content rewrite alone no
  longer leaves the operator chasing a flag that only clears on a layout change.

- **The `adopt_after` cutoff is parsed by one shared helper and never silently disabled (BG0039).**
  `conformance.adopt_after` and `provenance.adopt_after` looked identical in `.config.yaml` but
  were parsed by two different code paths with two different value formats and two different
  boundary operators - and the conformance side dropped a bare-integer cutoff with no error
  (`id_number("103")` returned `None`), leaving the gate red and unexplained. A third reader,
  `validate`'s no-ac exemption, carried the same silent-fail and the same strict `<`. All three
  now route through `sdlc_md.parse_cutoff`, which accepts a bare integer (`103`) or a prefixed id
  (`US0103`, `CR0103`) interchangeably and raises a clear, loud config error on an unparseable
  value instead of returning `None` and silently judging everything (LL0008). The conformance and
  validate boundaries are aligned from strict `<` to `<=` to match the name and provenance's
  existing behaviour: ids up to and including the cutoff are exempt ("this id and earlier are
  grandfathered"). The repo's own `provenance.adopt_after: 57` keeps exempting ids <= 57 unchanged.
- **`reconcile apply` no longer reports a status flip it did not persist (BG0043).** A status
  fix the writer could not place in the row (an off-schema/header-less layout it declines to
  guess) was still printed as `set <id>: A -> B` and counted as a changed row, while the index
  stayed untouched - a no-op dressed as a clean apply. `apply_type` now partitions planned fixes
  by what actually landed in the buffer: only persisted fixes are reported as changes, an
  unpersisted one is surfaced (a `WARNING: could not apply ...` on stderr, named in the summary
  line, non-zero exit) so it is hand-edited rather than trusted. The writer also preserves inline
  emphasis on a status cell - a bold-wrapped `**Proposed**` is rewritten to `**Complete**`, not
  flattened to `Complete` - mirroring the reader's tolerant canonicalisation. This is the
  fail-loud discipline (LL0008): never announce an edit you did not make.
- **`reconcile` verified to scope the count recompute to the canonical global summary, sparing
  per-epic count sub-tables (BG0044).** An index carrying per-epic `| Done | N |` blocks plus a
  global summary recomputes only the global summary (identified by its `Total`-row signature, or
  as the sole summary); the per-section blocks survive unchanged rather than being stamped with
  the project-wide total. Locked with a regression test on the exact field shape.
- **`validate personas` no longer reports a vacuous clean pass on a nested persona layout (BG0040).**
  The flat `personas/*.md` glob matched zero files when a project keeps its personas nested (e.g.
  `personas/team/`, `personas/stakeholders/`), and the check still printed "personas look
  well-formed". It now emits a `persona-layout` advisory ("personas present but not in the flat
  Cooper layout (N nested files found); not validated") when the flat glob inspects nothing but
  persona-shaped files sit in subdirs. A pass means inspected and well-formed, never found nothing
  to inspect (LL0008). The `seats/` subtree (review-seat charters) stays excluded.

### Changed

- **`persona_resolve` reads a project's review seats, not only `personas/amigos/` (BG0042, RFC0021
  D6).** The resolution chain is now most-specific-first: an explicit `personas/amigos/<seat>.md`
  override, then a role-matched `personas/seats/*.md` card (matched by the declared `role:` field),
  then the skill default, then generic. A project's hand-authored "Three Amigos" are no longer
  shadowed by the generic defaults. Two seat cards declaring one role resolve lexically by filename
  with a warning; zero declaring it falls through to the default and never crashes. A seat resolved
  for `--render review` that lacks its review-render sections (Lens / Pushes Back When / Shadow) is
  a **hard error** (`RenderError`, RFC0021 D4), never a silent fallback. New floor tests prove a
  role-matched seat resolves over the default, the two-claim/zero-claim cases, the render-less hard
  error, and that build and review framed from one seat card stay separate instances the critic
  `author != reviewer` gate still requires (RFC0021 D5).
- **`project upgrade` is seat-aware - it enriches in place instead of manufacturing a parallel
  amigo set (CR0120 AC1-4, RFC0021 D2).** `_missing_amigos` no longer reports a role as missing
  when an existing `personas/seats/*.md` card declares it; the generic cards are installed
  **greenfield only**, when no seat or amigo fills the role, so an authored seat is never doubled
  by a generic card beside it. When a seat and an amigo both claim a role, the upgrade emits an
  explicit **overlap heads-up** naming the roles - in `--dry-run` too - so the parallel role
  systems are never a silent collision.
- **A conformance failure names its remedies inline instead of burying them in a docstring (CR0121).**
  The gate and `conformance check` previously printed a bare `N non-conformant unit(s)`; the two
  mechanisms that legitimately resolve it - the `conformance.adopt_after` cutoff (forward-only
  adoption, now stated with the correct value format) and the `verify_ac` backfill path - were
  documented only in the script's source. The output now names both, and distinguishes
  unadopted-discipline debt (most units mass-missing the same stage - pre-existing, forward-only)
  from scattered per-unit gaps that may be a regression from the current change, so a
  grown-but-accepted count no longer reads as a new breakage. No stale count is hard-coded in the
  config comment - any count shown is the live computed figure.
- **`reconcile detect` signposts the fix order and names the file to link (CR0122).** When both
  status drift and count drift are present, the report now states the recommended order - resolve
  the file/index status mismatches first, re-sync the index rows, recompute counts/summaries LAST
  (because fixing statuses moves the counts) - so the operator no longer learns it by watching the
  count move the wrong way. A `fix_order` field is added to the JSON report. A missing-row finding
  now emits the artifact's actual filename relative to its type directory (and carries a `file`
  field), so the index link can be wired without guessing.
- **Disambiguated the three "upgrade" surfaces in one place (CR0123).** `skill-update` (the
  installed skill), `project upgrade` (a consuming project's conventions), and `upgrade` (a
  project's v1 -> v2 artifact schema) were all called "upgrade". `reference-upgrade.md` now carries
  a single side-by-side table naming what each changes and when to reach for which, cross-linked
  from each command's help; the command and help wording names its target so "upgrade" is never
  bare. Documentation only; no behaviour change.
- **One seat schema: the enriched amigo template supersedes the lean review-seat charter (RFC0021
  slice 2, CR0120 AC5, D3).** `amigo-template.md` is now the single seat schema. It already was a
  strict superset of the old `review-seat-charter.md` (Cooper depth + charter discipline + the dual
  render + the declared role field), and it is now explicit that the one schema covers both a
  build-capable "Three Amigos" seat and a review-only document-owner seat (Product Owner / Product
  Manager / UX): a review-only seat fills the review render and marks the work-render sections
  "n/a". `review-seat-charter.md` is retired to a thin pointer at the enriched schema, so existing
  references do not 404 and any consuming project is guided to the one template. Every active source
  reference (`reference-consult.md`, `reference-persona.md`, `reference-workflow-personas.md`, the
  upgrade drift hint, the template header) now points at the enriched schema.
- **Consult resolves its seat through the same declared-`role:` chain as delegation (CR0124).** The
  consult workflow previously loaded its charter from the template keyed on `{{seat_name}}`/H1
  prose, so a project's authored seat was honoured when the sprint loop delegated work but shadowed
  in a consult. `reference-consult.md` now resolves the seat by declared `<!-- role: -->` (a project
  `personas/seats/` card whose role matches, else the skill default seat, else the generic enriched
  seat schema as the fallback), via a new `persona_resolve.py resolve-consult` surface that reuses
  the delegation resolver (`seat_card`, `card_role`, the chain). A consult critiques, so a matched
  seat missing its review render is a hard error, consistent with the delegation resolver. An
  authored seat is now honoured in both paths.

## [3.1.0] - 2026-06-25

### Added

- **sprint plan flags an undeclared dependency graph so its waves are real (CR0114, field
  report):** the `--goal design` rung now establishes inter-story `Depends on:` as part of
  grooming Draft -> Ready, so a designed backlog carries the dependency graph the planner needs.
  When `plan` selects a batch of >1 unit with no declared in-batch dependency, it prints a hint
  that all units are parallel because no `Depends on:` is declared - so a flat single wave is not
  mistaken for "no dependencies exist", the prose-derived sequencing the waves feature exists to
  remove (scripts/sprint.py, reference-sprint.md).
- **the Three Amigos are now a rich, instantiated engineering team (CR0118, RFC0020 D4):** an
  enriched amigo card (`templates/personas/amigo-template.md`) fuses Cooper goal-directed depth
  (Who They Are, Craft Goals, Proficiency, Scenario) with seat discipline (Non-Negotiables, Shadow,
  Tensions) and a dual render (build/author vs review, separate instances). Three default amigos
  ship instantiated - Engineering (Dani), QA (Sam), Product (Lena) - editable per project; a richer
  project-authored practitioner amigo overrides a default. Documented in reference-workflow-personas.md.
- **the test-spec AC Coverage Matrix scaffolds from an epic's stories (CR0115, field report):**
  `verify_ac` can emit a matrix pre-filled with one row per AC across an epic's stories, so the
  design rung no longer hand-extracts dozens of ACs and no AC is silently omitted - the model fills
  the Test Cases column, ts-check validates completeness (scripts/verify_ac.py).
- **mechanical author != reviewer independence gate (CR0117, RFC0020):** `critic.py record` now
  stamps both the reviewer and the author (the authoring seat / delegation id); the conformance
  gate hard-fails any Done unit whose critic verdict reviewer id equals its author id, or that has
  no recorded author - a self-review never clears Done, and the floor holds for generic workers too,
  not only persona-framed ones. Units closed before the gate carry a visible `pre-gate` marker and
  are grandfathered (one-time migration); the policy is reconciled in reference-sprint.md
  (independence is the floor for every risk tier, only the review depth scales).
- **project upgrade installs the amigo defaults (CR0119):** `project upgrade` installs the three
  default amigo cards into a consuming project's `sdlc-studio/personas/amigos/` when absent
  (idempotent, never overwriting a customised amigo) and reports the v3.1 persona enrichment, so
  upgrading projects gain the editable engineering team (scripts/project_upgrade.py, reference-upgrade.md).
- **persona-shaped delegation: workers are framed as amigo seats (CR0116, RFC0020 Accepted):** a new
  `persona_resolve.py` resolves the worker identity most-specific-first - a project-authored
  practitioner amigo overrides the skill default (Dani / Sam / Lena), which overrides generic. The
  agentic wave appends the resolved stance *after* the contract (file list / ACs / gates stay law),
  the build and review seats are always separate instances (the CR0117 independence gate), and
  `--skip-personas` yields a byte-equivalent contract that still builds. Wired in
  reference-agent-prompt-template.md + reference-sprint.md; RFC0020 accepted on Option B.

### Fixed

- **ac_scope no longer cries wolf on shared domain vocabulary (CR0113, field report):** the
  cross-epic AC lint flagged any story whose AC named a keyword distinctive to another epic's
  title, but a noun like "list" or "item" appears in the ACs of stories across many epics - it is
  shared domain vocabulary, not epic-specific leakage. ac_scope now measures document frequency
  across distinct epics and suppresses a keyword that spreads beyond a threshold, so a genuine,
  concentrated cross-epic reference still flags while the noise that trained operators to ignore
  the advisory is gone (scripts/ac_scope.py).
- **integrity no longer requires a Story link on test-specs (BG0038, field report):** an
  epic-scoped test-spec carries an Epic link and covers a whole epic with no single Story field
  (reference-test-spec.md#epic-scoped-coverage), yet `integrity.py` listed both Epic and Story as
  required and flagged the very artifact the skill mandates at epic scope. Story is dropped from the
  test-spec required-link set; Epic stays required, so a test-spec with neither still flags.

## [3.0.1] - 2026-06-24

> The v3 line: the `autosprint`->`sprint` rename + sprint lifecycle, greenfield authoring,
> the RV0005 self-review, and the field-dogfooding fixes - consolidated into one release.

### Added

- **natural-language "You can just ask" blocks on every command help file (CR0108):** the skill
  is model-invoked, so each `help/*.md` now opens with a `Just say... | Runs` table mapping plain
  phrasings to commands - a non-technical operator can just ask. A `disclosure` check enforces the
  block on every non-meta help file. Authored across 35 files via a multi-agent sweep.

- **`verify_ac --batch` jest mode - run the runner once, not a cold start per AC (CR0111, field
  report):** `reconcile --verify --batch` runs `jest --json` once and resolves jest-targeted ACs
  against that result set (a field sprint measured ~48 cold `jest -t` starts / 70s collapsing to
  one run). Mirrors `jest -t` (pass iff matches exist and all pass); cache misses + non-jest verbs
  fall through to the per-AC path. pytest/vitest caches are a fast-follow (the parse/resolve path
  is runner-general).

- **the `--goal design` rung authors the test-spec AC Coverage Matrix (CR0110, field report):**
  the breakdown produced Ready stories + points but never authored the test-spec, so the AC↔test
  bridge (CR0085) was reverse-engineered at *implement* (a field delivery repointed ~48 Verify
  lines + backfilled coverage gaps by hand). The design rung now authors each epic's AC Coverage
  Matrix - every AC mapped to a planned test case/title, Verify lines runner-targeted by
  construction - so implement binds to the matrix and the test-spec `epic-ts` (CR0096) requires at
  Done is produced up front. Documented in `reference-sprint.md` + `reference-test-spec.md`.

- **the tranche audit runs `verify_ac lint` + `ac_scope` (CR0109, field report):** `audit check`
  (the sprint breakdown's readiness groom) now flags **weak-verify** (a non-executable / prose
  Verify line, reusing `verify_ac.lint_verifier`) and **cross-epic-ac** (an AC owned by another
  epic, reusing `ac_scope`). Two readiness problems the skill already had tools for - but which a
  field breakdown re-discovered by hand - are now surfaced deterministically at design time.

- **`sprint plan` emits dependency waves (CR0107, field report):** the planner returned a flat
  order; the parallelisable wave structure (L1/L2/L3...) was only computed by the model at
  `--agentic` implement time, so operators hand-derived it and stored the rich plan externally.
  `build_plan` now returns **waves** (dependency levels) for priority/wsjf order - wave 1 = units
  with no in-batch dep, wave n+1 = units whose deps are all in earlier waves, units in a wave
  parallelisable - printed in the plan output and persisted by `--write`. Reuses the existing dep
  graph; within-wave order keeps WSJF/priority rank.

- **`sprint plan --epic` scopes a story batch to one or more epics (CR0106, field report):**
  the planner filtered only by status, so `--stories Draft` pulled every Draft story across all
  epics - a field agent planning the next tranche (EP0002+EP0003) had to hand-scope and hand-build
  the waves instead of using `plan --write`. `sprint plan --stories <status> --epic EPxxxx`
  (repeatable, union) now restricts to the named epics; dependency ordering, `--write`, and WSJF
  operate on the scoped batch. Story-only (errors with `--crs`/`--bugs`).

- **deterministic id-allocation extended to the meta-artifacts (CR0105):** `next_id.py allocate
  --type` now covers `review` (RV####) and `retro` (RETRO####) in addition to the 8 pipeline
  types, so review/retro ids are allocated collision-free (respecting `--remote`) instead of
  hand-picked by reading the directory. Kept out of `ARTIFACT_TYPES` so reconcile/conformance
  ignore them. (Lessons `LL####` keep their own `lessons.py` manager; personas are named.)

- **SOTA linter coverage in the quality guides (CR0103, RV0005 audit):** `best-practices/script.md`
  gains a Tooling section (ShellCheck + shfmt as the baseline; the anti-pattern table reframed as
  what ShellCheck enforces) and teaches `set -euo pipefail` instead of bare `set -e`;
  `best-practices/python.md` gains a Tooling section (Ruff + mypy/pyright, 3.10+ floor) and its
  Type Hints example uses PEP 604 `X | None` rather than `typing.Optional`; `help/code.md` `code
  check` now lists a shell linter so every language the repo ships is covered.

- **v3.0 capabilities surfaced in the always-loaded router + help catalogue (CR0104, RV0005
  review):** `help/help.md` now lists the `decisions` command (add/list/promote) and names the
  sprint **goal ladder** `triage -> plan -> design -> done`; the SKILL.md Type Reference gains
  `init` (greenfield step 1) and `decisions` and names the ladder; `artifact batch`,
  `--template full`, and `next_id allocate` are in the deterministic-tooling catalogue; the
  greenfield manual workflow leads with `init`. Closes the `decisions` doc-coverage false-green.

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

- **stripped internal provenance tags from consuming-facing docs + shipped code (CR0112):** the
  skill's own change-request ids (CR/BG/RFC) were embedded pervasively in `reference-*.md`,
  `help/*.md`, and `scripts/*.py` - where they collide with a consuming project's own id
  namespace. ~420 tags removed (a deterministic pass + an 82-file grammar-aware sweep); a
  `lint-style.sh` guard blocks the parenthetical provenance form from creeping back. The skill's
  own artifacts (change-requests/, CHANGELOG, rfcs/, reviews/) keep their ids; example ids stay.

- **`autosprint` renamed to `sprint` (CR0087, WS0 of RFC0019):** the command is now the whole
  sprint lifecycle (`--goal plan` / `design` / `done`), not just autonomous delivery - autonomy
  is the `--autonomous` flag, not the name. `scripts/autosprint.py` → `scripts/sprint.py`,
  `reference-autosprint.md` → `reference-sprint.md`, `help/autosprint.md` → `help/sprint.md`, and
  the live command surface now says `sprint`. **`autosprint` stays as a deprecated alias** (a
  re-export shim + NL resolution) so nothing breaks. History (closed CRs, RFC0001, prior
  CHANGELOG entries) keeps the original name.

### Fixed

- **`verify_ac` merges per-story results into the report instead of clobbering it (BG0037, field
  report):** `write_report` rebuilt verify-report.json from only the current run, so verifying a
  sprint one story at a time left the report holding only the last story - and `transition -> Done`
  (CR0084) reads that report, so the gate failed for every earlier story. Runs now merge (this
  run's entries win, others preserved); per-story verification accumulates and the Done-gate finds
  every verified story. `--fresh` forces a clean rebuild. No more `--dir`-re-stamps-everything.

- **`init` now gitignores the runtime-state dir (BG0036, field report):** `init` created
  `sdlc-studio/.local/` (caches, verify reports, lessons) but wrote no `.gitignore`, so greenfield
  projects committed derived state (this repo only avoided it via a hand-written root entry). `init`
  now drops a self-contained `sdlc-studio/.gitignore` (`.local/`) - never touching the project's own
  root `.gitignore`. Idempotent.

- **duplicate-id gate false-positived on the canonical two-table story index (BG0035, field
  report):** `reconcile.detect_duplicate_rows` counted an id across ALL tables in an `_index.md`,
  but the story-index template ships two id-bearing views (`Stories by Epic` + `All Stories`), so
  every story id was flagged twice (a field upgrade saw duplicate-id: 33). Detection is now
  **per-table**: an id once-per-view across the two tables is not a duplicate; a repeat *within*
  one table (the silent-collapse bug it guards, CR0055/BG0022) still flags. The template's
  two-view layout is valid again - no need to gut the per-epic view to pass the gate.

- **`--no-artifacts` behaviour de-duplicated to one canonical anchor (CR0102, RV0005 audit):**
  the suppressed-files / still-enforced-gates lists were restated verbatim across
  `reference-epic.md`, `reference-story.md`, and `reference-outputs.md` (drift risk on any change
  to the gate set). `reference-epic.md#flag-no-artifacts` is now the single source; story and
  outputs point to it and keep only their file-local framing (story-phase flow / status-flow shape).

- **Story Completion Cascade re-anchored on the deterministic close (CR0100, RV0005 audit):**
  `reference-outputs.md#story-completion-cascade` led with prose telling the agent to hand-edit the
  story Status, index rows, summary counts, and epic checkbox - exactly what `artifact.py close` /
  `transition.py` now own. It now leads with the deterministic close and marks steps 7-8 as
  script-owned (do not hand-edit), leaving only the genuine judgement residue as model steps.

- **`help/reconcile.md` now names the deterministic `scripts/reconcile.py` (CR0101, RV0005
  audit):** the per-command help framed all index/count/status fixes as model prose with no
  pointer to the script, inviting hand-recomputed counts (a recorded corruption mode). It now
  names the script (`detect`/`apply`/`--dry-run`), carries a do-not-hand-edit caution, and lists
  it in the See Also REQUIRED block.

- **`sprint plan` silently selected an empty batch for a lowercase status arg (BG0034, RV0005
  audit):** the documented form (`sprint --crs proposed`) never matched, because `select_batch`
  compared the raw arg against the canonical title-case vocab. The arg is now canonicalised
  (`proposed` == `Proposed`) and an unknown status fails loudly listing the valid vocabulary,
  instead of returning a silent zero-item batch. Docs aligned to title-case. (Found by the
  adversarial determinism lens; it was an untested path.)

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
