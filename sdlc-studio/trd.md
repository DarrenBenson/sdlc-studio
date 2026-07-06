# Technical Requirements Document

**Project:** SDLC Studio
**Version:** 4.0.0
**Status:** Draft
**Last Updated:** 2026-07-06
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
markdown knowledge base and the Python script layer, the 40+ scripts and their
shared library, the data architecture (markdown artifacts plus JSON state), soft
runtime dependencies, tool-neutral portability, and the architectural decisions
(ADRs).

Not covered: the per-command process flows (these live in the `reference-*.md`
files and are the artifact behaviours, not the technical design); the content of
the templates and best-practice guides; the consuming project's own stack (that is
each project's TRD).

### Key Decisions

- Progressive-disclosure router: `SKILL.md` is the only always-loaded file; all
  detail loads on demand through a loading guide.
- Determinism in scripts, judgement in the agent: side-effecting and mechanical
  work is delegated to pure-stdlib Python helpers that emit JSON; the agent
  reasons over JSON, not raw markdown.
- Files are the source of truth; indexes and statuses are derived and reconciled
  from a disk census.
- GitHub integration through the `gh` CLI only - no PyGitHub or token handling.
- `AGENTS.md` is the tool-neutral instruction standard; tool-specific files point
  at it rather than duplicate it.

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
| `SKILL.md` router | Always-loaded entry point: philosophy gates, type table, Progressive Loading Guide, pointers. ~195 lines, the only file paid for every invocation. | Markdown + YAML frontmatter |
| `help/*.md` (31 files) | Type-specific command help, prerequisites, output, examples; loaded on demand per `[type]`. | Markdown |
| `reference-*.md` (42 files) | Step-by-step workflow detail per domain; loaded only for multi-step workflows. | Markdown |
| `templates/` (72 files) | Document and code templates with `{{placeholder}}` syntax; loaded only when creating artifacts. | Markdown / text |
| `best-practices/` (19 files) | Quality guidelines consulted before producing artifacts. | Markdown |
| `lessons/` | Cross-project lessons registry (`_index.md`, `LL{NNNN}-*.md`), recalled before substantive decisions. | Markdown |
| `scripts/` (40+ scripts) | Deterministic Python helpers emitting JSON. Most are read-only; a bounded set writes artefacts and indexes (see §5 rule 5). | Python 3.10+ stdlib |
| `scripts/lib/sdlc_md.py` | Shared parsing/utility library; single source of truth for markdown conventions. | Python 3.10+ stdlib |
| `scripts/tests/` | Unit tests for the script layer (the dev-repo suite also covers repo-root `tools/`, so the exact count varies with checkout layout). | `unittest` |
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

The split rule (`reference-scripts.md`): read-only helpers (`reconcile`, `status`,
`validate`, `next_id`, `review_prep`) emit JSON and the agent does the judgement;
the side-effecting helpers (`repo_map`, `verify_ac`, `github_sync`, `plan`,
`lessons`) perform bounded, tested mutations. Everything else (reading files,
walking directories, simple transforms) stays with the agent's built-in tools.

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
Types: `prd`, `trd`, `tsd`, `persona`, `consult`, `chat`, `epic`, `story`, `code`,
`test-spec`, `test-automation`, `test-env`, `bug`, `cr`, `rfc`, `project`, `plan`,
`reconcile`, `status`, `hint`, `help`. The error-handling contract (missing
prerequisites, existing files, ID collision, open questions, unknown language) is
in `SKILL.md`.

### Script CLI contract

Every script in `scripts/` obeys a fixed contract (`reference-scripts.md`):

1. `#!/usr/bin/env python3`, executable bit set.
2. `argparse` subcommands (e.g. `repo_map.py build`).
3. `--help` on every subcommand.
4. Non-zero exit on any failure that should halt the workflow.
5. Bounded, tested write surface. Read-only helpers (`reconcile detect`, `status`,
   `validate`, `next_id`, `audit`, `critic`) never mutate the workspace. The
   deterministic-authoring helpers DO write, each within a tested boundary: `artifact.py`
   creates artefact files and appends index rows; `file_finding.py` files findings;
   `reconcile apply` rewrites `_index.md` rows and counts; `transition.py` rewrites an
   artefact's Status and cascades the epic breakdown; `github_sync.py` writes the
   `GitHub Issue` metadata line; `verify_ac.py` rewrites the `Verified:` line; `migrate_v3.py`
   renames files and rewrites ids/links; `plan.py archive` moves plan files; `lessons.py add
   --global` writes a lesson. Shared-file writes go through `sdlc_md.atomic_write`
   (temp-then-replace) and id allocation is serialised by `sdlc_md.allocation_lock`, so a
   crash or a concurrent writer never corrupts a shared file. The scripts are NOT read-only
   over the workspace; the guarantee is that every write is tested and bounded.
6. No network access except the `gh` CLI wrapper in `github_sync.py` (no token
   handling).
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
| test-spec | `sdlc-studio/test-specs` | `TS` |
| workflow | `sdlc-studio/workflows` | `WF` |

IDs are 4-digit zero-padded. `CR`/`RFC` display with a dash (`CR-0001`); others do
not (`US0001`). `ID_RE`, `norm_id`, and the globbing tolerate both forms and mixed
case so a file named `cr0001.md` and an index entry `CR-0001` normalise to the same
record. `id_number` extracts the numeric part.

#### Status vocabulary (`STATUS_VOCAB`)

Each type has a closed status set; a status outside the set is a validation error
because it breaks dashboard and reconcile counting. `canonical_status` reduces a
decorated line (e.g. `Done (v2.83.0) · **CR:** CR-0088 · **Points:** 8`) to its
vocabulary token by longest-prefix match.

