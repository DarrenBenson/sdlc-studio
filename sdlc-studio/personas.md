<!--
Template: User Personas (Streamlined)
File: sdlc-studio/personas.md
Source: Generated (brownfield) from skill source and usage
Generated: 2026-06-20
Confidence: INFERRED
Status values: See reference-outputs.md
Related: help/persona.md, reference-persona.md, reference-persona-generate.md
-->
# User Personas

**Project:** SDLC Studio
**Version:** 2.0.0
**Last Updated:** 2026-06-20
**Status:** Generated (brownfield)

> Generated in **Generate mode** by reverse-engineering the skill's own source
> and usage. These personas are **inferred** and await validation against real
> usage. Confidence markers per persona: [HIGH] clear from source, [MEDIUM]
> inferred from patterns, [LOW] speculative.

Personas for SDLC Studio, the Claude Code skill that drives a project from
requirements through to verified implementation. Referenced in user stories so
features are designed for specific users. Four personas are developed here,
matching PRD §2 Target Users: the Orchestrator/Operator (primary), the
Consuming-project Developer, the AI Agent executing the skill, and the Skill
Maintainer.

---

## Orchestrator / Operator  [HIGH]

**Role:** Delivery lead driving the pipeline; primary user
**Technical Proficiency:** Expert
**Primary Goal:** Run a delivery tranche end to end and trust that the paperwork
matches the code at the close

### Background

Owns delivery of a product or service that uses Claude Code with SDLC Studio
installed. Plans and runs tranches of work - decomposing a PRD into epics and
stories, kicking off agentic waves (`epic implement`, `project implement`), and
making the material decisions: RFC versus CR, what is Ready, when to tag a
release. Lives in `/sdlc-studio status` and `hint`, reads `reviews/LATEST.md` to
re-orient, and treats reconcile and review as scheduled discipline rather than
optional cleanup. Operates the doctrine: the skill is the operating system,
every substantive change flows through it.

### Needs & Motivations

- A single next step (`hint`) and a true dashboard (`status`) without manual bookkeeping
- Census-based `reconcile` that fixes mechanical drift in one pass and flags judgement calls without auto-transitioning
- `reconcile --verify` as a release gate so "Done" means tests passed, not asserted
- Agentic fan-out with bounded concurrency and quality gates, so a tranche completes without leaving artifacts inconsistent
- Deterministic ID allocation that never collides across repos
- Cross-project `lessons/` recall before substantive decisions

### Pain Points

- AI-assisted delivery drifts: specs and code diverge, statuses go stale, IDs collide
- Agentic batch runs that leave indexes, dependency tables and PRD feature statuses out of step
- Vague acceptance criteria that cannot be checked, so completion is a judgement call
- Bookkeeping that has to be done by hand after every wave
- Losing orientation after a context reset mid-tranche

### Typical Tasks

- `prd generate`, `epic`, `story` to decompose work, then `code plan` / `code implement`
- `epic implement` and `project implement` to drive agentic waves in dependency order
- `reconcile` after closing an epic, actioning a CR, tagging a release, or any manual edit
- `reconcile --verify` and the full review set (PRD, TRD, TSD, Persona, CODE) before a release
- `cr` and `rfc` to handle post-PRD change and unsettled design; `bug` for fixes

### Quote
>
> "Give me one next step, run the wave, then prove the dashboard is still true."

---

## Consuming-project Developer  [HIGH]

**Role:** Engineer who installs SDLC Studio into their own codebase
**Technical Proficiency:** Advanced
**Primary Goal:** Reverse-engineer reliable specs from their existing code, then
keep them honest as the code changes

### Background

Works on a brownfield project and wants the discipline without writing it from
scratch. Installs the skill to `.claude/skills/sdlc-studio/` (or via the
cross-harness installer), runs `init` to seed project config and an
agent-instructions file, then runs the generate pipeline over their codebase -
`prd generate`, `persona generate --from-code`, `epic`, `story`. Cares that the
skill is tool-neutral (`AGENTS.md` standard) so it does not lock them to one
harness, and that the helper scripts are pure stdlib so there is nothing extra
to install. Treats generated specs as a migration blueprint to be validated by
tests, not as documentation.

### Needs & Motivations

- A clean install and `init` that seeds config plus a doctrine-aligned agent-instructions starter
- Generate mode that produces specs detailed enough to rebuild the system elsewhere
- No third-party Python dependencies; soft runtime tools only when their own Verify lines need them
- Offline-capable core pipeline; sync and remote-ID checks degrade gracefully when `gh` is absent
- Clear guidance on what each command needs and produces (`{type} help`)

### Pain Points

- Brownfield codebases with no current, trustworthy requirements
- Tooling that assumes greenfield or assumes a specific harness
- Heavy dependency chains that complicate adoption in their CI
- Generated docs that drift the moment code changes, with no way to detect it

### Typical Tasks

