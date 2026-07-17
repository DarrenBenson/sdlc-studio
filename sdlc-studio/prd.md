# Product Requirements Document

**Project:** SDLC Studio
**Version:** 4.1.0
**Last Updated:** 2026-07-14
**Status:** Generated (brownfield extraction; epics/stories validated and closed out 2026-07-09, commit 841471e)

> Generated in **Generate mode** by reverse-engineering the skill's own source.
> This is a migration blueprint: detailed enough to rebuild SDLC Studio on a
> different harness. Per `reference-philosophy.md`, features are not "Done" until
> tests validate the spec against the implementation. Confidence markers and
> status values are defined at the foot of this document.
>
> **Coverage:** v4.1.0 as released, plus the work sitting on `main` under
> `CHANGELOG.md` `[Unreleased]` (the breakdown gate, sprint capacity, the sizing
> and velocity loop, the retro learning loop, the two-backlog workflow, the refine
> and migrate commands, the Issue and triage discovery track, and the un-skippable
> sprint close-down). Anything not yet in a tagged release is marked
> **[Unreleased]** in the tables below. The document version tracks the product
> version; it is not itself a release artefact.

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
Test-Driven -> Behaviour-Driven -> Eval-Driven -> Goal-Driven). The `sprint`
command is its executable form - a prioritised batch driven along the goal ladder
`triage -> plan -> design -> done` - and every run closes with a reconcile, a
review and a retro.

**Gates over goodwill.** v4 turns the most-skipped parts of that discipline from
prose into mechanism, because a rule enforced by judgement is the rule that gets
skipped under effort pressure - measured on the product's own benchmark, not
assumed. The engagement floor, the breakdown gate, the release gate and the
learning loop all share one shape: the fire/skip decision is computable from
artefact fields and config, never from the model's own read of how big the job
feels; the escape is a recorded operator decision, never an omission; and an
absent config blocks rather than disarms (see TRD ADR-006 through ADR-011).

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
  (`SKILL.md` router + 52 `reference-*.md` + 41 `help/*.md` + 78 templates + 20
  best-practice guides + a cross-project lessons registry). No runtime beyond the
  agent reading them.