| Type | Allowed statuses |
| --- | --- |
| epic | Draft, Ready, Approved, In Progress, Done |
| story | Proposed, Draft, Ready, Planned, In Progress, Review, Done, Won't Implement, Deferred, Superseded |
| plan | Draft, In Progress, Complete, Superseded |
| bug | Open, In Progress, Fixed, Verified, Closed, Won't Fix, Superseded |
| cr | Proposed, Approved, In Progress, Complete, Rejected, Deferred, Superseded, Blocked |
| rfc | Draft, In Review, Accepted, Superseded, Withdrawn |
| test-spec | Draft, Ready, In Progress, Complete, Superseded |
| workflow | Created, Planning, Testing, Implementing, Verifying, Reviewing, Checking, Done, Paused, Superseded |

#### Acceptance criteria

ACs are parsed two ways: a heading `### AC1: Title` (`AC_HEADING_RE`) or a compact
bullet `- **AC1:** text` (`AC_BULLET_RE`). Each AC may carry a `- **Verify:** ...`
verifier line and a `- **Verified:** yes|no|stale|manual (...)` result line, parsed
by `VERIFY_RE` / `VERIFIED_RE`. `verify_ac.py` rewrites the `Verified:` line in
place.

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
| `review-state.json` | review workflow | Review cadence and verdict state. [MEDIUM] |
| `review-queue.json` | review workflow | Pending review inputs. [MEDIUM] |
| `telemetry.jsonl` | `telemetry.py` (via `artifact close`) | Append-only run/close events feeding estimate calibration. [HIGH] |
| `verify-history.jsonl` | `verify_ac.py` | Append-only per-AC verification history. [HIGH] |
| `verify-report.json` | `verify_ac.py` | Machine-readable AC verification report (per-AC pass/fail/manual). [HIGH] |
| `repo-map.json` | `repo_map.py` | Per-file symbols, imports, in-degree score; queried for `READ THESE FILES FIRST` lists. [HIGH] |

### Migrations

Schema migration between skill versions is handled by `reference-upgrade.md`
(the `upgrade` type), not by the script layer. Because files are truth and indexes
are reconciled, most schema drift is repaired by `reconcile` rather than a numbered
migration. `lib/sdlc_md.py` tolerates legacy forms (optional blockquote, dashed and
undashed IDs, mixed case) so older artifacts parse without migration. [HIGH]

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
always-loaded footprint near-constant (`SKILL.md` ~195 lines) however large the
corpus grows. Agentic waves bound concurrency. Read-only scripts run in well under a
second (the script suite runs 1000+ tests in a few seconds).

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
| Network exfiltration | L | H | No network calls except `gh` and the consuming project's own Verify-line tools. |

### Security Controls

| Control | Implementation |
| --- | --- |
| Authentication | None at skill level; GitHub sync inherits `gh auth`. |
| Authorisation | Filesystem permissions of the host; script writes are bounded and tested (see §5 rule 5), not read-only. |
| Encryption at rest | Not applicable (plain files in the consuming repo). |
| Encryption in transit | Delegated to `gh` (HTTPS) for the only network path. |
| Secret handling | The skill handles no secrets; secret management is the consuming project's concern, documented in its `AGENTS.md`. |

---

## 10. Performance Requirements

| Metric | Target | Measurement |
| --- | --- | --- |
| Always-loaded context | ~195 lines (`SKILL.md`) | Line count of the router |
| Script run time | Sub-second on a typical project | `scripts/tests` suite: 1000+ tests in a few seconds |
| Reconcile / status | Sub-second | Read-only census over the artifact tree |
| Install | Single fetch-and-copy | `install.sh` / `install.ps1`, no build step |

The binding performance budget is context tokens, addressed structurally by
progressive disclosure rather than by a runtime metric.

---

## 11. Architecture Decision Records

### ADR-001: Progressive-disclosure router over a monolithic skill file

**Status:** Accepted

**Context:** A skill's entry file is loaded into the agent's context on every
invocation. SDLC Studio is large (46 reference files, 39 help files, many
templates and best-practice guides - see the §3 component table). A monolithic skill file would spend a
large, fixed token cost on every request regardless of the task.

**Decision:** Keep `SKILL.md` as a lean router (~195 lines) carrying only
philosophy gates, the type table, the Progressive Loading Guide, and pointers.
Everything else loads on demand via the loading guide, which maps each task type to
its primary/secondary/decision file loads.

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

---

## 13. Implementation Constraints

### Must Have

- `SKILL.md` stays lean (router only); detail loads on demand.
- Scripts stay pure stdlib, Python 3.10+; every workspace write is bounded and tested
  (§5 rule 5), going through `atomic_write` for shared files.
- Every script has unit tests; all tests pass before a release is tagged.
- `lib/sdlc_md.py` remains the single source of truth for markdown conventions.
- GitHub access only via `gh`; no token handling, no third-party client.
- `AGENTS.md` canonical; tool-specific files point at it.

### Won't Have (This Version)

- A network service, UI, or database.
- A third-party Python dependency.
- Executable conformance tests for the markdown command flows.
- Full agentic-wave parity outside Claude Code.

---

## Changelog

| Date | Version | Changes |
| --- | --- | --- |
| 2026-06-20 | 2.0.0 | Brownfield extraction of TRD from skill source (Generate mode) |
| 2026-07-06 | 4.0.0 | Refresh to the shipped script layer: corrected the write contract (§5 rule 5 - the script write surface is bounded and tested, not absent), component counts, state-file inventory, and test figures; a freshness guard now prevents the stale claims recurring |

---

> **Confidence Markers:** [HIGH] clear from code | [MEDIUM] inferred from patterns | [LOW] speculative
>
> **Status Values:** Draft | Approved (document); Proposed | Accepted | Deprecated | Superseded (ADRs)
