# Technical Requirements Document

**Project:** SDLC Studio
**Version:** 4.1.0
**Status:** Draft
**Last Updated:** 2026-07-14
**PRD Reference:** [PRD](./prd.md)

> Generated in **Generate mode** by reverse-engineering the skill's own source.
> This is a migration blueprint - detailed enough to rebuild SDLC Studio on a
> different agent harness. Per `reference-philosophy.md`, generated specs are not
> validated until tests run against the implementation; this TRD awaits that
> validation for its inferred claims. Confidence markers and status values are
> defined at the foot of the document. The TRD is consistent with the PRD's
> architecture section and feature inventory.

---

## 1. Executive Summary

### Purpose

Describe the technical design of SDLC Studio so it can be rebuilt on another agent
harness without access to the original author. SDLC Studio is a coding-agent skill
that drives a project from requirements to verified implementation as one governed
pipeline. It is not an application; it is a body of instruction files plus a small
deterministic Python layer that the host agent reads and runs.

### Scope

Covered: the progressive-disclosure router architecture, the split between the
markdown knowledge base and the Python script layer, the 58 scripts and their
shared library, the data architecture (markdown artifacts plus JSON state, and the
two id eras), the gate architecture, soft runtime dependencies, tool-neutral
portability, and the architectural decisions (ADRs).

Coverage: v4.1.0 as released, plus the `[Unreleased]` work on `main` (the breakdown
gate, sprint capacity, the sizing loop, the retro learning loop). The document
version tracks the product version; it is not itself a release artefact.

Not covered: the per-command process flows (these live in the `reference-*.md`
files and are the artifact behaviours, not the technical design); the content of
the templates and best-practice guides; the consuming project's own stack (that is
each project's TRD).

### Key Decisions

- Progressive-disclosure router: `SKILL.md` is the only always-loaded file; all
  detail loads on demand through a loading guide. (ADR-001)
- Determinism in scripts, judgement in the agent: side-effecting and mechanical
  work is delegated to pure-stdlib Python helpers that emit JSON; the agent
  reasons over JSON, not raw markdown. (ADR-002)
- Files are the source of truth; indexes and statuses are derived and reconciled
  from a disk census. (ADR-003)
- GitHub integration through the `gh` CLI only - no PyGitHub or token handling.
  (ADR-004)
- `AGENTS.md` is the tool-neutral instruction standard; tool-specific files point
  at it rather than duplicate it. (ADR-005)
- A gate's fire/skip decision is computed from artefact fields and config, never
  from model judgement; escapes are recorded, and an absent config blocks rather
  than disarms. (ADR-006, and its four v4 instances: ADR-007 the engagement floor,
  ADR-010 the learning loop, ADR-011 the breakdown gate)
- Artefact identity is distributed: collision-resistant short-ULID ids let
  uncoordinated writers file concurrently, with the sequential era kept valid
  forever. The entropy tail makes a same-window clash improbable, not impossible;
  a merge-time detector is the cross-machine backstop. (ADR-008)
- The engineering team is generated per project rather than shipped as a fixed
  cast. (ADR-009)

---

## 2. Project Classification

**Project Type:** sdk_library [HIGH]

**Classification Rationale:** SDLC Studio ships as an installable Agent Skill - a
directory of instruction files plus helper scripts - consumed by a host coding
agent. It has no server, no UI, and no long-running process. It is closest to a
library or SDK that the agent harness loads, so `sdk_library` fits better than
`web_application` or `api_backend`.

**Architecture Implications:**

- **Default Pattern:** layered knowledge base with a deterministic helper layer.
- **Pattern Used:** progressive-disclosure router (a lean always-loaded entry file
  plus on-demand detail) over a markdown knowledge base, with a read-only Python
  script layer for computation.
- **Deviation Rationale:** the router pattern is dictated by the token economics of
  an LLM context window - only `SKILL.md` is paid for on every invocation, so it
  must stay minimal while the rest of the corpus loads on demand. See ADR-001.

---

## 3. Architecture Overview

### System Context

The host agent harness (Claude Code, or any `AGENTS.md`-compatible tool) loads the
skill when a request matches its description. The agent parses
`/sdlc-studio [type] [action] [flags]`, reads the relevant instruction files, and
executes the workflow using its built-in tools (Read, Glob, Grep, Write, Edit,
Bash, Agent - see the `allowed-tools` line in `SKILL.md`). For mechanical or
side-effecting steps the agent shells out to the bundled Python scripts. All
durable state is plain files in the consuming repository under `sdlc-studio/`;
runtime state is JSON under `sdlc-studio/.local/` (gitignored). The only external
service is GitHub, reached through the `gh` CLI.

### Architecture Pattern

Hybrid: a progressive-disclosure instruction corpus (interpreted by the LLM) plus a
deterministic script tier (executed by the OS). [HIGH]

**Rationale:** the two tiers solve different problems. Judgement (design soundness,
drift adjudication, the five-leg review) belongs to the model; mechanical
computation (census, parsing, counting, ID allocation, drift detection) belongs to
tested code that runs the same way every time and does not cost context tokens. See
ADR-002.

### Component Overview

| Component | Responsibility | Technology |
| --- | --- | --- |
| `SKILL.md` router | Always-loaded entry point: philosophy gates, type table, Progressive Loading Guide, the Deterministic Entry Points card, pointers. ~260 lines (CI-budgeted under 500), the only file paid for every invocation. | Markdown + YAML frontmatter |
| `help/*.md` (40+ files) | Type-specific command help, prerequisites, output, examples; loaded on demand per `[type]`. | Markdown |
| `reference-*.md` (50+ files) | Step-by-step workflow detail per domain; loaded only for multi-step workflows. Each is line-budgeted. | Markdown |
| `templates/` (80+ files) | Document and code templates with `{{placeholder}}` syntax; loaded only when creating artifacts. Includes the persona/seat and stakeholder card schemas. | Markdown / text |
| `best-practices/` (~20 files) | Quality guidelines consulted before producing artifacts. | Markdown |
| `lessons/` | Cross-project lessons registry (`_index.md`, `LL{NNNN}-*.md`), ranked and printed into every sprint plan (ADR-010). | Markdown |
| `scripts/` (60+ scripts) | Deterministic Python helpers emitting JSON. The read path is read-only; a bounded, tested set writes artefacts, indexes and gate state (see §5 rule 5). | Python 3.10+ stdlib |
| `scripts/lib/` (6 modules) | Shared library. `sdlc_md.py` is the parsing core and the single source of truth for markdown conventions; `conventions.py`, `xrepo.py` and the rest carry per-domain shared logic. | Python 3.10+ stdlib |
| `scripts/tests/` (90+ modules) | Unit tests for the script layer; well over 2,500 tests at the time of writing. Exact figures are counted, not pinned here; the freshness guard checks the enumerated count only in `reviews/LATEST.md`. The repo-only `tools/` checkers have their own suite under `tools/tests/`. | `unittest` |
| `tools/` | Repo CI guards (style, links, skill frontmatter, versions, budgets, neutrality, action pins) plus the eval runner. Not part of the shipped payload. | Python / Bash |
| `install.sh` / `install.ps1` | Cross-harness installers for six targets. | Bash / PowerShell |

> **C4 Diagrams:** not generated for this brownfield extraction. Use
> `trd create --with-diagrams` or see `modules/trd/c4-diagrams.md` if formal C4
> views are wanted.

