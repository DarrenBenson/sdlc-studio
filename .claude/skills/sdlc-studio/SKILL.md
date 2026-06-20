---
name: sdlc-studio
description: "Full software development lifecycle pipeline: create or reverse-engineer PRDs, TRDs, personas, epics, and user stories with acceptance criteria, then plan, implement, test, and verify code against them - with status dashboards, reconciliation, change requests, RFCs, test specs, test automation, and bug tracking. Use when asked about PRDs, requirements documents, epics, user stories, personas, implementation planning, test specs, test automation, project status, bugs, change requests, or any /sdlc-studio [type] [action] command. Run /sdlc-studio help for the catalogue and /sdlc-studio status for next steps."
license: MIT
compatibility: "Requires Python 3.10+ for bundled scripts; gh CLI (authenticated) for GitHub sync commands. Agentic wave execution (--agentic) is Claude-Code-only."
metadata:
  version: "2.0.0"
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

# SDLC Studio

Manage project specifications and test artifacts. Supports the full pipeline from PRD creation through Epic decomposition, User Story generation, and streamlined test automation.

This file is the always-loaded router. It carries only what is needed to route a request:
philosophy gates, the Progressive Loading Guide, and pointers. The full command catalogue,
argument reference, workflow diagrams, and reference index are loaded on demand from
`help/help.md`, `help/arguments.md`, and `help/references.md`.

## Critical Philosophy (Read This First)

**Two modes for every artifact type:**

| Mode | Purpose | When to Use |
| --- | --- | --- |
| **create** | Author new specifications from user input | Greenfield projects, new features |
| **generate** | Extract specifications from existing code | Brownfield projects, documentation gaps |

> **New to Create vs Generate?** Read `reference-philosophy.md` - it explains why these modes exist and how they differ fundamentally.
>
> **Using generate mode?** You MUST read `reference-philosophy.md#generate-mode` first - generated specs must be validated by tests.

**Generate mode is NOT documentation.** It produces a **migration blueprint** - a specification detailed enough that another team could rebuild the system in a different technology stack. Generated specs MUST be validated by running tests against the existing implementation.

> **Operating Doctrine – onboarding to a project? Read `reference-doctrine.md` first.** It is the project-*agnostic* working discipline (the skill is the operating system; RFC/CR/ADR choice; files-are-truth + reconcile-from-census; reconcile/verify/review cadence; ship-paperwork-in-the-same-commit; consult gates; TDD; cross-repo numbering; **recall cross-project `lessons/` before substantive decisions**). A project's own agent-instructions file (`AGENTS.md`; Claude Code's `CLAUDE.md` can import it with `@AGENTS.md`) = this doctrine + that project's specifics; start from `templates/agent-instructions.md`. The cross-project lessons-learned folder is `lessons/` (see `help/lessons.md`).

## Quick Start

```bash
/sdlc-studio help                    # Full command reference (help/help.md)
/sdlc-studio status                  # Check pipeline state and next steps
/sdlc-studio hint                    # Single actionable next step
/sdlc-studio review                  # Unified PRD/TRD/TSD/Persona review
/sdlc-studio reconcile               # Fix all status drift in one pass
/sdlc-studio prd generate            # Create PRD from codebase
/sdlc-studio epic                    # Generate Epics from PRD
/sdlc-studio story                   # Generate Stories from Epics
/sdlc-studio code plan               # Plan implementation for story
/sdlc-studio code implement          # Execute implementation plan
/sdlc-studio story implement         # Execute story workflow (all phases)
/sdlc-studio epic implement          # Execute epic workflow (all stories)
/sdlc-studio project implement       # Execute all epics in dependency order
```

For the full catalogue (bug, cr, rfc, persona, consult, chat, trd, test-*, repo map,
sync, and every flag), run `/sdlc-studio help` or read `help/help.md`.

## Get Help for Any Type

```bash
/sdlc-studio {type} help             # Type-specific commands, prerequisites, output, examples
```

Examples: `/sdlc-studio epic help`, `/sdlc-studio code help`, `/sdlc-studio bug help`.

## When to Use

Use when asked about: PRD, TRD, epics, stories, personas, bugs, code planning, implementation, testing, test specs, test automation, project status, or any `/sdlc-studio` command.

## Instructions