- Install the skill, run `init`, commit the seeded agent-instructions file
- `prd generate` and `persona generate --from-code` to extract a baseline from their code
- `epic` and `story` to build an implementation-ready backlog
- `reconcile` and `validate` to keep their workspace and indexes honest
- `repo map build` to rank files for a story; `story sync` to mirror to GitHub Issues

### Quote
>
> "Pull a real spec out of my code, and tell me when it stops matching."

---

## AI Agent Executing the Skill  [HIGH]

**Role:** Non-human operator - the agent that reads SKILL.md and runs the workflows
**Technical Proficiency:** Expert (context-bounded)
**Primary Goal:** Execute the requested command correctly without drifting from
the doctrine, while keeping always-loaded context minimal

### Background

The agent invoked as `/sdlc-studio [type] [action]`. It parses the command in
the always-loaded router (`SKILL.md`, ~195 lines), loads the matching
`help/{type}.md`, gates on philosophy when in generate mode, then follows the
referenced `reference-{domain}.md` workflow under progressive disclosure -
loading reference files, templates and decision files only when a step needs
them. For deterministic, side-effect-bearing work (ID allocation, drift
detection, AC verification, repo indexing, GitHub sync) it calls the Python
helpers and reasons over their JSON rather than over raw files. After a context
reset it re-reads `reviews/LATEST.md` to anchor on current state, and recalls
`lessons/` before substantive decisions.

### Needs & Motivations

- Unambiguous routing: one entry point, a clear `[type] [action]` map, explicit load order
- Deterministic helpers that return structured JSON, so it reasons over state instead of re-deriving it
- A current-state anchor (`reviews/LATEST.md`) to recover orientation after a reset
- Progressive loading so context stays small no matter how large the skill grows
- Hard gates (generate-mode philosophy, `require_ac_verification`) that stop it promoting unverified work

### Pain Points

- Ambiguous instructions or duplicated guidance that invite divergent interpretations
- Re-deriving state from raw files - slow, and a source of error and drift
- Context bloat that crowds out the task
- Losing the thread after a reset mid-workflow
- Being asked to mark something Done without an executable check behind it

### Typical Tasks

- Parse the command, load `help/{type}.md`, follow the reference workflow step by step
- Run `reconcile.py`, `status.py`, `verify_ac.py`, `next_id.py`, `repo_map.py`, `github_sync.py` and act on their JSON
- Apply completion cascades on terminal status transitions across linked artifacts and indexes
- Fan out agentic waves as subagents within bounded concurrency, honouring quality gates
- Re-read `reviews/LATEST.md` and recall `lessons/` before deciding

### Quote
>
> "Route me cleanly, hand me JSON not raw files, and anchor me when my context resets."

---

## Skill Maintainer  [MEDIUM]

**Role:** Developer of SDLC Studio itself
**Technical Proficiency:** Expert
**Primary Goal:** Evolve the skill safely - back-port live fixes, keep scripts
deterministic and tested, and tag clean releases

### Background

Maintains this repo, which is the skill's own source. Production fixes land first
in the installed copy at `~/.claude/skills/sdlc-studio/`, then back-port here -
the installed copy is the back-port source (per project memory and `CLAUDE.md`).
Keeps `SKILL.md` lean by delegating the command catalogue, flags and reference
index out to `help/` and `reference-*.md`; adds help files and updates the
tables when adding commands. Runs markdownlint over all markdown and the unit
suite for the Python helpers, and requires both green before tagging. Writes to
the house style: British English, no em dashes, no corporate jargon, dense and
economical.

### Needs & Motivations

- A lint-clean, test-green gate (`npm run lint`; `python3 -m unittest` over `scripts/tests`) before any release
- A predictable structure: router stays minimal, detail lives in help and reference files
- `validate.py` to catch skill and instructions hygiene problems early
- A clear back-port path from the installed production copy into the repo
- Style discipline enforced consistently across 40-plus reference files and 70-plus templates

### Pain Points

- `SKILL.md` bloating as the always-loaded file, eroding the context budget for every consumer
- Back-port divergence between the installed copy and the repo source
- Untested markdown command behaviours - the main quality gap, since only the scripts have unit tests
- Style and structure drift across a large file set
- Historical ID collisions documented but easy to reintroduce

### Typical Tasks

- Back-port production fixes from `~/.claude/skills/sdlc-studio/` into the repo
- Add a help file under `help/`, update SKILL.md tables, add or update the relevant `reference-*.md`
- Run markdownlint and the script unit suite; fix failures before tagging
- Bump `version.yaml` and `metadata.version`; record changes in changelogs
- Run `validate` and `reconcile` against fixtures to confirm the skill behaves

### Quote
>
> "Keep the router lean, the scripts tested, and the back-port path honest - then tag it."

---

> **Confidence Markers:** [HIGH] clear from source | [MEDIUM] inferred from patterns | [LOW] speculative
>
> All personas above are inferred in Generate mode and await validation against real usage.
