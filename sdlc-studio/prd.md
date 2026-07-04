# Product Requirements Document

**Project:** SDLC Studio
**Version:** 2.0.0
**Last Updated:** 2026-06-20
**Status:** Generated (brownfield extraction - awaiting test validation)

> Generated in **Generate mode** by reverse-engineering the skill's own source.
> This is a migration blueprint: detailed enough to rebuild SDLC Studio on a
> different harness. Per `reference-philosophy.md`, features are not "Done" until
> tests validate the spec against the implementation. Confidence markers and
> status values are defined at the foot of this document.

---

## Mission

SDLC Studio takes a deliberate position against the prevailing direction of AI
coding tools. A wave of frameworks is inventing new, AI-native ways to deliver
software: fresh artifact formats, fresh ceremonies, fresh vocabularies for the
model to follow. We did the opposite. Software engineering already worked out how
to ship software that survives contact with reality - clear requirements,
acceptance criteria, traceability from intent to code, change control, and a
definition of done that means done. Those practices are not dated; they are the
part of two decades of agile and DevOps practice that earned its place. Teams
quietly dropped them not because they were wrong, but because maintaining them by
hand was expensive, so specifications went stale and the discipline lapsed. That
economics has changed. An agent can now author the requirements, keep them
current, and prove the code against them, with acceptance criteria as a
machine-checkable oracle and continuous reconciliation keeping every artifact
true to what was built. SDLC Studio wraps an agentic system around the proven
lifecycle rather than replacing it: the agent carries the cost of the ceremony,
and the discipline stays.

This is also why the lifecycle maps so cleanly onto what the field now calls loop
engineering. An agent is a model running in a loop that cannot reliably judge its
own exit condition; the software lifecycle has always been that loop - specify,
build, validate against the specification, reconcile, change, repeat - with
acceptance criteria as the test that closes it. The current wave of spec-driven
and eval-driven tooling is rediscovering, one piece at a time, a cycle the SDLC
described in full long ago. SDLC Studio treats the lifecycle as the loop and
acceptance criteria as the oracle, which is what makes a fully autonomous
delivery loop (see RFC-0001) a natural next step rather than a new invention.

We call the resulting discipline **Goal-Driven Development**: the human sets the
goal and acceptance criteria, the agent drives the lifecycle to them (the lineage
Test-Driven -> Behaviour-Driven -> Eval-Driven -> Goal-Driven). The `autosprint`
command is its executable form - `autosprint <batch> --goal done` - and every run
closes with a reconcile and review.

---

## 1. Project Overview

### Product Name

SDLC Studio - a Claude Code skill for managing the full software development
lifecycle.

### Purpose

SDLC Studio does not invent a new way to build software with AI. It takes the
practices software teams have proven over two decades of agile and DevOps -
requirements, acceptance criteria, traceability, change control, a real
definition of done - and builds an agentic system that executes them, using
machine-checkable acceptance criteria and continuous reconciliation to keep every
artifact true to the code. The agent carries the cost of the discipline; the
discipline stays.

### Tech Stack

- **Markdown** – the skill is a progressive-disclosure set of instruction files
  (`SKILL.md` router + 42 `reference-*.md` + 31 `help/*.md` + 72 templates + 19
  best-practice guides). No runtime beyond the agent reading them.
- **Python 3.10+ (stdlib only)** – 10 deterministic helper scripts under
  `scripts/`, sharing `lib/sdlc_md.py`. Pure stdlib; no third-party packages.
