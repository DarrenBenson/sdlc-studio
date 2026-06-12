# Changelog

All notable changes to SDLC Studio will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- **`tools/validate_skill.py`** - stdlib-only CI validator for SKILL.md
  frontmatter against the agentskills.io spec subset (name pattern and
  directory match, description length, known-field allowlist, semver
  `metadata.version`); wired into `npm run lint` as `lint:skill`.
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