When invoked with `/sdlc-studio [type] [action]`:

1. **Parse Command:** Extract type and action from arguments
2. **Load Help File:** Read `help/{type}.md` for command-specific guidance
3. **Check Philosophy:** If generate mode, load `reference-philosophy.md#generate-mode` FIRST
4. **Follow Progressive Loading:**
   - Load reference files only for multi-step workflows
   - Load templates only when creating artifacts
   - Load decision files when choosing approaches (TDD, Ready status)
5. **Execute Workflow:** Follow step-by-step procedure in reference file
6. **Update Status:** Modify artifact status markers per `reference-outputs.md`
7. **Validate:** Check Ready criteria in `reference-decisions.md` before proceeding

**Note:** Version checks run on `hint` and `status` commands only (see those help files).

See "Progressive Loading Guide" below for detailed file loading patterns.

## Progressive Loading Guide

Claude loads files progressively based on task needs:

| Task Type | Primary Load | Secondary Load | Decision Load |
| --- | --- | --- | --- |
| Understanding a command | help/{type}.md | - | - |
| Full command catalogue | help/help.md | - | - |
| Argument / flag reference | help/arguments.md | - | - |
| Reference & template catalogue | help/references.md | - | - |
| Create mode workflow | help/{type}.md | reference-{domain}.md | reference-philosophy.md#create-mode |
| Generate mode workflow | reference-philosophy.md#generate-mode | help/{type}.md | reference-{domain}.md |
| Creating artifacts | templates/core/{type}.md | reference-outputs.md | - |
| Loading modules | templates/modules/{domain}/*.md | - | - |
| Planning code | reference-code.md#code-plan-workflow | reference-decisions.md#story-ready | best-practices/{language}.md |
| Choosing TDD/Test-After | reference-decisions.md#tdd-decision-tree | reference-test-best-practices.md | - |
| Validating Ready status | reference-decisions.md#{type}-ready | reference-outputs.md | - |
| Document review | reference-review.md | reference-{doc}.md | - |
| Schema upgrade | reference-upgrade.md | reference-config.md | - |
| Project orchestration | reference-project.md | reference-epic.md | reference-config.md |
| Agentic execution | reference-agentic-lessons.md | reference-epic.md | - |
| Autosprint (Goal-Driven Development loop) | reference-autosprint.md | help/autosprint.md | reference-project.md |
| Building agentic wave prompts | reference-agent-prompt-template.md | reference-repo-map.md | reference-agentic-lessons.md#lessons-accumulation |
| Change request workflow | help/cr.md | reference-cr.md | reference-outputs.md |
| RFC / design exploration | help/rfc.md | reference-rfc.md | reference-outputs.md |
| Invoking skill internals | reference-scripts.md | scripts/README.md | - |
| Ranking files for a story | reference-repo-map.md | help/repo-map.md | reference-agent-prompt-template.md#agent-prompt-template |
| Verifying ACs against codebase | reference-verify.md | help/verify.md | reference-reconcile.md#verify-scope |
| Syncing CR/Story/Epic with GitHub | reference-github-sync.md | help/github-sync.md | reference-cr.md#cr-sync-workflow |
| Onboarding to a project / operating doctrine | reference-doctrine.md | help/init.md | lessons/_index.md |
| Recording and loading project lessons | reference-agentic-lessons.md#lessons-accumulation | help/lessons.md | reference-agent-prompt-template.md#agentic-execution |
| Recalling cross-project lessons (before a decision) | lessons/_index.md | help/lessons.md | reference-doctrine.md |
| Operator patterns (memory drift, incident localisation, release-gate) | reference-operator-heuristics.md | templates/workflows/release-gate.md | reference-reconcile.md#numeric-claim-drift |
| Hypothesis discipline (don't guess root cause) | reference-operator-heuristics.md#hypothesis-discipline | reference-bug.md#bug-close-workflow | reference-test-best-practices.md#verification-depth-tiers |
| Preparing to tag a release | templates/workflows/release-gate.md | reference-operator-heuristics.md | reference-reconcile.md |
| Deploy readiness (cold-spawn, smoke budget, rollback, soak) | reference-deploy-readiness.md | reference-test-best-practices.md#verification-depth-tiers | reference-decisions.md#release-strategy-decision |
| Verification depth tiers (smoke / functional / conversational / soak / live) | reference-test-best-practices.md#verification-depth-tiers | templates/core/bug.md | templates/core/story.md |
| Test-timeout tuning (measure local + CI variance) | reference-test-best-practices.md#test-timeout-tuning | - | - |
| Multi-persona pressure-test canvas (unsettled design) | reference-consult.md#pressure-test-canvas | reference-decisions.md | - |
| Plan-file lifecycle (active / archive / list) | reference-plan-files.md | help/plan.md | - |
| Reconcile cadence triggers | reference-reconcile.md#cadence-triggers | help/status.md#reconcile-recommendation | - |

**Template structure:**

| Path | Purpose |
| --- | --- |
| `templates/core/*.md` | Streamlined core templates (v2) |
| `templates/indexes/*.md` | Index file templates |
| `templates/modules/trd/*.md` | Optional TRD modules (diagrams, containers, ADR) |
| `templates/modules/tsd/*.md` | Optional TSD modules (contract, perf, security) |
| `templates/modules/epic/*.md` | Optional Epic perspective modules |
| `templates/config-defaults.yaml` | Skill default configuration |

**Module loading flags:**

| Flag | Modules Loaded |
| --- | --- |
| `trd create --with-diagrams` | modules/trd/c4-diagrams.md |
| `trd create --with-containers` | modules/trd/container-design.md |
| `trd create --full` | All TRD modules |
| `epic --perspective engineering` | modules/epic/engineering-view.md |
| `epic --perspective product` | modules/epic/product-view.md |
| `epic --perspective test` | modules/epic/test-view.md |

**Reference file mapping:**

Reference files follow the pattern `reference-{domain}.md`. When executing
a workflow, load the reference file matching the artifact type being created
or modified. Cross-domain files (`reference-decisions.md`, `reference-outputs.md`,
`reference-philosophy.md`) load as needed for validation, status updates, and
approach decisions. The full index is in `help/references.md`.

## Type Reference

| Type | Description |
| --- | --- |
| `prd` | Product Requirements Document |
| `trd` | Technical Requirements Document |
| `tsd` | Test Strategy Document (project-level) |
| `persona` | User Personas |
| `consult` | Persona consultation on artefacts |
| `chat` | Interactive persona sessions |
| `epic` | Feature groupings (Epics) |
| `story` | User Stories with acceptance criteria |
| `code` | Implementation planning, testing, and quality |
| `test-spec` | Consolidated test specification (plan + cases + fixtures) |
| `test-automation` | Generate executable test code |
| `test-env` | Containerised test environment setup |
| `bug` | Bug tracking and traceability |
| `cr` | Change requests (post-PRD change proposals) |
| `rfc` | Request For Comments – design exploration of an unsettled space, pre-CR |
| `project` | Project-level orchestration across all epics |
| `autosprint` | Goal-Driven Development loop: a prioritised batch driven to a goal |
| `plan` | Claude Code plan-file lifecycle (list, archive) |
| `reconcile` | Detect and fix status drift across all artifacts |
| `status` | Visual dashboard: Requirements, Code, Tests health |
| `hint` | Single actionable next step |
| `help` | Show command reference and examples |

## Full Reference

The catalogues that used to live inline are now loaded on demand to keep this router lean:

| You need... | Read |
| --- | --- |
| Every command, grouped by pipeline, with examples | `help/help.md` (or run `/sdlc-studio help`) |
| The complete argument and flag table | `help/arguments.md` |
| Workflow diagrams (greenfield, brownfield, agentic, project) | `help/help.md` "Typical Workflows" |
| The full `reference-*.md` index and template structure | `help/references.md` |
| Type-specific commands, prerequisites, output, examples | `help/{type}.md` |
| Step-by-step workflow detail for an artifact | `reference-{domain}.md` |
| Autosprint loop (Goal-Driven Development) | `help/autosprint.md` + `reference-autosprint.md` |

## Error Handling

**Missing prerequisites:** Prompts to run earlier pipeline step (e.g., no PRD → `prd`, no epics → `epic`, no stories → `story`, no plans → `code plan`). **Existing files:** Warns and asks to continue unless `--force`. **No type:** Asks user which type. **ID collision:** Auto-increments. **Open questions:** Reports and pauses. **Unknown language:** Asks user to specify framework.