#### Progressive-disclosure loading

`SKILL.md` carries a Progressive Loading Guide: a table that maps a task type to
its primary, secondary, and decision file loads. The agent reads only the rows it
needs. Examples: "Understanding a command" loads `help/{type}.md` only; "Generate
mode workflow" loads `reference-philosophy.md#generate-mode` first, then
`help/{type}.md`, then `reference-{domain}.md`. This keeps the always-loaded
footprint near-constant regardless of how large the corpus grows - the central
scaling property of the design.

#### Markdown / Python split

| Tier | Does | Owned by |
| --- | --- | --- |
| Markdown knowledge base | Judgement: design decisions, drift adjudication, body-level edits, dashboards, the five-leg review verdict. | The agent |
| Python script tier | Determinism: census, parsing, counting, ID allocation, drift detection, AC execution, repo indexing, GitHub sync. | Tested code |

The split rule (`reference-scripts.md`): read-only helpers (`reconcile detect`,
`status`, `validate`, `next_id`, `review_prep`, `audit`, `critic brief`/`show`,
`gate`) emit JSON and the agent does the judgement; the authoring and repair helpers
(`artifact`, `file_finding`, `transition`, `reconcile apply`, `verify_ac`,
`repo_map`, `github_sync`, `plan`, `lessons`, `retro`, `archive`, `critic record`)
perform bounded, tested mutations. `critic` straddles the line: its `brief`/`show`
path is read-only, but `record`/`evidence`/`signoff` append to the committed verdict
logs. Everything else (reading files, walking directories, simple transforms) stays
with the agent's built-in tools.

#### The gate tier

A third architectural element sits over both: `gate.py` composes the deterministic
checks into **lanes**, each returning PASS / warn / FAIL, and the whole into one
exit code. The default sweep runs conformance, reconcile, index-derived, validate,
constitution, integrity, duplicate-id, provenance, doc-coverage, engagement-floor,
disclosure, doc-freshness, mutation and hook-enabled. Bound lanes attach to a
specific obligation and cannot be skipped or excluded away: `--require-retro` (the
retro's content, plus the lessons summary and validity), `--require-review` (review
currency, not presence), `--require-handoff`, and `--release`, which EXECUTES every
story's `Verify:` expression rather than reading a stored report that could carry a
stale green. The gate writes nothing, so it is hook-safe. Its lanes are the
mechanism behind ADR-006 through ADR-011: a lane is how a rule stops being prose.

---

## 4. Technology Stack

### Core Technologies

| Category | Technology | Version | Rationale |
| --- | --- | --- | --- |
| Instruction language | Markdown + YAML frontmatter | n/a | The skill is read by an LLM; markdown is the native format for agent instruction files and templates. |
| Script language | Python | 3.10+ | `str \| None` union syntax and `from **future** import annotations` are used in `lib/sdlc_md.py`; pure stdlib keeps install dependency-free. |
| Templating | `{{placeholder}}` convention | n/a | Tool-neutral, plain-text substitution the agent fills in. |
| Test framework | Python `unittest` | stdlib | No third-party test runner needed; `python3 -m unittest discover` runs the suite. |

### Build & Development

| Tool | Purpose |
| --- | --- |
| `npm run lint` (markdownlint) | Lints all markdown across the repo. |
| `python3 -m unittest discover -s scripts/tests` | Runs the script unit tests; all must pass before a release is tagged. The dev-repo suite also exercises repo-root `tools/` tests resolved by relative path, so the count and a clean pass assume the full dev checkout (the Windows installer is gated by a separate `pwsh` smoke workflow). |
| `install.sh` / `install.ps1` | Install/uninstall the skill into one or more agent targets. |

### Infrastructure Services

| Service | Provider | Purpose |
| --- | --- | --- |
| GitHub Issues | GitHub | Two-way sync of CR/Story/Epic artifacts, via the `gh` CLI only. |

No databases, no servers, no container runtime at the skill level. The consuming
project supplies whatever Verify-line tools its acceptance criteria reference.

---

## 5. API Contracts

SDLC Studio exposes no network API. Its two contracts are the agent command surface
and the script CLI surface.

### Command surface

`/sdlc-studio [type] [action] [flags]`. The router parses `type` and `action`,
loads `help/{type}.md`, and follows the matching `reference-{domain}.md` workflow.
Types: `init`, `pvd`, `prd`, `trd`, `tsd`, `persona`, `consult`, `chat`, `epic`,
`story`, `code`, `test-spec`, `test-automation`, `test-env`, `bug`, `cr`, `rfc`,
`project`, `sprint`, `handoff`, `plan`, `decisions`, `reconcile`, `gate`, `deploy`,
`mutation`, `skill-update`, `status`, `hint`, `help`. (`sprint` was named
`autosprint` before v4.0; the old name is retired.) The error-handling contract
(missing prerequisites, existing files, id collision, open questions, unknown
language) is in `SKILL.md`.

### Script CLI contract

Every script in `scripts/` obeys a fixed contract (`reference-scripts.md`):

1. `#!/usr/bin/env python3`, executable bit set.
2. `argparse` subcommands (e.g. `repo_map.py build`).
3. `--help` on every subcommand.
4. Non-zero exit on any failure that should halt the workflow.
5. Bounded, tested write surface. Read-only helpers (`reconcile detect`, `status`,
   `validate`, `next_id`, `audit`, `critic brief`/`show`) never mutate the workspace.
   The deterministic-authoring helpers DO write, each within a tested boundary:
   `artifact.py` creates artefact files and appends index rows; `file_finding.py` files
   findings; `reconcile apply` rewrites `_index.md` rows and counts; `transition.py`
   rewrites an artefact's Status and cascades the epic breakdown; `github_sync.py` writes
   the `GitHub Issue` metadata line; `verify_ac.py` rewrites the `Verified:` line;
   `migrate_v3.py` renames files and rewrites ids/links; `plan.py archive` moves plan
   files; `archive.py` relocates a type's terminal index rows into its `archive/`
   sub-index; `lessons.py add --global` writes a lesson; `decisions.py` appends to the
   decisions ledger; `retro.py` writes the batch retro artefact and the committed
   `VELOCITY.md` history row; `handoff.py` writes the handoff artefact, its index and the
   worklist; `persona_gen.py` writes the generated seat and stakeholder cards with their
   provenance stamp (ADR-009); `critic record` appends to the committed verdict, evidence
   and sign-off logs. This list names the load-bearing writers, not all of them -
   `reference-scripts.md` is the authoritative catalogue of the script write surface.
   Shared-file writes go through `sdlc_md.atomic_write` (temp-then-replace) and id
   allocation is serialised by `sdlc_md.allocation_lock`, so a crash or a concurrent
   writer never corrupts a shared file. The one deliberate exception to atomic-write is
   the append-only ledgers - `critic`'s verdict/evidence/sign-off logs, `telemetry.jsonl`
   and `verify-history.jsonl` - each grown by a single `O_APPEND` row write rather than a
   rewrite, so a torn write costs only its own last row (which `critic.read_verdicts`
   reports rather than silently drops), never the file. The scripts are NOT read-only
   over the workspace; the guarantee is that every write is tested and bounded.
