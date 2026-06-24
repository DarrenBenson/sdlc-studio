<!--
Template: Agent Instructions (canonical, tool-neutral)
Usage: Save this as AGENTS.md at your project root. AGENTS.md is the cross-tool
       standard read by Codex, Copilot, Cursor, Gemini, Aider, Windsurf and Zed.
       For Claude Code, add a one-line CLAUDE.md that imports it (see
       agent-instructions.CLAUDE.md). Fill in every {{placeholder}}; delete the
       guidance comments. Keep it short - an agent reads it every session, and a
       bloated file gets ignored.
Related: reference-doctrine.md, help/init.md, agent-instructions.CLAUDE.md
-->
# {{PROJECT_NAME}} - Agent Instructions

{{One sentence: what this project is and does.}} This file is read at the start of
every session by your coding agent. It is the project's single source of truth for
how to work here; tool-specific files (`CLAUDE.md`, `.github/copilot-instructions.md`)
should point to it rather than duplicate it.

## Operating doctrine

This project runs on the **sdlc-studio** skill. Before substantive work:

1. Read `.claude/skills/sdlc-studio/reference-doctrine.md` - the project-agnostic
   operating rules (the SDLC is the operating system; files are truth, indexes are
   derived; reconcile cadence; TDD by default).
2. Read `sdlc-studio/reviews/LATEST.md` for current orientation.
3. Run `/sdlc-studio status` then `/sdlc-studio hint` for the next concrete step.
   (`status`/`hint` also surface a one-line notice if a newer SDLC Studio release
   exists - run `/sdlc-studio skill-update` to take it, or it stays quiet until the
   next release. Opt out with `version_check.enabled: false` in `.config.yaml`.)
4. Recall relevant cross-project lessons (`/sdlc-studio lessons recall`).

**After any context compaction or reset** (a `/compact`, `/clear`,
auto-summarisation, or a fresh session), re-read `sdlc-studio/reviews/LATEST.md`
and run `/sdlc-studio status` before continuing. That file is a state snapshot,
not a transcript, so it survives compaction and re-orients you in one read - in
any agent (Claude Code, Codex, Copilot, opencode).

Do not restate the doctrine here. Capture below only what an agent cannot infer
from the code or the doctrine: this project's specifics.

## Non-negotiable gates

**IMPORTANT - never release to production until the full pre-release gate is green.**
In order, before tagging any release:

1. `/sdlc-studio reconcile --verify` - the executable AC gate. It runs every story's
   `Verify:` expression and fails on any `no` or `stale`. This is what makes "Done"
   mean done.
2. `/sdlc-studio review` - the full review set, **all five legs: PRD - TRD - TSD -
   Persona - CODE** (plus a **PVD** leg when the product spans repos and a
   `sdlc-studio/product/pvd.md` exists). The CODE leg is not optional; doc-only review
   never finds a crash bug, a deploy gap, or an untested hot path. The review confirms
   the **PRD requirements are met** (the Product Owner's sign-off) - and, where a PVD
   exists, the **PVD requirements are met** (the Product Manager's sign-off).

Triage and **fix** the findings before tagging. No exceptions - even a genuine
production hotfix files a `bug` (rationale + `Verify:` expression + audit pin).

**Index & verification conventions.** Keep **one canonical status summary** per `_index.md` - the
`| Status | Count |` table with a `**Total**` row, which `reconcile` maintains. Per-section / per-epic
count tables are author-maintained; do not give them a `Total` row (reconcile would treat them as the
global summary). For a human-checked AC, write `Verify: manual <what to check>` so it is counted
*manual*, never shelled out - and never hand-stamp `Verified:` for an AC a machine did not check.

Every substantive change flows through the skill:
**CR / RFC -> Epic -> Story -> code plan -> code implement -> code verify ->
reconcile -> review.** No ad-hoc coding. Default to TDD: author the `Verify:`
expression or failing test first, then make it pass.

## How to work

1. **Think before coding.** State assumptions explicitly. If multiple readings exist,
   surface them rather than picking silently. If a simpler approach exists, say so.
2. **Simplicity first.** The minimum code that satisfies the story's acceptance
   criteria. Nothing speculative - no abstraction for single-use code, no
   configurability that was not asked for.
3. **Surgical changes.** Touch only what the story requires. Match the existing style.
   Ship the paperwork (PRD / TRD / capability tables) in the same commit as the code.
4. **Goal-driven autonomous execution.** Set the goal to complete every task in the
   approved plan or wave **autonomously, without human intervention**. The SDLC's own
   gates (consult, verify, test, check, reconcile) ARE the review - run each wave
   through to ship plus reconcile. Do not stop mid-execution. Stop only for: a genuine
   technical blocker the SDLC cannot resolve, an explicit operator pause, or a
   destructive / hard-to-reverse action (force-push, branch or table deletion, sending
   an external message).
   - **When you need another opinion, consult personas instead of stopping.**
     `/sdlc-studio consult team` (Three Amigos: Product Owner, Engineering, QA) on any epic or
     story design. `/sdlc-studio consult stakeholders` when the change touches the
     running system. Concerns are advisory - record them and proceed unless one is a
     hard technical blocker.
5. **Use the deterministic tooling - never hand-roll what it wires.**
   - **Bootstrap with `init`** (it creates the directory tree, the per-type `_index.md`
     files, config, and the agent-instructions). After `init` the first `new` of any type is
     indexed - a bare `indexed=false` means "no index yet", not "the tool does not index".
   - **Create every artifact with `artifact.py new` / `/sdlc-studio` create.** It allocates a
     collision-free id, writes the file, appends the index row, and wires a story into its
     parent epic. **Never hand-allocate ids or hand-author `_index.md`** - the file is truth,
     the index is derived. For many at once use `artifact.py batch` (one atomic pass).
   - **Fan out only over pre-wired scaffolds.** Delegated sub-agents fill **content**; the
     tool owns structure (ids, slugs, filenames, links, index).
   - **The index is derived:** run `reconcile` / `reconcile fields` / `validate` to sync;
     never hand-copy file-owned cells (story points, titles).
   - **A story reaches Done only when its executable ACs pass.** Author `Verify:` lines in the
     DSL (`jest`/`pytest`/`http`/`manual`) against the real runner; `transition -> Done` is
     gated on the verify result. Record load-bearing decisions in `decisions.md`, not scattered.
   - **Foundation first, then autosprint.** Build the foundation epic by hand to a green gate
     (it sets conventions every later story inherits); autosprint needs a runnable gate, so
     hand subsequent epics to `autosprint --epic EPxx --goal done` once it is green.

## Project specifics

Fill these in. This is the part an agent cannot infer.

- **Stack:** {{languages, frameworks, runtime versions}}
- **Run / build / test:** {{exact commands, e.g. `make test`, `npm run dev`}}
- **Deploy & CI:** {{how a release ships; what the CI gate runs}}
- **Config & secrets:** {{where config lives, how secrets are provided, what NOT to commit}}
- **Code style:** {{rules that differ from defaults, e.g. British English, no em-dash,
  error-shape conventions, "no `any`"}}
- **Architecture & services:** {{topology and key services, or "see TRD §{{n}}"}}
- **Gotchas:** {{non-obvious behaviour that has bitten people before}}

## Don't

- Don't grow this file with per-ship narrative - that is what `git log`, spec detail
  blocks, and `sdlc-studio/reviews/LATEST.md` are for.
- Don't use a library from memory - query current API docs first; training data is stale.
- Don't mark a generated spec Done without tests. Generated specs are migration
  blueprints, not documentation, and never auto-promote to Done.
