# SDLC Studio

**Version 3.0.1** | MIT Licence

**Set a goal and acceptance criteria; the agent drives the proven software
lifecycle to it - and proves the code against it.** SDLC Studio brings back the
engineering discipline the AI-coding wave dropped - clear requirements, acceptance
criteria, traceability, a definition of done that means done - and has the *agent*
carry the cost of the ceremony, so the discipline stays. Its **`sprint`** loop
runs a prioritised batch of work along a goal ladder (`triage -> plan -> design ->
done`), closing every run with a reconcile and review.

```bash
/sdlc-studio sprint --crs Proposed --goal done   # set the goal; or just ask in natural language
```

A full software-development-lifecycle skill for AI coding agents - one folder of
instructions, templates, and tested scripts that takes a project from requirements
to verified code:

> **PRD → TRD → Personas → Epics → User Stories → Plan → Code → Tests → Verify**

SDLC Studio is a standard [Agent Skill](https://agentskills.io)
(`SKILL.md` format), so the same install works in **Claude Code, OpenAI
Codex, Gemini CLI, opencode, and GitHub Copilot**.

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
true to what was built. The agent carries the cost of the ceremony, and the
discipline stays.

It is also why the lifecycle is, in current terms, a loop-engineering problem
already solved. An agent runs in a loop that cannot judge its own exit condition;
the lifecycle has always been that loop - specify, build, validate against the
specification, reconcile, repeat - with acceptance criteria as the test that
closes it. The spec-driven and eval-driven tools arriving now are rediscovering a
cycle the SDLC described in full long ago.

## Goal-Driven Development

This is the discipline SDLC Studio enables and `sprint` automates. You set the
**goal** and the acceptance criteria; the agent drives the proven lifecycle to it -
decompose, build under TDD, verify, reconcile, review. It sits in the lineage
**Test-Driven -> Behaviour-Driven -> Eval-Driven -> Goal-Driven Development**. Say
`/sdlc-studio sprint --crs Proposed --goal done` (or just ask in natural
language); the loop runs the batch along the goal ladder (`triage -> plan -> design
-> done`), stops when its acceptance criteria are met, and closes every run with a
reconcile and review (the sprint review).

## The idea (for beginners)

Most AI coding jumps straight from a vague prompt to code, then drifts
as the project grows. SDLC Studio adds the steps a real team uses, so
the agent always has the context it needs to stay on track. Each step
writes a plain markdown file under `sdlc-studio/` in your project. You
stay in control: review each artefact, then run the next command.

Start a brand-new project with `prd create`, or point it at existing
code with `prd generate`. If you ever lose your place,
`/sdlc-studio status` shows where you are and `/sdlc-studio hint` tells
you the single next thing to do.

## Install

One line, any platform:

```bash
# macOS / Linux - Claude Code, globally (the classic)
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash

# Every tool you have installed
curl -fsSL https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.sh | bash -s -- --target auto
```

```powershell
# Windows
irm https://raw.githubusercontent.com/DarrenBenson/sdlc-studio/main/install.ps1 | iex
```

### Where it installs

| Tool | Global | Project-local | Invoke as |
| --- | --- | --- | --- |
| Claude Code | `~/.claude/skills` | `.claude/skills` | `/sdlc-studio` (or model-invoked) |
| Codex | `~/.agents/skills` | `.agents/skills` | `$sdlc-studio`, `/skills` |
| Gemini CLI | `~/.gemini/skills` | `.gemini/skills` | auto via description; `/skills` to confirm |
| opencode | `~/.config/opencode/skills` | `.opencode/skills` | auto via skill tool |
| Copilot | (repo-scoped) | `.github/skills` | from chat |
| `agents` (generic) | `~/.agents/skills` | `.agents/skills` | read by Codex, Gemini, Copilot, Cursor |

`--target claude,codex` picks tools; `--local` installs into the current
project; `--list-targets` shows the map and what is detected. The generic
`.agents/skills` directory is read by four tools, so `--target agents`
covers Codex, Gemini, Copilot, and Cursor in one copy (Claude Code does
not read it). Native
alternatives also work: `gh skills install DarrenBenson/sdlc-studio
sdlc-studio` (Copilot) or `gemini skills install
https://github.com/DarrenBenson/sdlc-studio`.

**Stale-copy sweep:** after installing, the installer refreshes every
other sdlc-studio copy it finds in the known locations (reported as
`old -> new`; it never touches a directory that is not this skill), so
no stale version lingers when you use several tools. Opt out with
`--no-sweep` / `-NoSweep`. Full detail: [docs/INSTALL.md](docs/INSTALL.md).

### Verify

Start your tool in any project and run `/sdlc-studio status` (Claude
Code) or confirm the skill is listed (`/skills` in Codex/Gemini). You
should see the pipeline dashboard.

## Quick start

```text
/sdlc-studio init              # New project: scaffold the tree, indexes, config (greenfield step 1)
/sdlc-studio status            # Where am I? (four-pillar dashboard)
/sdlc-studio hint              # The single next thing to do
/sdlc-studio prd create        # New project: interview -> PRD
/sdlc-studio prd generate      # Existing code: extract the PRD from it
/sdlc-studio epic              # Break the PRD into Epics
/sdlc-studio story             # Break Epics into User Stories with AC
/sdlc-studio code plan         # Plan the next story
/sdlc-studio code implement    # Build it
/sdlc-studio code verify       # Verify against acceptance criteria
```

Run `/sdlc-studio help` for the full catalogue (bugs, change requests,
RFCs, personas, test specs, test automation, GitHub sync, and every
flag).

## What you get

**Two modes for every document.** `create` interviews you (greenfield);
`generate` reverse-engineers a *migration blueprint* from existing code
(brownfield) - detailed enough to rebuild the system, validated by
running tests against the real implementation.

**Status that polices itself.** Artifacts carry canonical statuses;
`reconcile` detects and fixes drift from a file census; acceptance
criteria can carry executable `Verify:` lines that `reconcile --verify`
actually runs. A blind-review gate checks that a plan's tasks logically
satisfy every AC *before* implementation.

**Determinism in scripts, judgement in the model.** A suite of stdlib-only
Python helpers (census, status, validation, ID allocation, repo indexing, AC
verification, the portable quality gate, deterministic artifact create/close,
GitHub sync, plan/lessons management) with 850+ unit tests do the mechanical
work; the model does the thinking.

**Agentic execution.** `epic implement --agentic` analyses the story
dependency graph and hub-file overlap, then runs safe waves of parallel
implementation agents (Claude Code only), with quality gates at every
wave boundary and a lessons file that makes each wave smarter than the
last.

**Cross-project memory.** A lessons registry ships with the skill
(`lessons recall` before big decisions; `lessons add --global` to
promote what you learn), and each project accumulates its own pitfall
file that agentic waves inject into every prompt.

**Two-way GitHub sync.** CRs, stories, and epics sync with GitHub
Issues through the `gh` CLI; merged PRs trigger completion cascades.

## Output structure

```text
sdlc-studio/
  prd.md  trd.md  tsd.md  personas.md
  epics/      EP0001-*.md  + _index.md
  stories/    US0001-*.md  + _index.md
  plans/      PL0001-*.md  + _index.md
  bugs/       BG0001-*.md  + _index.md
  test-specs/ TS0001-*.md  + _index.md
  crs/  rfcs/  reviews/  workflows/
  .local/                  # gitignored: caches, reports, lessons
tests/                     # generated test code (project root)
```

## Requirements

- Python 3.10+ for the bundled scripts (pure stdlib, no pip installs)
- `gh` CLI (authenticated) only for the GitHub sync commands
- Whatever test runners your AC verifiers invoke (pytest, vitest, go...)

## Upgrading

**v2.x → v3.0** is a drop-in: re-run the installer, no project migration (`schema_version` is
still 2). The one rename to know: **`autosprint` is now `sprint`** - the old command still works
as a deprecated alias, so existing scripts and habits keep running.

## Upgrading from v1.x

Re-run the installer - it replaces the skill in place and sweeps other
locations up to the same version. **No project migration is needed:**
the artifact schema is unchanged (`schema_version: 2`), so existing
`sdlc-studio/` directories keep working. What changed in v2 is the
skill itself: open Agent Skills frontmatter, `$CLAUDE_SKILL_DIR` script
paths, consolidated reference docs, new helpers and CI guards - see
[CHANGELOG.md](CHANGELOG.md).

**v2.0 → v2.1** is a drop-in: re-run the installer. No project migration -
`schema_version` is still 2. v2.1 adds the `autosprint` loop, complexity/test-risk
signals, the `audit` harness, an optional `constitution`, index archival, and
per-project config; nothing in the artifact schema changed.

**v2.1 → v2.2** is a drop-in too. New in v2.2: the skill checks for a newer release on
`status`/`hint` and **`/sdlc-studio skill-update`** upgrades the install (user / project
/ agents, auto-detected) on confirm - so from here on, upgrading is one command. The
check is on by default, silent offline, and never nags once dismissed; opt out with
`version_check.enabled: false`.

## Roadmap

**Shipped in v3.0.0 - the sprint lifecycle, greenfield authoring, and a self-review pass:**
**`autosprint` is renamed `sprint`** (the command is the whole lifecycle; autonomy is the
`--autonomous` flag) - `autosprint` stays as a deprecated alias, so nothing breaks. The sprint
**goal ladder** `triage -> plan -> design -> done` makes each rung a reviewable stop-point;
greenfield **authoring** drives a PRD into epics and stories (`sprint <prd.md> --goal design`);
planning orders by **seat-scored WSJF**. Greenfield gets an executable **`init`** (step 1) and a
project **`decisions`** log. A full adversarial **self-review** (RV0005) then hardened the skill:
the AC-to-test bridge is mandatory at epic scope, a Done-gate consults the AC-verify result,
docs point at the deterministic scripts rather than hand-edits, and the best-practice guides
adopt the SOTA linters (ShellCheck/shfmt, Ruff/mypy).

**Shipped in v2.4:** **`project upgrade`** migrates an existing project to the current
conventions - it detects the version/convention gap, auto-corrects the safe set (config,
provenance cutoff, index drift) on confirm, and reports the judgement items; `skill-update`
offers it after a bump. Plus an advisory **progressive-disclosure + best-practice check** that
keeps the skill's own token footprint honest (Load-when markers, no orphans, lean router).

**Shipped in v2.3 - a product layer, determinism, and a documentation DoD:** the **Product
Vision Document** (a multi-repo product layer above the PRD, with read-only projection and
cross-repo feature-map traceability); fully **deterministic artifact create/close** for every
numbered type, with **provenance** stamping; local **run telemetry**; a portable,
ecosystem-neutral **CI gate** bundling every deterministic check; a **doc-coverage Definition
of Done** (docs ship with the code); the **Cooper goal-directed persona model** plus isolated
review-seat charters (RFC0016/RFC0017); and help reframed around the autosprint loop.

**Shipped in v2.2:** a built-in version check + **`skill-update`** - the skill notices
new releases on `status`/`hint` and upgrades itself (scope-detected) on confirm, with a
per-version snooze so it never nags.

**Shipped in v2.1 - the autonomous loop + a deterministic control plane:**
`autosprint` with hard guardrails (decisions ledger, iteration cap, completion
oracle, conformance gate, independent critic) and complexity-aware `--order wsjf`;
code-complexity + churn signals driving estimation, refactor-first, and
complexity-weighted test risk; a portable adversarial `audit` harness with a
deterministic finding filer; an optional project `constitution` with a
machine-checkable principle gate; progressive-disclosure index archival for large
boards; deterministic status transitions; and per-project config (status-vocab
extensions, conformance adoption cutoff).

**Next:** complexity-weighted wave-sizing (RFC0009 WS5) once per-story run-cost
telemetry exists; a wired `/audit` command after a third proving run. See the
RFC registry (`sdlc-studio/rfcs/`) for the full design backlog.

## Troubleshooting

- **`/sdlc-studio` not found** - confirm the skill directory exists for
  your tool (`install.sh --list-targets`), then restart the session;
  Claude Code also live-reloads project-level skills.
- **Installer download fails** - check network/proxy; you can install
  manually: `git clone` this repo and copy
  `.claude/skills/sdlc-studio/` into your tool's skills directory.
- **Commands run but nothing happens** - run `/sdlc-studio status`; if
  the pipeline is empty the next step is `prd create` or `prd generate`.
- **Uninstall** - `./install.sh --uninstall` (same `--target`/scope you
  installed with); preview with `--dry-run`.

## Contributing and development

Dev instructions live in [AGENTS.md](AGENTS.md) (read natively by
Codex, Copilot, Cursor, Gemini; Claude Code imports it via CLAUDE.md).
Lint with `npm run lint` (markdown, style, links, frontmatter spec,
version consistency, line budgets); test with `npm test`. Behavioural
eval scenarios live in [evals/](evals/README.md). See
[CONTRIBUTING.md](CONTRIBUTING.md).

## Documentation

- [docs/INSTALL.md](docs/INSTALL.md) - full installer reference
- `/sdlc-studio help` - command catalogue (also
  `.claude/skills/sdlc-studio/help/help.md`)
- `.claude/skills/sdlc-studio/reference-doctrine.md` - the operating
  doctrine for running any project with this skill
- [CHANGELOG.md](CHANGELOG.md) | [SECURITY.md](SECURITY.md) | [SUPPORT.md](SUPPORT.md)