- **Python 3.10+ (stdlib only)** – 58 deterministic helper scripts under
  `scripts/`, sharing a six-module `lib/` whose parsing core is `lib/sdlc_md.py`.
  Pure stdlib; no third-party packages required (PyYAML is used for config when
  present and degrades to the caller's default when absent).
- **Soft runtime deps** – `gh` CLI (sync), `pytest`/`jest`/`vitest`/`go`/`curl`/
  `jq`/`rg` (whichever a project's AC Verify lines invoke), `git` (id allocation,
  the engagement floor's commit attribution).

### Architecture Pattern

Progressive-disclosure router. `SKILL.md` is the only always-loaded file; all
detail is loaded on demand via a loading guide. Deterministic, side-effect-bearing
work (id allocation, artefact creation, drift detection, AC verification, mutation
checking, repo indexing, GitHub sync, the gates) is delegated to Python scripts so
the agent reasons over JSON, not raw files. Judgement stays with the agent; the
decision to *run* a gate never does. See the TRD for the full architecture.

---

## 2. Problem Statement

### Problem Being Solved

AI-assisted delivery drifts: specs and code diverge, statuses go stale, ids
collide, acceptance criteria are vague, and agentic batch runs leave artifacts
inconsistent. SDLC Studio imposes a governed lifecycle with machine-checkable
acceptance criteria, census-based drift detection, and completion cascades so the
paperwork stays true to the code without manual bookkeeping.

Underneath that sits a second, harder problem the v4 work is aimed at: **an agent
under effort pressure skips the process it is told to follow.** The project's own
benchmark measured it - on the base models most teams run, an agent free to judge
whether a ticket was "big enough for ceremony" shipped the same defect as an agent
with no process at all, precisely on the tickets where the ceremony would have
caught it. Stronger models engaged unprompted; weaker ones did not, and the
judgement call is where the process leaks. So the parts of the lifecycle that
matter most are enforced mechanically: a planning floor, a grooming gate, a
verified definition of Done, and a learning loop that must produce work.

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

Status: all features **Complete** at v4.1.0 (the skill is in production use), with
the rows marked **[Unreleased]** complete on `main` and not yet in a tagged
release. Confidence **[HIGH]** unless noted – extracted directly from source. The
Epic column maps each feature to its owning epic (see `sdlc-studio/epics/`); a few
[Unreleased] rows delivered by an interactive RFC/CR sprint before the per-request
epic decomposition cite that governing RFC/CR instead.

> **Complete vs Ready:** these statuses describe the *implementation* - the
> features ship and work. The generated spec that documents them was tracked at
> epic and story level as **Ready** until the test suite validated it against the
> implementation, at which point the epics and stories were transitioned to **Done**
> in the verified close-out of 2026-07-09 (commit 841471e). **Complete is not the
> same as calibrated:** the token forecast under "Sizing and velocity" ships and
> runs, and its prediction is a falsified hypothesis (see §10).
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
| Validate | Skill + instructions + seat hygiene checks | Complete | Medium | scripts/validate.py | EP0008 |
| Lessons registry | Cross-project lessons-learned, recall before decisions | Complete | Medium | lessons/, scripts/lessons.py | EP0009 |
| Init / Onboarding | Project config + doctrine onboarding + agent-instructions seed | Complete | High | help/init.md, reference-doctrine.md | EP0009 |
| Operator heuristics | Live-service patterns, deploy readiness, release gate | Complete | Medium | reference-operator-heuristics.md, reference-deploy-readiness.md | EP0009 |
| Upgrade | Schema migration between versions, incl. the v2 -> v3 id walk | Complete | Low | reference-upgrade.md, scripts/migrate_v3.py | EP0008 |
| Cross-tool portability | AGENTS.md standard, cross-harness installer (six targets) | Complete | High | templates/agent-instructions.md, install scripts | EP0009 |

### v3 and v4 capabilities

| Feature | Description | Status | Priority | Location | Epic |
| --- | --- | --- | --- | --- | --- |
| Sprint loop (Goal-Driven) | A prioritised batch driven along `triage -> plan -> design -> done`; WSJF order, dependency waves, agentic execution, close = reconcile + review + retro | Complete | High | reference-sprint.md, scripts/sprint.py | EP0031, EP0032 |
| Engagement floor | A multi-file change in a spec-bearing repo REQUIRES the planning pass. Deterministic gate lane: a shipped unit that neither planned (AC / `Verify:` / linked plan) nor declares a real single-file `Affects:` is refused. Opt out only by recorded config or waiver | Complete | High | reference-doctrine.md (rule 16), reference-config.md, scripts/engagement_floor.py | EP0031 |
| Breakdown gate | `sprint plan` REFUSES an ungroomed batch (a unit must declare `Affects:` and a size). Exits non-zero and prints no plan. `sprint.breakdown: judgement` downgrades it to a report; an absent config BLOCKS | Complete **[Unreleased]** | High | reference-sprint.md#breakdown, scripts/sprint.py | CR0260 |
| Sprint capacity | `capacity.tokens/minutes/units` - one number feeding both the plan-time fit check and the run-time appetite breaker. Over-budget WARNS, never gates | Complete **[Unreleased]** | Medium | reference-config.md#capacity, scripts/sprint.py, scripts/loop_guard.py | CR0259 |
| Run appetite / breaker | `--appetite-minutes` / `--appetite-units` bound an unattended run; the breaker stops it cleanly at a unit boundary with its own exit code | Complete | High | reference-sprint.md#appetite, scripts/loop_guard.py | EP0032 |
| Sizing and velocity loop | Modified Fibonacci **Points** (1, 2, 3, 5, 8, 13, 20) size a story/bug and a T-shirt **Size** sizes a CR/RFC/epic - the one size vocabulary (Effort S/M/L is retired). Forecast = sum(Points) x the measured tokens-per-point rate; WSJF = CoD / Points; `retro accuracy` judges the recorded plan-time forecast against measured actuals; `retros/VELOCITY.md` is a committed history. **Points are the first cost predictor to clear the pre-registered bar** (r = +0.68, §10) | Complete **[Unreleased]** | Medium | scripts/sprint.py, scripts/retro.py, scripts/telemetry.py | RFC0038, EP0048 |
| Distributed identity (schema v3) | Collision-free ULID ids (`US-01JQK3F8`) so uncoordinated writers - human and agent, across machines and git states - never mint the same id. Sequential ids stay valid; `migrate_v3 adopt` is forward-only and the two eras coexist | Complete | High | reference-upgrade.md, scripts/migrate_v3.py, scripts/lib/sdlc_md.py | EP0012, EP0028 |
| Generated team (seats) | `persona generate --team` grows fresh named engineering seats from THIS project (PRD/TRD/config/repo map) onto behavioural variables and risk axes, never demographics. 3 core roles + up to 2 signal-earned extras, cast capped at 5. Provenance stamp + content hash keep an operator's edit from being clobbered | Complete | High | reference-persona-generate.md#team-generation, scripts/persona_gen.py | EP0030 |
| Stakeholder panel | `persona generate --stakeholders` generates the other side of the table (buyer, compliance, ops, served) with veto lines and the Cooper arbitration rule on every card: a buyer goal never overrides the Primary user's interface | Complete | Medium | reference-persona-generate.md, templates/personas/stakeholder-template.md | EP0030 |
| Cooper persona arbitration | Personas arbitrate rather than decorate: a multi-Primary cast warns, two Primaries on one `Interface:` is an error, `**Serves:**` tags feed a coverage check, and every consult carries the Primary test plus a per-seat objection quota | Complete | Medium | reference-persona.md, scripts/validate.py | EP0030 |
| Learning loop | Doctrine rule 17: a retro is checked on its CONTENT, every finding takes a disposition (filed, or declined with a reason - silence fails), and its lessons are lifted into the store the next `sprint plan` prints unasked. Bound close-gate lanes; `lessons.loop: judgement` opts out | Complete **[Unreleased]** | High | reference-retro.md, reference-doctrine.md (rule 17), scripts/retro.py, scripts/lessons.py | EP0010 |
| Lessons ranking | `lessons rank` orders the registry by recurrence (computed from citations in the files, never asserted), recency, and structural-fix demotion - a lesson whose class a shipped guard now makes impossible stops crowding out live ones | Complete **[Unreleased]** | Medium | scripts/lessons.py | EP0010 |
| Mutation gate | Proves the tests can FAIL, where `verify_ac` proves they pass: a bounded declared fault set applied to a surface, re-running the suite per mutation, reporting killed / survived / error / unviable. Advisory lane in the gate; an absent report reads not-run, never PASS | Complete | High | help/mutation.md, reference-test-best-practices.md, scripts/mutation.py | EP0011 |
| Quality gate (`gate`) | One portable, ecosystem-neutral exit code over the deterministic checks (conformance, reconcile, validate, integrity, duplicate-id, doc-coverage, engagement-floor, doc-freshness, mutation, ...), plus bound close lanes (retro, lessons, review currency, handoff) and `--release`, which EXECUTES every story's `Verify:` line | Complete | High | help/gate.md, scripts/gate.py | EP0026, EP0031 |
| Independence gate | Author != reviewer, enforced mechanically; a verification depth is required before a terminal bug status | Complete | High | scripts/transition.py, scripts/critic.py | EP0026 |
| Handoff guide | A generated record of where an agentic run stopped: delivered with evidence, remaining with a per-item pointer and a copilot-tail / judgement tag, and the open decisions. A Done unit whose ACs are red or stale is reported as remaining, not delivered | Complete | Medium | scripts/handoff.py | EP0032 |
| Adversarial audit | Pressure-tests the workspace and its artefacts, seeding its lens set from the ranked lessons registry | Complete | Medium | reference-audit.md, scripts/audit.py | EP0026 |
| Triage and noise control | An `inbox` lane for findings under schema v3; duplicate and noise detection on filing | Complete | Medium | scripts/triage_noise.py, scripts/file_finding.py | EP0014 |
| Decisions ledger and waivers | A recorded decision is the only escape from a gate: `decisions waive --subject rule:<lane>[:<id>]` names a subject and leaves an audit trail | Complete | High | reference-decisions.md, scripts/decisions.py | EP0019 |
| Repo review / lite on-ramp | `review generate` gives an existing repo a zero-setup taster; the lite profile is the on-ramp | Complete | Medium | scripts/review_generate.py, scripts/lite_profile.py | EP0016 |
| PVD (multi-repo) | The Product Vision Document above the PRD; cross-repo `Depends on:` resolution through its manifest | Complete | Low | reference-pvd.md, scripts/pvd.py, scripts/lib/xrepo.py | EP0032 |
| Id allocation | Deterministic next-id (sequential era) and collision-free ULID minting (v3), remote-aware, serialised by an allocation lock | Complete | High | scripts/next_id.py, scripts/artifact.py | EP0008, EP0012 |
| Skill self-update / version check | `hint`/`status` compare the installed version against the latest GitHub release over a direct HTTPS GET (`api.github.com`); default on, `version_check.enabled` opt-out, 5s timeout, silent when offline; `skill-update` installs a newer release | Complete | Low | help/skill-update.md, reference-skill-update.md, scripts/version_check.py | EP0008 |
| Two-backlog workflow | A request backlog (CR/RFC/Issue) sits beside the product backlog: `plan` refuses a request as a sprint unit (G1), a request's terminal status is derived from its children (G2), request/child links resolve both ways (G3), `status` reports the two backlogs apart (G4), and reconcile flags an accepted childless request as undecomposed (G5). Gated by `two_backlog.enforce`, default off so an upgrade keeps the old flow until it opts in | Complete **[Unreleased]** | High | reference-sprint.md, scripts/lib/sdlc_md.py, scripts/sprint.py | EP0033, EP0034 |
| refine (request decomposition) | `refine` turns a CR/RFC into an epic plus sized stories with the two-backlog links wired; `--add` appends further epics to an already-decomposed request, and `show` lists an existing decomposition read-only | Complete **[Unreleased]** | High | reference-scripts-create.md, scripts/refine.py | EP0035, EP0036, EP0039 |
| Migration to the sizing model | `migrate_v3 sizing` converts legacy Effort to a T-shirt `Size` or point band deterministically and reports the units a human must re-size; the `migrate` orchestrator runs the project upgrade, that sizing pass and an artefact-review sweep in one dry-run report, applying only the safe set | Complete **[Unreleased]** | Medium | reference-upgrade.md, scripts/migrate.py, scripts/migrate_v3.py | EP0037, EP0042 |
| Issue type and triage | An `Issue` discovery artefact joins the vocabulary; `triage` refiles an Issue into bugs atomically, reconcile flags an untriaged Issue, and an Issue's terminal status derives from its children | Complete **[Unreleased]** | Medium | help/issue.md, help/triage.md, scripts/triage.py, scripts/file_finding.py | EP0038 |
| Amigo consult in refine/triage | refine and triage route a request's open questions to the resolved seat cards by lens, record which seats were consulted, degrade gracefully when seats are absent, and hold the author != reviewer independence line | Complete **[Unreleased]** | Medium | reference-consult.md, scripts/refine.py, scripts/triage.py | EP0040 |
| Command-surface audit | `command_audit.py` enumerates every command and route with a keep/fold/retire disposition mapped to the process spine, a dead-route check confirms each kept command's tooling runs, and `hint`/`status` surface the Discovery-versus-Delivery backlog split | Complete **[Unreleased]** | Low | scripts/command_audit.py, scripts/status.py | EP0041 |
| reconcile apply creates a missing index | `reconcile apply` materialises a missing pipeline or meta `_index.md` from its template, clearing missing-index drift rather than only reporting it | Complete **[Unreleased]** | Low | reference-reconcile.md, scripts/reconcile.py | EP0043 |
| Audit cost pre-flight | `audit` estimates the agents, tokens and wall-time of a scoped run and confirms above a threshold before a large adversarial fan-out | Complete **[Unreleased]** | Low | reference-audit.md, scripts/audit_cost.py | EP0044 |
| Interactive sprint token capture | `retro` records an interactive sprint's actual token count and computes its tokens-per-point, retiring the "interactive means UNMEASURED" framing while keeping the forecast-is-not-a-gate guards | Complete **[Unreleased]** | Low | reference-retro.md, scripts/retro.py | EP0045 |
| Sprint close-down gate | A close-owed detector names terminal delivery units filed since the last retro; `status`/`hint` nudge; `gate` grows a close-owed lane (warn by default, block under `--require-close`); a Stop-hook installer redefines sprint-done as close-gate-green | Complete **[Unreleased]** | Medium | reference-sprint.md, scripts/gate.py, scripts/handoff.py | EP0046 |
| Backlog triage in plan | Triage lenses (duplicate/subsumed/superseded by Affects-overlap and title similarity, plus oversized, stale and orphaned-dependency) run as a pass inside `sprint plan` - oversized blocks, judgement lenses report, drops are logged - with filing-time duplicate detection and a `status` summary | Complete **[Unreleased]** | Medium | reference-sprint.md, scripts/backlog_triage.py, scripts/sprint.py | EP0047 |

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

#### Engagement floor (the planning pass is not a judgement call)

**User Story:** As an orchestrator, I want a multi-file change in a spec-bearing
repo to be unable to reach Done without a planning pass, so the pipeline cannot be
skipped exactly on the changes that need it.

**Acceptance Criteria:**

- [ ] A shipped unit that touches more than one source file and carries no acceptance criterion, no `Verify:` line and no linked plan FAILS the gate.
- [ ] "Multi-file" is judged from the unit's declared `Affects:` and cross-checked against the source files its own commit touched, so pure omission cannot dodge the floor.
- [ ] A `Refs: <id>` commit trailer attributes a shared commit's files per id; attribution is strictly additive, so a "see also" trailer can never lower a unit's file count and disarm its own check.
- [ ] The only escapes are recorded: `engagement_floor: judgement` in config (the lane reports, never blocks), an `adopt_after:` id cutoff that is refused if set beyond the current work, or a `decisions waive` entry.

**Dependencies:** scripts/engagement_floor.py, scripts/gate.py, reference-doctrine.md rule 16
**Status:** Complete · **Confidence:** [HIGH]

#### Breakdown gate (`sprint plan` refuses an ungroomed batch) [Unreleased]

**User Story:** As an operator, I want the planner to refuse a batch it cannot
honestly size, so a plan is never false authority over unsized work.

**Acceptance Criteria:**

- [ ] A unit is groomed only when it declares BOTH the files it will touch (`Affects:`) and a size: a story/bug by `Points:`, a CR/RFC/epic by a T-shirt `Size:`.
- [ ] With any ungroomed unit in the batch, `sprint plan` exits non-zero and prints NO plan, naming each offending unit, what it lacks, and the command that fixes it.
- [ ] The planner derives shared-file clusters from `Affects:`, so two units touching the same file are never reported as safely parallel.
- [ ] `sprint.breakdown: judgement` makes the lane report instead of block; an absent config BLOCKS and an unknown mode falls back to enforce.
- [ ] `sprint breakdown` reports the same census read-only, so a backlog can be groomed against exactly what the gate reads.

**Dependencies:** scripts/sprint.py, reference-sprint.md#breakdown
**Status:** Complete **[Unreleased]** · **Confidence:** [HIGH]

> The remaining features follow the same shape. Implementation-ready AC for each
> is extracted at the **story** layer (`story generate`), not duplicated here.
> Only a **story** carries executable `- **Verify:**` lines; CR and bug acceptance
> criteria are prose, and the filer refuses a command-shaped `Verify:` in one (see
> §4, Business Logic Rules).

---

## 4. Functional Requirements

### Core Behaviours

- A single router (`SKILL.md`) parses `[type] [action]`, loads the matching
  `help/{type}.md`, and follows the referenced `reference-{domain}.md` workflow.
- Generate mode produces migration-blueprint specs validated by tests; create
  mode authors forward-looking specs interactively.
- Every numbered artifact has an id (a 4-digit zero-padded sequential id, or a
  collision-free ULID under schema v3), an `_index.md` registry, blockquote
  metadata headers (`> **Field:** value`), and a canonical status vocabulary.
- Terminal status transitions trigger completion cascades that update all linked
  artifacts, indexes, dependency tables, and PRD feature statuses.
- The `sprint` loop drives a batch along `triage -> plan -> design -> done`,
  bounded by a declared appetite, and closes with reconcile + review + retro as a
  single blocking gate.
- Artefacts are created by the deterministic tooling (`artifact.py new`/`batch`,
  `file_finding.py`), never hand-authored: the id, the index row and the epic
  wiring are allocated by construction.

### Input/Output Specifications

- **Input:** `/sdlc-studio [type] [action] [flags]`, plus the project's own code
  and existing artifacts.
- **Output:** Markdown artifacts under `sdlc-studio/`, JSON state under
  `sdlc-studio/.local/`, and structured stdout from scripts.

### Business Logic Rules

- Files are the source of truth; indexes are derived and reconciled from a census.
- Ids never change once assigned. Sequential ids auto-increment on collision under
  an allocation lock; ULID ids (schema v3) carry an entropy tail so two
  uncoordinated writers in the same instant cannot mint the same id at all.
- "Done" requires verification: a story reaches Done only when its executable ACs
  pass. `transition -> Done` is gated, and a terminal bug status requires a
  recorded verification depth.
- **Only a story carries executable `- **Verify:**` lines.** CR and bug acceptance
  criteria are prose, and the filer refuses a command-shaped `Verify:` in one: a
  line nothing executes is a permanent false RED when it is wrong and a false GREEN
  when it is loose, and both had already happened.
- **The engagement floor:** a change touching more than one source file in a
  spec-bearing repo gets the planning pass before any code - a rule, not a
  judgement call.
- **The breakdown gate:** a batch reaching `sprint plan` must be groomed (every
  unit declares `Affects:` and a size) or the plan is refused outright.
- **The learning loop:** every retro finding takes a disposition - filed, or
  declined with a reason. Both are green; silence is not.
- A gate's fire/skip decision is computed from artefact fields, config and
  deterministic signals - never from model judgement. An escape is a recorded
  operator decision; an absent config blocks rather than disarms.
- Ship the paperwork in the same commit as the code (doctrine).

---

## 5. Non-Functional Requirements

### Performance

Scripts are pure stdlib. Read-path scripts (status, repo map, next-id,
review_prep, audit, critic, `gate`) are read-only over the workspace; the
authoring and repair scripts (`artifact`, `file_finding`, `transition`,
`reconcile apply`, `verify_ac`, `archive`, `lessons`, `retro`) write within a
tested, bounded surface, going through `atomic_write` for any shared file.
reconcile/status run in well under a second on a typical project (observed in
normal use, not a gated benchmark). `mutation` is the exception by design: it
re-runs the suite once per mutant and is minutes, not seconds.

### Security

Network access is limited to four outbound, optional paths, each degrading silently
when offline: the `gh` CLI (GitHub sync), a direct HTTPS GET to `api.github.com` for
the release check (the skill self-update; default on, opt out with
`version_check.enabled: false`; 5s timeout, any failure treated as offline),
`git fetch origin` in `sprint plan`'s origin-drift preflight and remote-aware id
allocation (best-effort, failure ignored), and the tools a project's Verify lines
invoke - whose reachable hosts a project bounds with `SDLC_VERIFY_HTTP_HOSTS`. No
secrets handled by the skill; secret handling is the consuming project's concern
(documented in its AGENTS.md).

### Scalability

Progressive disclosure keeps always-loaded context minimal (SKILL.md ~260 lines,
CI-budgeted under 500) regardless of total skill size. Agentic waves bound
concurrency; the appetite breaker bounds an unattended run. Schema-v3 ULID
identity is what makes the workspace safe for several uncoordinated writers -
human and agent, across machines and git states - filing concurrently.

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
headers (`Status`, `Owner`, `Epic`, `Story`, `Affects`, `Effort`, `Depends on`,
etc.), parsed by `lib/sdlc_md.py`. [HIGH] Note: some templates also document YAML
frontmatter, but the parser of record reads the blockquote headers - the two
should be reconciled (see TRD §6 open question).

Ids come in two eras that coexist by design: sequential (`US0001`, schema v2) and
ULID (`US-01JQK3F8`, schema v3). Both parse; `migrate_v3 adopt` is forward-only, so
an existing sequential id stays valid in tickets, chat and docs while new artefacts
mint ULIDs.

Machine state lives under `sdlc-studio/.local/` (gitignored): `project-state.json`,
`run-state.json`, `review-state.json`, `review-queue.json`, `status-cache.json`,
`verify-report.json`, `verify-history.jsonl`, `repo-map.json`,
`mutation-report.json`, `wsjf-inputs.json`. Measurement state is deliberately
**committed**, because it is evidence the team must read on a fresh clone, not a
cache: `retros/VELOCITY.md` is the human-read history, and beneath it the per-unit
run telemetry lives committed under `retros/evidence/` as `actuals-*.jsonl` (what a
unit actually cost) and `forecasts-*.jsonl` (what the planner predicted). A
pre-existing `.local` telemetry log is migrated there on first write - evidence only
one machine can read is not evidence.

### Relationships and Constraints

Hierarchical traceability: PRD → CR/Epic → Story → Plan/Test Spec/Workflow/Bug,
with RFC above CR for unsettled design and Retro/Review/Handoff closing a run.
Link fields are required per type (see `reference-outputs.md#traceability`).

### Storage Mechanisms

Plain files in the repo (`sdlc-studio/`), user-local runtime state in
`sdlc-studio/.local/` (gitignored).

---

## 8. Integration Map

### External Services

- **GitHub Issues** via the `gh` CLI only (no PyGitHub) - CR/story/epic sync.
- **GitHub Releases API** (`api.github.com`) via a direct stdlib HTTPS GET for the
  skill self-update check (`version_check.py`; default on, `version_check.enabled`
  opt-out, 5s timeout, silent on any failure).
- **The git remote** (`git fetch origin`) in `sprint plan`'s origin-drift preflight
  and remote-aware id allocation (best-effort; failure ignored, skipped with no remote).

### Authentication Methods

Inherited from `gh auth` for sync and from the ambient git credentials for `fetch`.
The release check is an unauthenticated public GET. None otherwise.

### Third-Party Dependencies

None at the skill level (stdlib Python, `urllib` for the release check). Soft runtime
tools listed in §1.

---

## 9. Configuration Reference

### Environment Variables

| Variable | Description | Required | Default |
| --- | --- | --- | --- |
| `CLAUDE_SKILL_DIR` | Path to the installed skill (used to invoke scripts) | No | resolved by harness |
| `SDLC_AUTHOR` | Author identity (`Name; type; version`, or a bare name) stamped as `Raised-by` when a creation path is given no explicit author; a multi-line value is refused | No | the invoking agent's own identity |
| `SDLC_VERIFY_HTTP_HOSTS` | Comma-separated host allow-list for the `http` AC verifier: non-empty turns on restricted mode and a target host outside it is refused | No | unset (unrestricted, subject only to the http/https scheme floor) |
| `SDLC_TRIAGE_SESSION` | Keys the triage session for the `triage.session_cap` filing budget; set a fresh value to start a new budget | No | `default` |
| `SDLC_DEBUG` | `1` emits one stderr line from each swallowed-advisory site (the opt-in diagnostic channel) | No | unset |
| `SDLC_STUDIO_REQUIRE_CHECKSUM` | Require a checksum on install (sensitive environments) | No | unset |

`SDLC_ENGAGEMENT_STRICT` is retired: the engagement floor's `commit-msg` gate blocks
unconditionally under `--strict`, and the one escape is `git commit --no-verify`.

### Feature Flags

Project config (`sdlc-studio/.config.yaml`, defaults in
`templates/config-defaults.yaml`). The gate-bearing keys are the ones that matter,
and they share one shape: the default is ON, the opt-out is a recorded value, and an
**absent** config blocks rather than disarms. The one deliberate exception is
`two_backlog.enforce`, which defaults **OFF** so an existing project pulling a newer
skill keeps its old flow until it opts in - the release must not break it.

| Key | Default | Effect |
| --- | --- | --- |
| `engagement_floor` | `floor` | `judgement` makes the lane report, never block. A mapping form carries `adopt_after:` (a forward-only id cutoff; set beyond the current work it is refused as a silent disarm) |
| `sprint.breakdown` | `enforce` | `judgement` makes `sprint plan` report an ungroomed batch instead of refusing it |
| `lessons.loop` | `loop` | `judgement` makes the retro/lessons close lanes advisory |
| `two_backlog.enforce` | `false` (deliberate) | The two-backlog hard gates (plan refuses a request, terminal status derived from children, `undecomposed` drift, CR-creation Size demand). OFF for upgrade safety; one config line turns it on |
| `capacity.tokens` / `.minutes` / `.units` | 500000 / 240 / 8 | The sprint ceiling. Tokens are a forecast and warn only; minutes and units feed the run breaker |
| `appetite.minutes` / `.units` | 0 (inherit `capacity`) | Pin one axis of the run breaker independently of capacity |
| `require_ac_verification` | `false` | Abort the completion cascade when a story's ACs do not pass. Adopt incrementally: leave off while seeding `Verify:` lines, enable once reconcile reports `manual: 0` |
| `quality.done_requires_verified` | `true` | The hard Done gate: a story cannot transition to Done while its executable ACs are red or never-run. Set false to downgrade it to an advisory warn |
| `quality.require_full_sections` | off | Hold every story to the full template's sections, not just the stamped ones |
| `schema_version` | 3 | 1 = legacy, 2 = modular, 3 = distributed identity + triage |

Plus story-quality thresholds, review interval, commit strategy and coverage
targets. See `reference-config.md` for the full reference.

---

## 10. Quality Assessment

### Tested Functionality

The Python scripts have unit tests (`scripts/tests/`; 2151 at the time of writing -
run `python3 -m unittest discover` for the live count rather than trusting a pinned
number, and `tools/tests/` covers the repo-only CI checkers). Markdown is guarded by
the eight-check `npm run lint` chain (markdownlint, prose style, links, skill
frontmatter, version consistency, line budgets, neutrality, action pins), each of
which except markdownlint runs without npm - see AGENTS.md "Testing the Skill". A
pre-commit hook (`tools/enable-hooks.sh`) makes the whole gate un-skippable rather
than something an agent has to remember.

### Untested Areas

The markdown command *behaviours* (process flows in `reference-*.md`) have no
executable tests – they are validated by use, by the scripts they invoke, and by the
eval scenarios (`tools/eval_run.py`) that drive a fixture project through a flow and
record a per-behaviour verdict. This is still the main gap a generated test backlog
would close.

### The cost model: a falsified predictor, then Fibonacci points

Stated plainly, because the product's own doctrine is that a claim registered as
evidence must survive being wrong - and this one was wrong before it was right.

The first sprint planner forecast a batch's token cost from the cognitive complexity
of the files a unit declares. That predictor was **falsified**: fitted to six units it
scored 1.09x in-sample, then 0.55x out-of-sample on the next sprint, under-forecasting
monotonically (a prior coefficient over-forecast by 3.3x). The diagnosis was that the
*input* carried no plan-time signal - file complexity does not measure the work done
in a file, and the thing cost actually tracked (tool-uses, r = 0.926) is an output,
unknowable when planning.

RFC0038 replaced it rather than re-fitting it. The bar was set **before** the data
was seen (pooled r >= 0.50, within-sprint correlations must not flip sign, beat Effort
0.35 clearly, predict a held-out sprint within 0.75x-1.25x), then 20 delivered units
across four sprints were re-estimated in modified Fibonacci points blind to outcome.
Points cleared every clause: **r = +0.682 pooled** (and +0.782 on units <= 8) against
Effort's 0.35 and file-complexity's 0.03. Points are the first cost predictor this
project has found that works. The shipped model is `forecast = sum(Points) x the
measured tokens-per-point rate` - a point measures about 25,000 tokens (flat across
the 2-, 3-, 5- and 8-point bands), seeded from that blind study and replaced by the
project's own measured rate once it has enough delivered units. Effort S/M/L is
retired; a unit too big to size on the scale is decomposed, not estimated.

The two loop defects this section used to list as open are **fixed** (BG0133, BG0136):
`retro accuracy` now judges only the forecast recorded at plan time and never
re-derives one from the live constants, so a recalibration can no longer silently
rewrite what a past sprint is deemed to have predicted; and the finder records
`Affects:`, so a filed bug is born plannable instead of refused by the project's own
planner. The forecast ships quoted with a band (honest to about +/-50%), never a gate;
`retro accuracy` and the committed `retros/VELOCITY.md` keep the next miss visible.

### Technical Debt

Known historical id collisions documented in `reference-outputs.md`. Generate-mode
validation (tests against behaviour) is not yet wired for the markdown layer.

The 2026-07-04 enforcement-gap retrospective that this section used to carry is
**closed**: the mutation gate is shipped (assertion integrity is executably checked,
not merely written down), `transition` reads the verification depth before a terminal
bug status, reconcile's findings name their cause and route to the tool that
diagnoses them, the router carries a Deterministic Entry Points card and
`reference-scripts.md` is the catalogue, and the style guard enforces British
spellings. Each was a rule stated but not enforced; each is now a lane with an exit
code. The live backlog is small and is listed in `reviews/LATEST.md`; `bugs/_index.md`
is the register of record.

The honest residue: the loop can now measure itself, and it did - a first predictor was
falsified and a second (Fibonacci points) cleared a pre-registered bar (above). The
sizing feature is Complete and, unlike its predecessor, earns a cost claim - held to a
band, never a gate. What remains open is calibration to THIS project: the ~25,000
tokens-per-point rate ships as a seed and only becomes the project's own measurement
once it has enough delivered units, so today's forecasts still lean on the study's rate.

---

## 11. Open Questions

- Should the markdown command flows get executable conformance tests, or is the
  scripts' test suite plus reconcile/validate plus the eval scenarios sufficient as
  the oracle?
- ~~Is there a plan-time predictor of delivery cost at all?~~ **Closed (RFC0038).** File
  complexity was falsified and tool-uses is an output, but modified Fibonacci points
  cleared a pre-registered bar (r = +0.68 pooled, +0.78 on units <= 8) in a blind
  re-estimation of 20 delivered units. The shipped forecast is sum(Points) x the
  measured tokens-per-point rate; the per-unit estimate stays, sized on the scale.
- The learning loop is mandated on the engagement floor's *reasoning* and not yet on
  its *evidence*. The claim that closing the loop cuts repeat defects is registered
  as a claim to be measured. What experiment settles it?
- Does the repo want a committed, self-managed `sdlc-studio/` workspace long-term
  (this brownfield run), or is it a one-off design vehicle for RFC0001?

---

## Changelog

| Date | Version | Changes |
| --- | --- | --- |
| 2026-06-20 | 2.0.0 | Brownfield extraction of PRD from skill source (Generate mode) |
| 2026-07-14 | 4.1.0 | Refresh to the v4 feature set: the engagement floor, the breakdown gate, sprint capacity and the run appetite, the sizing and velocity loop (with its falsification stated), ULID identity, the generated team and stakeholder panel, the learning loop, the mutation gate and the release gate. `autosprint` renamed to `sprint`. Corrected the corpus and test counts, replaced the closed 2026-07-04 enforcement-gap list, and expanded the config reference to the gate-bearing keys |

---

> **Confidence Markers:** [HIGH] clear from code | [MEDIUM] inferred from patterns | [LOW] speculative
>
> **Status Values:** Complete | Partial | Stubbed | Broken | Not Started