- **Soft runtime deps** – `gh` CLI (sync), `pytest`/`jest`/`vitest`/`go`/`curl`/
  `jq`/`rg` (whichever a project's AC Verify lines invoke).

### Architecture Pattern

Progressive-disclosure router. `SKILL.md` is the only always-loaded file; all
detail is loaded on demand via a loading guide. Deterministic, side-effect-bearing
work (ID allocation, drift detection, AC verification, repo indexing, GitHub sync)
is delegated to Python scripts so the agent reasons over JSON, not raw files. See
the TRD for the full architecture.

---

## 2. Problem Statement

### Problem Being Solved

AI-assisted delivery drifts: specs and code diverge, statuses go stale, IDs
collide, acceptance criteria are vague, and agentic batch runs leave artifacts
inconsistent. SDLC Studio imposes a governed lifecycle with machine-checkable
acceptance criteria, census-based drift detection, and completion cascades so the
paperwork stays true to the code without manual bookkeeping.

### Target Users

The orchestrator/operator running delivery, the developer of a consuming project,
the AI agent executing the skill, and the skill maintainer. See
`sdlc-studio/personas.md`.

### Context

Distributed as a skill installed to `.claude/skills/sdlc-studio/`. This repo is
the skill's own source; the installed copy at `~/.claude/skills/sdlc-studio/` is
the back-port source for production fixes (see `CLAUDE.md`). Tool-neutral by
design: `AGENTS.md` is the cross-tool instruction standard, with `CLAUDE.md`
importing it.

---

## 3. Feature Inventory

Status: all features **Complete** at v2.0.0 (the skill is in production use).
Confidence **[HIGH]** unless noted – extracted directly from source. The Epic
column maps each feature to its owning epic (see `sdlc-studio/epics/`).

> **Complete vs Ready:** these statuses describe the *implementation* - the
> features ship and work. The generated spec that documents them is tracked
> separately at epic and story level as **Ready** (awaiting test validation per
> `reference-philosophy.md`), so a feature can be Complete in code while its
> extracted spec is not yet Done.
>
> **Location column:** each entry names the reference/help doc and the
> deterministic script that *backs* the command. The script is the read-only or
> analytical core; orchestration - applying reconcile auto-fixes, the `--verify`
> delegation, the review CODE leg and cadence, the `status --full` render - is
> performed by the skill command around the script. See the EP0005 stories for
> exact per-script scope.

| Feature | Description | Status | Priority | Location | Epic |
| --- | --- | --- | --- | --- | --- |
| PRD (create/generate) | Author or reverse-engineer requirements | Complete | High | help/prd.md, reference-prd.md | EP0001 |
| TRD (create/generate) | Technical architecture, ADRs, optional modules | Complete | High | help/trd.md, templates/modules/trd | EP0001 |
| TSD | Project-level test strategy | Complete | Medium | help/tsd.md | EP0001 |
| Personas (create/generate) | User personas, inferred from code in generate mode | Complete | Medium | reference-persona-generate.md | EP0001 |
| Consult / Chat | Persona consultation + Three Amigos pressure-test | Complete | Medium | reference-consult.md, reference-workflow-personas.md | EP0001 |
| Epic decomposition | Group PRD features into epics, perspectives | Complete | High | reference-epic.md | EP0002 |
| Story generation | Stories with implementation-ready AC (create + `generate`) | Complete | High | reference-story.md | EP0002 |
| Change Requests | Post-PRD change lifecycle, `cr action`, `cr sync` | Complete | High | reference-cr.md | EP0006 |
| RFCs | Design exploration of unsettled space, spawns CRs | Complete | Medium | reference-rfc.md | EP0006 |
| Bug tracking | Bug lifecycle with traceability + hypothesis discipline | Complete | High | reference-bug.md | EP0006 |
| Code plan | Implementation plan for a story | Complete | High | reference-code.md | EP0003 |
| Code implement | Execute a plan (TDD-gated) | Complete | High | reference-code.md | EP0003 |
| Plan-file lifecycle | Claude Code plan files: list/archive | Complete | Low | reference-plan-files.md, scripts/plan.py | EP0003 |
| Test spec | Consolidated plan + cases + fixtures | Complete | High | reference-test-spec.md | EP0004 |
| Test automation | Generate executable tests | Complete | High | help/test-automation.md | EP0004 |
| Test environment | Containerised test env setup | Complete | Low | help/test-env.md | EP0004 |
| Reconcile | Census-based drift detection + auto-fix; `--verify` | Complete | High | reference-reconcile.md, scripts/reconcile.py | EP0005 |
| Verify AC | Executable AC verifier DSL | Complete | High | reference-verify.md, scripts/verify_ac.py | EP0005 |
| Review | Unified PRD/TRD/TSD/Persona + CODE review, cadence | Complete | High | reference-review.md, scripts/review_prep.py | EP0005 |
| Status / Hint | Pipeline dashboard + single next step | Complete | High | help/status.md, scripts/status.py | EP0005 |
| Project orchestration | `project plan` / `project implement`, dependency order | Complete | High | reference-project.md | EP0007 |
| Epic implement (agentic) | Wave analysis + subagent fan-out, quality gates | Complete | High | reference-epic.md, reference-agentic-lessons.md | EP0007 |
| Repo map | AST repo indexer (stdlib), ranks files for a story | Complete | Medium | reference-repo-map.md, scripts/repo_map.py | EP0008 |
| GitHub sync | Two-way Issues sync via `gh` (CR/story/epic) | Complete | Medium | reference-github-sync.md, scripts/github_sync.py | EP0008 |
| ID allocation | Deterministic next-id, cross-repo aware | Complete | High | scripts/next_id.py | EP0008 |
| Validate | Skill + instructions hygiene checks | Complete | Medium | scripts/validate.py | EP0008 |
| Lessons registry | Cross-project lessons-learned, recall before decisions | Complete | Medium | lessons/, scripts/lessons.py | EP0009 |
| Init / Onboarding | Project config + doctrine onboarding + agent-instructions seed | Complete | High | help/init.md, reference-doctrine.md | EP0009 |
| Operator heuristics | Live-service patterns, deploy readiness, release gate | Complete | Medium | reference-operator-heuristics.md, reference-deploy-readiness.md | EP0009 |
| Upgrade | Schema migration between versions | Complete | Low | reference-upgrade.md | EP0008 |
| Cross-tool portability | AGENTS.md standard, cross-harness installer | Complete | High | templates/agent-instructions.md, install scripts | EP0009 |

### Feature Details (representative)

#### Reconcile (census-based drift detection)

**User Story:** As an orchestrator, I want drift between artifacts and code fixed
in one pass so dashboards and statuses stay true after agentic runs.

**Acceptance Criteria:**

- [ ] Builds a census of all artifacts from disk (files are truth), not from indexes.
- [ ] Detects status drift, stale index rows, unticked cascade checkboxes, broken dependency-table statuses.
- [ ] `--scope` limits to a subset (e.g. `stories,epics`); `--verify` delegates to `verify_ac.py`.
- [ ] Auto-fixes mechanical drift; reports judgement-call items without auto-transitioning.

**Dependencies:** scripts/reconcile.py, lib/sdlc_md.py
**Status:** Complete · **Confidence:** [HIGH]

#### Verify AC (executable acceptance-criteria verifier)

**User Story:** As an agent closing a story, I want acceptance criteria checked
against the running code so "Done" means verified, not asserted.

**Acceptance Criteria:**

- [ ] Parses `Verify:` lines in story AC into executable checks.
- [ ] Runs each check; reports `Verified: yes/no` per AC with pass/fail/manual counts.
- [ ] Supports a verify gate (`require_ac_verification`) that aborts the completion cascade on failure.
- [ ] Writes a machine-readable report to `.local/verify-report.json`.

**Dependencies:** scripts/verify_ac.py
**Status:** Complete · **Confidence:** [HIGH]

> The remaining features follow the same shape. Implementation-ready AC for each
> is extracted at the **story** layer (`story generate`), not duplicated here.

---

## 4. Functional Requirements

### Core Behaviours

- A single router (`SKILL.md`) parses `[type] [action]`, loads the matching
  `help/{type}.md`, and follows the referenced `reference-{domain}.md` workflow.
- Generate mode produces migration-blueprint specs validated by tests; create
  mode authors forward-looking specs interactively.
- Every numbered artifact has a 4-digit zero-padded ID, an `_index.md` registry,
  blockquote metadata headers (`> **Field:** value`), and a canonical status
  vocabulary.
- Terminal status transitions trigger completion cascades that update all linked
  artifacts, indexes, dependency tables, and PRD feature statuses.

### Input/Output Specifications

- **Input:** `/sdlc-studio [type] [action] [flags]`, plus the project's own code
  and existing artifacts.
- **Output:** Markdown artifacts under `sdlc-studio/`, JSON state under
  `sdlc-studio/.local/`, and structured stdout from scripts.

### Business Logic Rules

- Files are the source of truth; indexes are derived and reconciled from a census.
- IDs never change once assigned; collisions auto-increment.
- "Done" requires verification (tests pass) in generate mode.
- Ship the paperwork in the same commit as the code (doctrine).

---

## 5. Non-Functional Requirements

### Performance

Scripts are pure stdlib. Read-path scripts (status, repo map, next-id,
review_prep) are read-only over the workspace; reconcile and verify_ac perform
bounded, opt-in writes (auto-fixes and `Verified:` back-annotation
respectively). reconcile/status run in well under a second on a typical project
(observed in normal use, not a gated benchmark).

### Security

No network calls except `gh` (GitHub sync) and the tools a project's Verify lines
invoke. No secrets handled by the skill; secret handling is the consuming
project's concern (documented in its AGENTS.md).

### Scalability

Progressive disclosure keeps always-loaded context minimal (SKILL.md ~195 lines)
regardless of total skill size. Agentic waves bound concurrency.

### Availability

Offline-capable: the core pipeline needs no network. Sync and remote-ID checks
degrade gracefully when `gh`/remotes are absent.

---

## 6. AI/ML Specifications

### Models and Providers

Harness-provided (Claude Code / any AGENTS.md-compatible tool). The skill is
model-neutral; it ships no model calls of its own.

### Prompt Patterns

Agentic wave prompts follow `reference-agent-prompt-template.md`. Progressive
loading controls what enters context per task.

### Context Management

Always-loaded router + on-demand reference loading; `reviews/LATEST.md` is the
current-state anchor re-read after a context reset.

---

## 7. Data Architecture

### Data Models

Markdown artifacts whose metadata is carried as `> **Field:** value` blockquote
headers (`Status`, `Owner`, `Epic`, `Story`, etc.), parsed by `lib/sdlc_md.py`.
[HIGH] Note: some templates also document YAML frontmatter, but the parser of
record reads the blockquote headers - the two should be reconciled (see TRD §6
open question). JSON state files: `project-state.json`, `review-state.json`,
`review-queue.json`, `status-cache.json`, `verify-report.json`.

### Relationships and Constraints

Hierarchical traceability: PRD → CR/Epic → Story → Plan/Test Spec/Workflow/Bug.
Link fields are required per type (see `reference-outputs.md#traceability`).

### Storage Mechanisms

Plain files in the repo (`sdlc-studio/`), user-local runtime state in
`sdlc-studio/.local/` (gitignored).

---

## 8. Integration Map

### External Services

GitHub Issues (via `gh` CLI only; no PyGitHub).

### Authentication Methods

Inherited from `gh auth` for sync. None otherwise.

### Third-Party Dependencies

None at the skill level (stdlib Python). Soft runtime tools listed in §1.

---

## 9. Configuration Reference

### Environment Variables

| Variable | Description | Required | Default |
| --- | --- | --- | --- |
| `CLAUDE_SKILL_DIR` | Path to the installed skill (used to invoke scripts) | No | resolved by harness |

### Feature Flags

Project config (`.sdlc-studio.yaml` / `templates/config-defaults.yaml`):
`require_ac_verification`, story-quality thresholds, review interval, commit
strategy, coverage targets.

---

## 10. Quality Assessment

### Tested Functionality

The Python scripts have unit tests (`scripts/tests/`; ~1000 and growing - run
`python3 -m unittest discover` for the live count rather than trusting a pinned
number). Markdown is guarded by seven CI checks (`npm run lint`, or each one
directly - see AGENTS.md "Testing the Skill", which lists the npm-independent
commands).

### Untested Areas

The markdown command *behaviours* (process flows in `reference-*.md`) have no
executable tests – they are validated by use and by the scripts they invoke. This
is the main gap a generated test backlog would close.

### Technical Debt

Known historical ID collisions documented in `reference-outputs.md`. Generate-mode
validation (tests against behaviour) is not yet wired for the markdown layer.

**Enforcement gaps (a 2026-07-04 field retrospective, tracked as CRs).** The skill
is strong on *document integrity* (status propagation, index reconcile, structural
validate) and thinner on *behaviour / test integrity*. Each gap below is a place a
rule is stated but not executably enforced, so it holds only when the agent
remembers:

- **Test integrity (CR0131 discipline, CR0134 gate).** Nothing detects a vacuous
  assertion or an injected-data test that never exercises the real wiring; a green
  suite can sit over dead code. CR0131 added the discipline (prose + template
  fields); CR0134 proposes the executable mutation-check gate that would enforce it.
- **Verification depth (CR0136).** The depth tiers are documented but `transition.py`
  never reads the depth field, so a `smoke`-only bug can be marked Fixed.
- **Finding self-diagnosis (CR0132, completing CR0025).** `reconcile`'s
  `count-mismatch` emits a generic fix hint that does not name the cause or route to
  the tool that diagnoses it, so a real drift reads as a "quirk" to ignore.
- **Toolbox discoverability (CR0133).** The dominant finding: 40+ deterministic
  scripts exist but an agent reaches for a handful and hand-does the rest. A single
  session broke CI four ways and re-proposed three already-shipped tools, purely by
  not finding them. This is the highest-impact item.
- **British-spelling check (CR0135).** `lint-style.sh` enforces em-dash + jargon but
  not Americanised spelling.

There are also 17 open audit-filed bugs (incl. 1 Critical) raised against this
workspace and its scripts; several qualify the feature statuses above. See
`bugs/_index.md` for the full register.

---

## 11. Open Questions

- Should the markdown command flows get executable conformance tests, or is the
  scripts' test suite plus reconcile/validate sufficient as the oracle?
- Does the repo want a committed, self-managed `sdlc-studio/` workspace long-term
  (this brownfield run), or is it a one-off design vehicle for RFC0001?

---

## Changelog

| Date | Version | Changes |
| --- | --- | --- |
| 2026-06-20 | 2.0.0 | Brownfield extraction of PRD from skill source (Generate mode) |

---

> **Confidence Markers:** [HIGH] clear from code | [MEDIUM] inferred from patterns | [LOW] speculative
>
> **Status Values:** Complete | Partial | Stubbed | Broken | Not Started
