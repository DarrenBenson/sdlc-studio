<!--
Template: Agent Instructions (tool-neutral). Save as AGENTS.md at the project root; Claude
Code imports it from a one-line CLAUDE.md (agent-instructions.CLAUDE.md). Fill in every
{{placeholder}}, then delete this comment. Every call loads this file: keep it short.
-->
# {{PROJECT_NAME}} - Agent Instructions

{{One sentence: what this project is and does.}} This file is the single source of truth
for how to work here; tool-specific files point to it.

## Operating doctrine

`<skill>` below is the folder the sdlc-studio skill is installed in for your tool: `~/.claude/skills/sdlc-studio` (Claude Code), `~/.agents/skills/sdlc-studio` (Copilot CLI, Codex, Gemini CLI, Cursor), or `.claude/skills/sdlc-studio` / `.agents/skills/sdlc-studio` in this repository for a project-local install.

This project runs on the **sdlc-studio** skill. Before substantive work, and again after any
context compaction or reset (`/compact`, `/clear`, a fresh session):

1. Read `<skill>/reference-doctrine.md`, the project-agnostic operating rules.
2. Read `sdlc-studio/reviews/LATEST.md`, the state snapshot that survives compaction.
3. Run `/sdlc-studio status`, then `/sdlc-studio hint` for the next step.
4. Recall relevant lessons: `/sdlc-studio lessons recall`.

Do not restate the doctrine here; record below only what this project adds to it.

## Non-negotiable gates

**Never release until the full pre-release gate is green.** In order, before any tag:

1. `/sdlc-studio reconcile --verify` runs every story's `Verify:` expression and fails on any
   `no` or `stale`. This is what makes "Done" mean done.
2. `/sdlc-studio review` runs all five legs, **PRD - TRD - TSD - Persona - CODE** (plus **PVD**
   when `sdlc-studio/product/pvd.md` exists), and confirms the PRD (and PVD) requirements
   are met. The CODE leg is not optional.

Fix the findings before tagging. Even a production hotfix files a `bug` (rationale +
`Verify:` expression + audit pin).

**Review is independent of the author.** One independent reviewer, a fresh context that did
not write the change, records each unit's verdict with `critic.py record`, and its APPROVE
decides the unit. The run is signed once, with `sprint sign`, by its reviewer of record: the
operator, or a named delegate in a separate trust boundary, never a unit's author or reviewer.

**Integrate continuously.** Commit each unit to `main` when its gate passes and push `main`; open no PR and push no branch unless `release_strategy` is `pr-required`.

**No ad-hoc coding.** Every change flows CR / RFC -> Epic -> Story -> code plan -> code
implement -> code verify -> reconcile -> review. Default to TDD: write the `Verify:`
expression or the failing test first.

**The engagement floor.** A change to more than one source file names every existing
requirement it interacts with, and how each is resolved, and writes one acceptance criterion
per interaction before any code. Opt out with `engagement_floor: judgement` in
`sdlc-studio/.config.yaml`.

## How to work

1. **Think, then make the smallest change.** State assumptions, surface rival readings, write
   the minimum the criteria need, and ship the paperwork in the same commit as the code.
2. **Run approved work to the end.** Stop only for a blocker the SDLC cannot resolve, an
   operator pause, or a destructive action; for a second opinion, `/sdlc-studio consult team`.
3. **Use the deterministic tooling; never hand-roll what it wires.**
   - Create artifacts with `python3 <skill>/scripts/artifact.py new --type bug --title "..."
     --affects "a.py, b.py" --points 3` (`batch` for many). A bug names its files and size;
     a CR is a request, and the epic `refine` writes from it is sized.
   - **Never hand-allocate ids or hand-author `_index.md`**: the index is derived.
   - Pass prose as a document, never a shell argument: `--fields-file FIELDS.json` (`-` reads stdin).
   - **A story reaches Done only when its executable ACs pass**: `transition -> Done` is
     gated on its `Verify:` lines.

The other habits (index conventions, fan-out, temp files) are in the Working habits
section of `<skill>/reference-doctrine.md`.

## Project specifics

Fill these in: this is the part an agent cannot infer.

- **Stack:** {{languages, frameworks, runtime versions}}
- **Run / build / test:** {{exact commands, e.g. `make test`, `npm run dev`}}
- **Deploy & CI:** {{how a release ships; what the CI gate runs}}
- **Config & secrets:** {{where config lives, how secrets are provided, what NOT to commit}}
- **Code style:** {{rules that differ from defaults}}
- **Architecture & services:** {{topology and key services, or "see TRD"}}
- **Gotchas:** {{non-obvious behaviour that has bitten people before}}

## Don't

- Grow this file with per-ship narrative: `git log` and `LATEST.md` hold it.
- Use a library from memory: query its current API docs first.
- Mark a generated spec Done without tests.
- Share a temp path: name it per agent or run, or keep it in your worktree.