6. Network access is limited to three outbound paths, each best-effort and degrading
   silently when offline: the `gh` CLI wrapper in `github_sync.py` (no token handling;
   `gh` owns auth), a direct stdlib HTTPS GET to `api.github.com` in `version_check.py`
   for the release check (`version_check.enabled` opt-out, 5s timeout), and
   `git fetch origin` in `sprint.py`'s origin-drift preflight and remote-aware id
   allocation. No other script opens a socket.
7. Plain text to stdout by default; `--format json` where machine-parseable output
   matters.
8. Unit tests under `scripts/tests/test_<script>.py`.

Invocation is always `python3 "$CLAUDE_SKILL_DIR/scripts/<name>.py" ...` from repo
root. `$CLAUDE_SKILL_DIR` is set by the harness at every install level; when unset
(another tool, or a bare shell) the agent substitutes the directory containing
`SKILL.md`. The quoted variable fails loudly when unset rather than guessing
between installed copies.

### Error / report format

Scripts that emit machine-readable output use JSON. The verifier writes a report to
`.local/verify-report.json`; reconcile emits a drift report (with drift kinds
`status-mismatch`, `missing-row`, `orphan-row`, `count-mismatch`, `missing-index`);
status emits the four-pillar census. There is no single canonical error envelope;
failures surface as a non-zero exit plus a stderr message. [MEDIUM]

**Findings carry an actionable fix (CR0025), and it must name the cause.** Each
drift item carries a `fix` string; per CR0025 a check emits remediation guidance,
not a bare finding. The contract is that the `fix` is specific enough to act on
*and* routes to the sibling tool when the diagnosis lives there - e.g. an
out-of-vocab status surfaces as a `count-mismatch` whose `fix` should name the
offending status and point at `validate` / the `status_vocab` config, not the
generic "recompute the counts" (which sends the agent to `apply`, where it cannot
be resolved). The `count-mismatch` finding does not yet meet this bar; closing it
is CR0132. A generic fix hint whose remedy is in another tool is a dead end - the
finding must be self-diagnosing. [MEDIUM]

---

## 6. Data Architecture

### Data Models

Durable state is markdown artifacts with a metadata block. The single source of
truth for parsing is `lib/sdlc_md.py`. Metadata lines take the form
`> **FieldName:** value` (the leading blockquote `>` is optional for older
artifacts). Common fields: `id`, `title`, `status`, `epic`, `story`, `created`,
`updated`. Note: the PRD describes these as YAML frontmatter; in the implementation
the metadata is parsed from `> **Name:** value` blockquote lines by
`extract_field`, with the H1 supplying the title. This is the one notable
divergence from the PRD's data-architecture wording. [HIGH]

#### Artifact type registry (`ARTIFACT_TYPES` in `lib/sdlc_md.py`)

| Type | Directory | ID prefix |
| --- | --- | --- |
| epic | `sdlc-studio/epics` | `EP` |
| story | `sdlc-studio/stories` | `US` |
| plan | `sdlc-studio/plans` | `PL` |
| bug | `sdlc-studio/bugs` | `BG` |
| cr | `sdlc-studio/change-requests` | `CR` |
| rfc | `sdlc-studio/rfcs` | `RFC` |
| issue | `sdlc-studio/issues` | `IS` |
| test-spec | `sdlc-studio/test-specs` | `TS` |
| workflow | `sdlc-studio/workflows` | `WF` |

Retro (`RETRO`), review (`RV`) and handoff (`HO`) artefacts sit outside this
registry - they are sequential-only meta artefacts created through `artifact.py`'s
`meta_new` path, with their own index files and a reconcile `meta` lane. They carry
no status/count block, which is why they need a separate lane rather than the
pipeline census.

#### Two id eras (schema v2 and v3)

Sequential ids are 4-digit zero-padded. `CR`/`RFC` display with a dash (`CR-0001`);
others do not (`US0001`). `ID_RE`, `norm_id`, and the globbing tolerate both forms
and mixed case so a file named `cr0001.md` and an index entry `CR-0001` normalise to
the same record. `id_number` extracts the numeric part.

Under `schema_version: 3` (the v4 default) new artefacts mint a short **ULID** id
instead: `US-01JQK3F8`, an 8-char Crockford-base32 suffix that is 6 timestamp chars
plus a 2-char entropy tail (`short_ulid` in `lib/sdlc_md.py`). The truncated
timestamp prefix keeps ids coarsely creation-ordered - it resolves to roughly a
17-minute bucket - and the 2 random chars are what stop two uncoordinated writers
(a human on a laptop, an agent in a container, on different git states) minting the
same id in the same bucket. The guarantee is probabilistic, not absolute: a same-
bucket clash is improbable (about 1 in 1024, the 2 base-32 chars) rather than
certain, and the allocator's directory-glob retry - it re-mints, then extends the
suffix on a persistent clash - is the single-writer local backstop, while
`allocation_lock` serialises same-process writers. What that local retry cannot see
is another machine's not-yet-merged file, so the residual cross-machine case is
caught at merge (see ADR-008). The two eras **coexist**: `migrate_v3 adopt` is
forward-only, so existing sequential ids stay valid in tickets, chat and docs, and
only new artefacts are ULIDs. Every id-consuming regex, the census, and the title
parser accept both. See ADR-008.

#### Status vocabulary (`STATUS_VOCAB`)

Each type has a closed status set; a status outside the set is a validation error
because it breaks dashboard and reconcile counting. `canonical_status` reduces a
decorated line (e.g. `Done (v2.83.0) · **CR:** CR-0088 · **Points:** 8`) to its
vocabulary token by longest-prefix match.

| Type | Allowed statuses |
| --- | --- |
| epic | Draft, Ready, Approved, In Progress, Done |
| story | Proposed, Draft, Ready, Planned, In Progress, Review, Blocked, Done, Won't Implement, Deferred, Superseded |
| plan | Draft, In Progress, Complete, Superseded |
| bug | Open, In Progress, Fixed, Verified, Closed, Won't Fix, Superseded |
| cr | Proposed, Approved, In Progress, Complete, Rejected, Deferred, Superseded, Blocked |
| rfc | Draft, In Review, Accepted, Superseded, Withdrawn |
| issue | Open, Triaging, Triaged, Resolved, Closed, Won't Fix, Superseded |
| test-spec | Draft, Ready, In Progress, Complete, Superseded |
| workflow | Created, Planning, Testing, Implementing, Verifying, Reviewing, Checking, Done, Paused, Superseded |

`Blocked` (story, cr) and `Deferred`, `Planned`, `Paused` are re-activatable, not
absorbing, so `TERMINAL_STATUS` excludes them from the archive-candidate set.

**Inbox triage lane (findings, schema v3).** Under v3 the finding types (`bug`,
`cr`, `rfc`) gain an `inbox` status prepended to their vocabulary (`INBOX_STATUS`,
`status_vocab` in `lib/sdlc_md.py`): an agent-filed finding lands in `inbox`, and a
*different* seat triages it into the workflow proper - `bug` to `Open`, `cr` to
`Approved`, `rfc` to `In Review` (`TRIAGE_TARGET`), promoting straight past the
pre-workflow `Proposed`/`Draft` proposal states an agent finding never occupies. The
lane is dormant under v2. This is distinct from the `issue` type's own intake lane
(`Open` -> `Triaging` -> `Triaged` -> `Resolved`), where an Issue is triaged into
delivery bugs.

#### Acceptance criteria

ACs are parsed two ways: a heading `### AC1: Title` (`AC_HEADING_RE`) or a compact
bullet `- **AC1:** text` (`AC_BULLET_RE`). Each AC may carry a `- **Verify:** ...`
verifier line and a `- **Verified:** yes|no|stale|manual (...)` result line, parsed
by `VERIFY_RE` / `VERIFIED_RE`. `verify_ac.py` rewrites the `Verified:` line in
place. The parser is fenced-block aware, so an illustrative `Verify:` line inside a
code block in a document is never executed.

**Only a story carries an executable verifier.** CR and bug acceptance criteria are
**prose**, and `file_finding.py` / `artifact.py` refuse a command-shaped `Verify:`
in one at creation, from a single shared authority so the two paths cannot disagree.
The reason is structural rather than stylistic: nothing executes a CR or bug AC, so
a command written into one is a claim with no runner - a wrong one is a permanent
false RED that nobody sees fail, and a loose one is a false GREEN. Both had already
happened in this workspace: one verifier grepped for an env var under the wrong
name, and one passed against unrelated prose while the feature it claimed to check
did not exist. `validate.py` warns on the ones already in a tree. The corollary for
the pipeline is that an un-decomposed CR reaches Done on prose alone, which is why
`sprint plan` flags a Large or wide-footprint CR that no story cites (ADR-011).

#### Two backlogs (dual-track: discovery feeds delivery)

Types split across two backlogs, and the split is load-bearing (`lib/sdlc_md.py`).
The **discovery** backlog is the options funnel - what someone wants or has observed,
not yet committed work: `DISCOVERY_TYPES` is `rfc`, `cr`, `issue`. Within it,
`REQUEST_TYPES` (`rfc`, `cr`) is the narrower set that `refine` decomposes into an
epic plus stories; an `issue` is `triage`d into bugs instead, so it is discovery but
not a request. The **delivery** backlog is the work itself - sized, planned and
closed on executable acceptance: `PRODUCT_TYPES` is `epic`, `story`, `bug`. (`plan`,
`test-spec` and `workflow` are process artefacts on neither.) The predicates
`is_discovery` / `is_request` are the single authority every backlog-side gate reads.

Enforcement is opt-in per project via `two_backlog.enforce` in `.config.yaml`
(`two_backlog_enforced`), defaulting OFF so an upgrading project keeps its old flow
until it opts in. When enforced, two hard gates fire: **G1**, where `sprint plan`
refuses a discovery item as a sprint unit (it has no executable ACs to close on); and
**G2**, where a request's terminal status is DERIVED from the state of the units it
produced, never asserted directly. `reconcile` additionally flags an accepted
childless request as undecomposed, and creating a CR then demands a T-shirt Size.

Decomposition is wired with two link primitives, written on both sides so the graph
resolves either way: a child names its origin with `> **Parent:** <id>` (a batch
epic from `refine --into` carries one `Parent:` line per request it delivers), and a
request lists what it became with `> **Decomposed-into:** <ids>`. `refine` (request
-> epic + stories) and `triage` (issue -> bugs) write both halves identically.
`reconcile`'s `link-asymmetry` drift kind flags a link declared on one side only, so
a half-written decomposition never certifies clean.

### Storage Strategy

| Data Type | Storage | Rationale |
| --- | --- | --- |
| Specs, epics, stories, plans, bugs, CRs, RFCs, test specs | Markdown files under `sdlc-studio/`, committed | Files are truth; reviewable in PRs; survive context resets. |
| Index registries (`_index.md` per type) | Markdown tables, committed | Derived view; reconciled from the file census, never authoritative. |
| Runtime / cache state | JSON under `sdlc-studio/.local/`, gitignored | Machine-generated, per-user, regenerable; must not pollute history. |
| Current-state anchor | `sdlc-studio/reviews/LATEST.md`, committed | Re-read after a context compaction to re-orient in one read. |

#### JSON state files (under `.local/`)

| File | Writer | Purpose |
| --- | --- | --- |
| `project-state.json` | project orchestration | Tracks `project plan` / `project implement` progress and dependency order. [MEDIUM] |
| `run-state.json` | `sprint.py` / `handoff.py` | A run's identity, batch, resolved appetite and outcome, written under a lock. The breaker reads back the ceiling the plan stamped, so plan and run cannot disagree. [HIGH] |
| `review-state.json` | review workflow | Review cadence and verdict state. [MEDIUM] |
| `review-queue.json` | review workflow | Pending review inputs. [MEDIUM] |
| `wsjf-inputs.json` | the review seats (via the plan-rung consult) | Per-unit value / time-criticality / risk-reduction / size scores feeding the WSJF order. [HIGH] |
| `telemetry.jsonl` | `telemetry.py` (via `artifact close`) | Append-only run/close events feeding the estimate-vs-actual report. `latest_actuals()` reads the last **non-null** value per field, so a bare close record after an instrumented one cannot erase the measurement. [HIGH] |
| `verify-history.jsonl` | `verify_ac.py` | Append-only per-AC verification history. [HIGH] |
| `verify-report.json` | `verify_ac.py` | Machine-readable AC verification report (per-AC pass/fail/manual). [HIGH] |
| `mutation-report.json` | `mutation.py` | Per-mutant killed / survived / error / unviable, with the git rev and a content hash per target, so a dirty tree cannot ride an old green. [HIGH] |
| `repo-map.json` | `repo_map.py` | Per-file symbols, imports, in-degree score; queried for `READ THESE FILES FIRST` lists. [HIGH] |

One measurement artefact is deliberately **committed** rather than `.local/`:
`sdlc-studio/retros/VELOCITY.md`, one row per sprint (forecast, actual, ratio,
coverage). It is a history a human reads to decide whether the forecast constants
have earned a change - not a cache, and explicitly not an auto-recalibration input
(ADR-010's honesty rule: the report stops at reporting).

### Migrations

The operator-facing surface is the `upgrade` type (`SKILL.md`'s type table points it
at `reference-upgrade.md`); its walkthrough distinguishes the three things called
"upgrade" (the skill self-update, a project's convention upgrade, and the schema
v2 -> v3 id migration). Contrary to an older claim that migration is doc-only, a
tested script layer performs it: `project_upgrade.py` migrates a consuming project's
artefacts to current conventions and, with `--apply`, performs only the safe
deterministic set (scaffold `.config.yaml` and `.version`, then reconcile drift);
`migrate_v3.py` rewrites sequential ids to short ULIDs (and converts a container's
legacy Effort/Points to a T-shirt Size under `sizing`); and `migrate.py` is the
orchestrator over all of them - it runs the pieces in order, adds an artefact-review
sweep, and emits one report split into what it upgraded deterministically and what
needs a human, auto-applying only the reversible set. Because files are truth and
indexes are reconciled, most schema drift is still repaired by `reconcile` rather
than a numbered migration, and `lib/sdlc_md.py` tolerates legacy forms (optional
blockquote, dashed and undashed IDs, mixed case) so older artifacts parse without
migration. [HIGH]

---

## 7. Integration Patterns

### External Services

| Service | Purpose | Protocol | Auth |
| --- | --- | --- | --- |
| GitHub Issues | Two-way sync of CR/Story/Epic artifacts | `gh` CLI subprocess | Inherited from `gh auth`; the skill handles no tokens |

`github_sync.py` subcommands: `pull` (fetch `sdlc:*`-labelled issues into local
files), `push` (create/update issues from local files), `cascade` (walk merged PRs
and trigger Story Completion Cascades), `state` (print sync state). All GitHub calls
route through `gh`; the logic is idempotent and unit-tested. See ADR-004.

### Event Architecture

No message queues or event bus. The nearest analogue is the **completion cascade**:
a terminal status transition on an artifact triggers updates across all linked
artifacts, indexes, dependency tables, and PRD feature statuses
(`reference-outputs.md`). The `github_sync.py cascade` subcommand extends this to
merged PRs.

### Agentic execution

`epic implement` / `project implement` fan out work to subagents via the harness's
Agent tool, bounded into waves with quality gates (`reference-agentic-lessons.md`,
`reference-agent-prompt-template.md`). Wave prompts begin from a `repo_map`-derived
file list. This is the one part of the skill flagged Claude-Code-only in the
`compatibility` frontmatter; the rest is harness-neutral.

---

## 8. Infrastructure

### Deployment Topology

The skill is copied into an agent's skills directory. There is no running service.
`install.sh` and `install.ps1` fetch the skill from the GitHub repo and install it
into one or more of six targets:

| Target | Local install directory (per `install.sh`) |
| --- | --- |
| Claude Code | `.claude/skills/sdlc-studio/` |
| Codex | `.agents/skills/sdlc-studio/` (shared with `agents`) |
| Gemini CLI | `~/.gemini/skills/sdlc-studio/` |
| opencode | `~/.config/opencode/skills/sdlc-studio/` |
| GitHub Copilot | `.github/skills/sdlc-studio/` |
| `agents` (generic) | `.agents/skills/sdlc-studio/` (shared with Codex) |

The six targets resolve to **five** distinct directories: `codex` and `agents`
both install to `.agents/skills`.

Both installers support per-target selection, `--global`/`--local`, `--uninstall`,
`--list-targets`, `--dry-run`, and a `--version` tag. The Windows installer body
lives in a function so it works both downloaded and piped via `irm ... | iex`.

The installed copy at `~/.claude/skills/sdlc-studio/` is the back-port source for
production fixes: fixes land there first, then back-port to this repo (per
`CLAUDE.md` and project memory).

### Environment Strategy

| Environment | Purpose | Characteristics |
| --- | --- | --- |
| Development | This repo; edit skill source | Lint + unit tests gate a release tag. |
| Installed (per-user) | `~/.claude/skills/sdlc-studio/` | Production fix source; back-ported here. |
| Consuming project | Any repo that installs the skill | Holds its own `sdlc-studio/` workspace and `.local/` state. |

### Scaling Strategy

Scaling is about context tokens, not machines. Progressive disclosure keeps the
always-loaded footprint near-constant (`SKILL.md` ~260 lines, CI-budgeted under 500)
however large the corpus grows. Agentic waves bound concurrency and the appetite
breaker bounds an unattended run. Read-only scripts run in well under a second; the
script suite runs 2,500+ tests in under a minute. The one deliberate exception is
`mutation.py`, which re-runs the suite once per mutant and is measured in minutes -
which is why its gate lane reads a stored report rather than executing, and reports
STALE on a rev change or an edited target rather than passing.

Distribution scales too, not just context: short-ULID identity (ADR-008) is what
lets several uncoordinated writers - human and agent, on different machines and git
states - file into one workspace without an id allocator to coordinate through. The
id is a 6+2-char suffix (6 timestamp chars, 2 entropy chars); two writers in the same
~17-minute bucket collide only if the 2-char tail also collides (about 1 in 1024),
the allocator's glob-retry is the single-writer local backstop, and the residual
cross-machine clash is caught at merge (ADR-008).

> **Container Design:** not applicable - the skill ships no containers. The
> consuming project's `test-env` type handles containerised test environments.

---

## 9. Security Considerations

### Threat Model

| Threat | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Script mutating files outside its remit | L | M | Contract rule 5: writes confined to `.local/` or named files; `plan.py archive` is the sole, bounded exception. Unit-tested. |
| Token leakage via GitHub integration | L | M | No token handling; all GitHub access via `gh`, which owns auth (ADR-004). |
| Malformed artifact crashing a script | M | L | `lib/sdlc_md.py` JSON helpers never raise (return a default); parsers tolerate legacy forms. |
| Supply-chain risk from third-party deps | L | M | Pure stdlib; no third-party packages to compromise. |
| Network exfiltration | L | H | Three outbound paths only, each degrading silently offline: `gh` (GitHub sync, owns auth), a public HTTPS GET to `api.github.com` for the release check (`version_check.enabled` opt-out), and `git fetch origin` (drift preflight, ambient git creds) - plus the consuming project's own Verify-line tools (host-bounded by `SDLC_VERIFY_HTTP_HOSTS`). See §5 rule 6. |

### Security Controls

| Control | Implementation |
| --- | --- |
| Authentication | None at skill level; GitHub sync inherits `gh auth`. |
| Authorisation | Filesystem permissions of the host; script writes are bounded and tested (see §5 rule 5), not read-only. |
| Encryption at rest | Not applicable (plain files in the consuming repo). |
| Encryption in transit | HTTPS on all three network paths: `gh` (GitHub sync), the `api.github.com` release check, and `git fetch origin` over the remote's transport. |
| Secret handling | The skill handles no secrets; secret management is the consuming project's concern, documented in its `AGENTS.md`. |

---

## 10. Performance Requirements

| Metric | Target | Measurement |
| --- | --- | --- |
| Always-loaded context | ~260 lines (`SKILL.md`), hard ceiling 500 | Line count of the router, gated by `check_budgets.py` |
| Script run time | Sub-second on a typical project | `scripts/tests` suite: 2,500+ tests in under a minute |
| Reconcile / status / gate | Sub-second | Read-only census over the artifact tree |
| Mutation run | Minutes, by design | One suite run per mutant; not on the fast path |
| Install | Single fetch-and-copy | `install.sh` / `install.ps1`, no build step |

The binding performance budget is context tokens, addressed structurally by
progressive disclosure rather than by a runtime metric.

**The cost model, and how it is recorded.** The sprint planner forecasts a batch's
token cost as `sum(Points) x the measured tokens-per-point rate`. Modified Fibonacci
points replaced the falsified file-complexity predictor (RFC0038): in a blind
re-estimation of 20 delivered units they scored **r = +0.682 pooled** (+0.782 on
units <= 8), clearing a bar fixed before the data was seen. A point measures about
25,000 tokens, flat across the bands, seeded from that study and replaced by the
project's own rate once it has enough delivered units. The forecast is **recorded at
plan time** to `retros/evidence/forecasts-*.jsonl` (`telemetry.forecasts`), stamped
with the points and the estimator rate constants that produced it, so `retro
accuracy` judges that recorded number and never re-derives one - the loop can falsify
itself. It is quoted with a band (about +/-50%) and is **never** a gate: a script
cannot observe token spend, so tokens warn while minutes and units stop a run. See §12.

---

## 11. Architecture Decision Records

### ADR-001: Progressive-disclosure router over a monolithic skill file

**Status:** Accepted

**Context:** A skill's entry file is loaded into the agent's context on every
invocation. SDLC Studio is large (52 reference files, 41 help files, many
templates and best-practice guides - see the §3 component table). A monolithic skill file would spend a
large, fixed token cost on every request regardless of the task.

**Decision:** Keep `SKILL.md` as a lean router (~260 lines, CI-budgeted under 500)
carrying only philosophy gates, the type table, the Progressive Loading Guide, the
Deterministic Entry Points card, and pointers. Everything else loads on demand via
the loading guide, which maps each task type to its primary/secondary/decision file
loads.

**Consequences:**

- Positive: always-loaded footprint stays near-constant as the corpus grows; new
  commands add a `help/` file and a guide row, not router bulk.
- Positive: the agent reads only what a task needs, lowering cost and noise.
- Negative: detail is spread across many files; contributors must keep the loading
  guide and the type tables in sync (enforced partly by `validate.py instructions`).

### ADR-002: Deterministic Python helpers emitting JSON, not agent-parsed markdown

**Status:** Accepted

**Context:** Through v1.5.0 every workflow was agent-native: the model parsed
markdown, counted artifacts, allocated IDs, and detected drift in-context. This was
non-deterministic, token-expensive, and re-derived state every session.

**Decision:** Move mechanical, high-frequency, or side-effecting work into pure-
stdlib Python scripts under `scripts/`, sharing `lib/sdlc_md.py`. Read-only helpers
emit JSON the agent consumes; the agent keeps the judgement (drift adjudication,
body edits, dashboards, the five-leg review verdict). "Determinism in scripts,
judgement in the agent."

**Consequences:**

- Positive: census, parsing, counting, ID allocation, drift detection run the same
  way every time, are covered by the script unit-test suite, and cost no context
  tokens.
- Positive: a single parsing source of truth (`lib/sdlc_md.py`) stops convention
  drift across helpers.
- Negative: adds a Python 3.10+ runtime dependency and a second language to
  maintain; a migration to another harness must port both tiers.

### ADR-003: Files are truth; reconcile from a disk census

**Status:** Accepted

**Context:** Indexes, dashboards, dependency tables, and PRD feature statuses
duplicate state that also lives in the artifacts. Agentic batch runs leave these
views stale and inconsistent.

**Decision:** Treat the artifact files on disk as the sole source of truth. Indexes
and statuses are derived. `reconcile.py` builds a census from disk and reports drift
(`status-mismatch`, `missing-row`, `orphan-row`, `count-mismatch`, `missing-index`);
the agent applies fixes and the judgement-call transitions. Doctrine adds
"ship the paperwork in the same commit as the code".

**Consequences:**

- Positive: a single reconcile pass restores consistency after any agentic run; no
  authoritative index to corrupt.
- Positive: artifacts are reviewable in PRs and survive context resets.
- Negative: derived views can lag truth between reconciles; the cadence triggers in
  `reference-reconcile.md` exist to bound that lag.

### ADR-004: `gh` CLI for GitHub, not a PyGitHub dependency

**Status:** Accepted

**Context:** Two-way Issue sync needs authenticated GitHub access. A Python client
(PyGitHub) would add a third-party dependency and require the skill to handle
tokens.

**Decision:** Route every GitHub call through the `gh` CLI as a subprocess
(`github_sync.py`). No third-party client, no token handling - `gh` owns auth.

**Consequences:**

- Positive: keeps the script layer pure stdlib; no secret management in the skill;
  sync degrades gracefully when `gh` is absent.
- Positive: idempotent, unit-testable sync logic with `gh` mocked.
- Negative: `gh` must be installed and authenticated; output-format changes in `gh`
  could require parser updates.

### ADR-005: `AGENTS.md` as the tool-neutral instruction standard

**Status:** Accepted

**Context:** The skill should run under any coding agent, not only Claude Code.
Duplicating operating instructions per tool (`CLAUDE.md`,
`.github/copilot-instructions.md`, Cursor rules) causes drift.

**Decision:** Make `AGENTS.md` the canonical, tool-neutral instruction file (read by
Codex, Copilot, Cursor, Gemini, Aider, Windsurf, Zed). Tool-specific files point at
it - Claude Code's `CLAUDE.md` imports it with `@AGENTS.md`. `init` seeds it from
`templates/agent-instructions.md`; `validate.py instructions` enforces the hygiene
(AGENTS.md canonical, CLAUDE.md a pointer, doctrine + `LATEST.md` pointers present,
pre-release gate and compaction rule present, no narrative bloat). The cross-harness
installer targets six agents.

**Consequences:**

- Positive: one source of operating truth across tools; consistent onboarding;
  portability is a first-class property.
- Negative: the agentic wave execution path remains Claude-Code-only (per the
  `compatibility` frontmatter), so full feature parity across harnesses is not yet
  reached.

### ADR-006: Deterministic triggers for hygiene gates; judgement never decides fire/skip

**Status:** Accepted

**Context:** ADR-002 moved mechanical work into scripts but left open who decides
*whether* a hygiene step runs. The N=5 benchmark (D0014,
`docs/benchmarks/2026-07-08-n5-run.md`) measured that judgement-scaled hygiene is
skipped under effort pressure: the arm free to choose skipped the pipeline and
shipped the same defect as the no-pipeline baseline in 10/10 runs, while the
mandated arm caught it in 3/5. The product thesis (gates over goodwill) applies to
the model as much as to humans.

**Decision:** For any check, review, or gate the pipeline adds, the fire/skip
decision MUST be computable from artifact fields, config, and deterministic signals
(status, Affects, difficulty band, declared paths) - never from model judgement. The
model keeps the judgement *inside* a step that has fired (what the finding is,
whether the AC matches the spec); it never decides whether the step happens. Skips
exist only as recorded operator overrides. New stories adding enforcement
(CR0194-CR0197 onward) inherit this as a design default; a judgement-gated trigger
in a design is a review finding.

**Consequences:**

- Positive: enforcement cannot decay under pressure; the gate's firing rule is
  testable; overrides leave an audit trail.
- Negative: deterministic triggers over-fire on edge cases a human would waive -
  the recorded-override path is the pressure valve, and threshold tuning becomes
  real config work.

### ADR-007: The engagement floor - a mandated planning pass on multi-file changes

**Status:** Accepted

**Context:** The pipeline's value depends on the agent engaging it. The v4 benchmark
rerun measured what actually happens when that decision is left to the model: on the
base models most teams deploy, an agent free to scale ceremony to perceived ticket
size shipped the hidden-requirement defect at the same rate as an agent with no
process at all, because it judged the ticket too small for ceremony exactly when the
ceremony would have caught the defect. Frontier models engaged unprompted. The
mandated planning pass cut escapes 4-5x for roughly 10-20% more tokens.

**Alternatives considered:**

- *Leave it to judgement* (the pre-v4 behaviour). Falsified by the measurement above:
  on the weaker half of the model population it is indistinguishable from no process.
- *Mandate the full pipeline on every change.* Rejected: a single-line fix in an
  unspecced repo does not need a spec delta, and a rule that obviously over-fires is
  a rule people disable wholesale.
- *A floor.* Below the line, mandate; above it, judgement still scales the ceremony.

**Decision:** A change touching more than one source file in a repo that carries a
numbered spec or an sdlc-studio workspace REQUIRES the planning pass before code: a
spec delta naming every existing requirement the change interacts with, and one
acceptance criterion per interaction. This is doctrine rule 16 and, where a workspace
exists, a blocking gate lane: a shipped unit that neither planned (acceptance
criteria, a `Verify:` line, or a linked plan) nor declares a real single-file
`Affects:` path is refused. The signal is a file count and a presence check - no
model call. Multi-file-ness is judged from the declared `Affects:` and cross-checked
against the source files the unit's own commit touched.

**Consequences:**

- Positive: the ceremony cannot be skipped precisely where it pays. Pure omission
  cannot dodge the floor, and understatement is caught whenever a unit's commit names
  only that unit.
- Positive: the escape is recorded, never silent - `engagement_floor: judgement` in
  config, or a `decisions waive` entry naming the rule and optionally the unit.
- Negative: git cannot attribute a file to one id among several, so understatement in
  a commit shared with another work item was a disclosed hole. It is closed by an
  opt-in `Refs: <id>` commit trailer, whose attribution is strictly additive - a "see
  also" trailer can raise a unit's file count but never lower it, so the convention
  cannot be used to disarm a unit's own check.
- Negative: adoption needs an `adopt_after:` id cutoff or the floor fails an existing
  backlog wholesale. A cutoff set beyond the current work is refused, because that
  would be a silent disarm wearing a config key's clothes.

### ADR-008: Collision-resistant short-ULID artefact ids, with the sequential era kept valid

**Status:** Accepted

**Context:** Artefact ids were sequential (`US0001`), allocated by scanning the
highest existing number. That is safe for one writer. It is not safe for several
uncoordinated ones - two agents on two machines, or a human and an agent on
divergent git states, both scan the same tree and both mint the same id. The failure
is silent until a merge, and it is the failure that stops the workspace being usable
by a real team.

**Alternatives considered:**

- *A central allocator or lock file.* Rejected: it needs a shared writable location,
  which the design deliberately does not have (files in a git repo, no service).
- *Sequential ids plus renumbering at merge.* Rejected: an id that changes is not an
  id. It has already been quoted in a ticket, a commit message and a conversation.
- *UUIDv4.* Collision-free, but unsortable and unreadable.
- *ULID.* Time-ordered prefix, Crockford base32, entropy tail.

**Decision:** Under `schema_version: 3` (the v4 default), new artefacts mint a short
ULID (`US-01JQK3F8`): an 8-char suffix of 6 timestamp chars that keep ids roughly
chronological plus a 2-char entropy tail, so two writers in the same ~17-minute
timestamp bucket collide only if that tail also collides - about 1 in 1024, rather
than certain. Existing sequential ids stay valid forever - `migrate_v3 adopt` is
FORWARD-ONLY, and the two eras coexist by design. Every id-consuming regex, the
census, and the title parser accept both.

**Consequences:**

- Positive: several human and agent writers can file concurrently, across machines and
  git states, with no coordination and no allocator.
- Positive: nothing an operator has already quoted anywhere breaks. Adoption is a
  cutoff, not a rewrite; the operator is asked, and the migration refuses without
  `--confirm`.
- Negative: ids stop being memorable and countable ("we're at CR0260" no longer works
  once the era flips). The numbering question is real enough that the upgrade walk
  presents all three answers rather than choosing for the operator.
- Negative: two id forms must be parsed forever, and a clone whose config says v2 while
  its ids are v3 is a genuine mixed-mode hazard - reconcile emits an era-divergence
  advisory for exactly that case.

**Residual risk:** the scheme is collision-resistant, not collision-free. Within one
machine the allocator's directory-glob retry sees an in-flight clash and re-mints
(extending the suffix on a persistent one), so the single-writer case is closed. It
cannot see another machine's not-yet-merged file, so the surviving case is two writers
on separate clones minting inside the same ~17-minute bucket with a colliding 2-char
tail (about 1 in 1024 per such pair). That surfaces at merge, where `next_id.py
collisions` is the guard - it flags any normalised id claimed by more than one file and
exits non-zero, so a cross-machine duplicate is caught deterministically rather than
riding into history silently.

### ADR-009: Generate the engineering team from the project, do not ship a cast

**Status:** Accepted

**Context:** v3 shipped a fixed Three Amigos cast: the same Product Owner, Engineer and
QA in every project. A fixed cast has fixed blind spots, and its objections are generic
enough to be ignored. A payments QA and a games QA are paranoid about entirely different
things, and the difference is where the value is.

**Alternatives considered:**

- *Keep the fixed cast.* Cheap, and its output is decorative.
- *Make the operator author the personas.* Correct in principle and, in practice, the
  step that never gets done.
- *Generate the cast from the project.*

**Decision:** `persona generate --team` analyses the PRD, TRD, config and repo map onto
**behavioural variables and risk axes - never demographics** - asks hard-capped
multi-choice questions only where the signals are genuinely ambiguous, and writes fresh
named individuals into `personas/seats/`: 3 core roles plus up to 2 signal-earned
extras, cast capped at 5. `--stakeholders` generates the other side of the table with
veto lines and a Cooper arbitration rule on every card (a buyer's goal never overrides
the Primary user's interface). Model judgement inside a deterministic frame:
`persona_gen.py` is a §5 rule 5 writer - it writes the cards and owns the provenance
stamp and content hash - and `validate.py seats` is the error-level floor (declared
role, review render, demographic denylist, one card per role, valid stamps).

**Consequences:**

- Positive: the objections are grounded in this project's stack, domain and risk class,
  so a seat can plausibly catch something the author would not.
- Positive: the provenance stamp plus content hash discriminate authored from generated
  cards, so an operator's edit promotes a card to authored and a re-run can never clobber
  it. A guard that cannot tell what it wrote from what a human wrote would eventually
  destroy the human's work.
- Negative: persona proliferation is the documented failure mode of the technique, so the
  cast is hard-capped and extra seats need a strong signal, not a preference.
- Negative: a generated persona is an assumption until validated. Cards keep a provisional
  label until `persona review` clears them, and `status` surfaces the count - an
  un-cleared cast is visible rather than quietly authoritative.

### ADR-010: The learning loop is a gate on the retro's CONTENT, not its existence

**Status:** Accepted

**Context:** The retro was the one ceremony the close gate blocked on, and the gate
globbed for a filename. A 0-byte `RETRO9999.md` passed it. Meanwhile the cross-project
lessons registry had no automatic reader at all: a lesson could be written down, paid for,
and written down again, without ever reaching the agent about to repeat it.

**Alternatives considered:**

- *Leave the retro as prose doctrine.* Same failure mode as judgement-gated engagement
  (ADR-006): the step gated on goodwill is the step that gets skipped.
- *Gate on the artefact's existence.* Already shipped, already falsified - satisfied by
  `touch`.
- *Gate on content and disposition, and make the store readable by machine.*

**Decision:** Doctrine rule 17. A retro is checked on its content (`retro.py validate`:
required sections, at least one real lesson, every finding dispositioned), every finding
takes a disposition - **filed** as a Bug or CR, or **declined with a reason** - and the
retro's lessons are lifted into the store (`retro extract`) that the next `sprint plan`
prints unasked, including the ranked cross-project registry a new project inherits on day
one. `lessons rank` orders by recurrence computed from citations in the files, recency,
and structural-fix demotion. Bound close-gate lanes enforce it; `lessons.loop: judgement`
makes them advisory.

**Consequences:**

- Positive: the retro produces work rather than prose, and a lesson written in one sprint
  is read in the next by a mechanism rather than by remembering to look.
- Positive: filing and declining are **both green**. This is load-bearing - if declining
  cost more than filing, the gate would teach people to file rubbish to go green. What is
  refused is silence: a finding written down and left to rot.
- Positive: a ceremony gate needs a deterministic tool to interrogate, or it can only ask
  the filesystem. The tell that a gate is about to be forgeable is that no script produces
  or validates the artefact it gates on.
- Negative: the default is mandated on ADR-006's *reasoning*, not yet on ADR-006's
  *evidence*. The claim that closing the loop reduces repeat defects is **registered as a
  claim to be measured, not asserted as a finding**, and that distinction is kept
  explicitly rather than quietly elided.

### ADR-011: The breakdown gate lives in `plan`, the command people actually run

**Status:** Accepted

**Context:** The `--goal design` rung has been specified for months to produce a
reviewable, estimated backlog. It has never once been invoked. Backlogs reach `sprint plan`
ungroomed, and the planner produced a plan anyway: a flat token forecast over unsized
units, a wave that claimed two units were parallel when both rewrote the same file, and a
Large CR that no story would ever gate on an executable acceptance criterion. Each looked
exactly like a real plan.

**Alternatives considered:**

- *Keep grooming as a separate step and ask harder.* This is the thing that has already
  failed, for months, in this repository.
- *Warn at plan time.* An advisory lane is the lane that gets scrolled past, and the plan
  would still print - so the false authority would still be produced.
- *Refuse.*

**Decision:** A unit is **groomed** only when it declares both the files it will touch
(`Affects:`) and a size: a story/bug by `Points:`, a CR/RFC/epic by a T-shirt `Size:`.
With any ungroomed unit in the batch, `sprint plan` exits non-zero and prints **no plan at
all**, naming each offending unit, what it lacks, and the command that fixes it. The
planner additionally derives shared-file clusters from the `Affects:` it already parses, so
a declared dependency is no longer the only way to see a collision. `sprint.breakdown:
judgement` downgrades the lane to a report; an absent config BLOCKS and an unknown mode
falls back to enforce.

**Consequences:**

- Positive: a plan is never false authority over work nobody has sized. Enforcement sits in
  the command that is actually invoked, which is the only place enforcement survives.
- Positive: a shared file is a fact where a `Depends on:` edge is only a declaration. On its
  first run the cluster check caught two false-parallel pairs in this repo's own backlog,
  one of which was the change that introduced it.
- Negative: the gate refuses real work on day one. Its first run refused three bugs filed
  the same day by this project's own filer, because the filer has no flag to record
  `Affects:` - when two tools judge the same artefact they must agree on what a complete one
  is, and here they did not.
- Negative: some work genuinely cannot be sized before it is investigated. That case is a
  recorded config decision, not an exception the planner infers for itself.

---

## 12. Open Technical Questions

- [ ] **Q:** Should the markdown command flows get executable conformance tests, or
  is the script suite plus `reconcile`/`validate` a sufficient oracle?
  **Context:** the markdown layer's behaviour is currently validated by use, not by
  tests - the main generate-mode validation gap.
- [ ] **Q:** Should metadata move to true YAML frontmatter to match the PRD's
  wording, or stay as `> **Name:** value` blockquote lines that `lib/sdlc_md.py`
  already parses?
  **Context:** the divergence is cosmetic today but matters for any harness that
  expects frontmatter.
- [ ] **Q:** What is the porting path for the Claude-Code-only agentic wave
  execution to other `AGENTS.md` harnesses?
  **Context:** it is the only non-neutral feature.
- [x] **Q:** Is there a plan-time predictor of delivery cost at all? **Resolved
  (RFC0038).** The file-complexity predictor was falsified out-of-sample (0.55x); its
  replacement, modified Fibonacci points, cleared a pre-registered bar in a blind
  re-estimation of 20 delivered units (r = +0.682 pooled, +0.782 on units <= 8). The
  shipped forecast is `sum(Points) x the measured tokens-per-point rate`, recorded when
  the plan is made (not re-derived at retro time), so the loop is now falsifiable.
- [ ] **Q:** Should the meta artefacts (retro, review, handoff) join `ARTIFACT_TYPES`?
  **Context:** they are sequential-only, carry no status block, and need a separate
  reconcile lane precisely because they sit outside the registry. Folding them in
  would unify the census at the cost of making the status/count block optional
  everywhere.

---

## 13. Implementation Constraints

### Must Have

- `SKILL.md` stays lean (router only); detail loads on demand.
- Scripts stay pure stdlib, Python 3.10+; every workspace write is bounded and tested
  (§5 rule 5), going through `atomic_write` for shared files.
- Every script has unit tests; `gate.py --release` passes before a release is tagged.
- `lib/sdlc_md.py` remains the single source of truth for markdown conventions; a
  second module re-hardcoding the status vocabulary or the id grammar is a defect, not
  a convenience.
- GitHub access only via `gh`; no token handling, no third-party client.
- `AGENTS.md` canonical; tool-specific files point at it.
- Every new gate obeys ADR-006: the fire/skip decision is computable from artefact
  fields, config and deterministic signals. A judgement-gated trigger in a design is a
  review finding.
- A gate asserts on **content**, never on an artefact's existence, and degrades
  honestly: a surface a checker cannot handle is reported un-checked, never passed.

### Won't Have (This Version)

- A network service, UI, or database.
- A required third-party Python dependency (PyYAML is used when present and degrades to
  the caller's default when absent).
- Executable conformance tests for the markdown command flows (the eval scenarios are a
  partial stand-in, not a replacement).
- Full agentic-wave parity outside Claude Code.
- A token budget that gates. A script cannot observe token spend, so a self-reported
  number could never be a breaker; tokens warn, minutes and units stop the run.
- Auto-refitting of the estimator's fitted constants from the velocity history. Curve-
  fitting a handful of sprints fits noise and dresses it as evidence; a human reads the
  trend and decides. (This is distinct from what the shipped loop DOES do: once a project
  has enough delivered units it replaces the seeded tokens-per-point rate with its own
  measured rate, recomputed per plan - an average of measured points, not a refit.)

---

## Changelog

| Date | Version | Changes |
| --- | --- | --- |
| 2026-06-20 | 2.0.0 | Brownfield extraction of TRD from skill source (Generate mode) |
| 2026-07-06 | 4.0.0 | Refresh to the shipped script layer: corrected the write contract (§5 rule 5 - the script write surface is bounded and tested, not absent), component counts, state-file inventory, and test figures. The `doc-freshness` guard checks only `reviews/LATEST.md`, and only the facts it states there (version, the enumerated `N script tests` count, disclosure count) - it is advisory and does not pin this document's component counts, which is why they are now stated as growth-tolerant bands rather than exact figures |
| 2026-07-14 | 4.1.0 | The v4 architecture: the gate tier (§3), the two id eras (§6), story-only executable verifiers (§6), the run/appetite and measurement state files (§6), the falsified cost model (§10), and five new ADRs - ADR-007 the engagement floor, ADR-008 ULID identity, ADR-009 the generated team, ADR-010 the learning loop, ADR-011 the breakdown gate. Corrected the component counts, the router's line figure (~195 was stale; it is ~260) and the test count |

---

> **Confidence Markers:** [HIGH] clear from code | [MEDIUM] inferred from patterns | [LOW] speculative
>
> **Status Values:** Draft | Approved (document); Proposed | Accepted | Deprecated | Superseded (ADRs)
