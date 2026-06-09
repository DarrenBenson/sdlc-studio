# SDLC Studio Operating Doctrine

**Read this to onboard to ANY sdlc-studio project.** These are the project-*agnostic*
working rules – the discipline that makes a Claude effective in an sdlc-studio repo.
Project-*specific* facts (architecture, config paths, deploy recipes, code-style
rules, the agents/services) live in that project's agent-instructions file
(`AGENTS.md`, which `CLAUDE.md` / `.github/copilot-instructions.md` may point to)
+ TRD, not here.

> A project's agent-instructions file should be **doctrine (this file) + project
> specifics**. The cross-tool standard is `AGENTS.md`; Claude Code reads `CLAUDE.md`
> (point it at `AGENTS.md` with `@AGENTS.md`). Start from
> `templates/agent-instructions.md`.
> When onboarding to a new project: (1) read this doctrine, (2) read the project
> agent-instructions file, (3) read `sdlc-studio/reviews/LATEST.md` for current
> orientation,
> (4) run `/sdlc-studio status` then `/sdlc-studio hint`, (5) **recall relevant
> cross-project lessons** (`lessons/`, see `help/lessons.md`).

## The rules

1. **The skill is the operating system.** Every substantive change flows through
   it: **CR / RFC → Epic → Story → code plan → code implement → code verify →
   reconcile → review.** Even a small bug fix gets a `bug` file (rationale +
   `Verify:` expression + audit pin). No ad-hoc coding, even under time pressure;
   the only exception is a genuine production hotfix – and even then, file the bug.

2. **RFC vs CR vs ADR – pick the right artifact.** Unsettled design (≥2 options or
   open decisions, often cross-repo) → **RFC** (explore → decide → spawns CRs).
   A clear change → **CR** (propose → action into epics). A decision already made →
   **ADR** in the TRD. If you're writing "Option A vs B" or "TBD" in a CR, it should
   have been an RFC.

3. **Files are truth; indexes are derived.** `_index.md`, PRD §3, TRD §6 rows,
   capability lists – all derived from file headers + code. Drift accumulates
   silently. **`reconcile` mechanically propagates; `reconcile --verify` is the
   executable AC gate; `review` is the human-judgment cross-doc check.** Reconcile
   from a **file census** – detect *missing rows* (a file with no index row) and
   *orphan rows*, and recompute counts from the census; never adjust totals blind.

4. **Reconcile cadence – non-negotiable.** Run `reconcile` after: closing an epic,
   actioning a CR, tagging a release, ANY manual status edit, and every 7 days as a
   backstop. Cutting this corner costs more downstream (it always surfaces as a
   same-day drift discovery).

5. **`reconcile --verify` before every release tag.** Executes each story's
   `Verify:` DSL; fails the gate on any `no`/`stale`. This is what makes "Done" mean
   done. Author a `Verify:` line on every AC.

6. **Full review set between releases – including a CODE leg.** A fast ship train
   accumulates drift that mechanical reconcile and doc-only review both miss. Run
   **all legs (PRD · TRD · TSD · Persona · CODE)**, ideally fanned out as parallel
   review subagents, then triage + FIX findings before new feature work. The CODE
   leg is non-negotiable – reconcile/doc-review will never find a crash bug, a
   deploy gap, or an untested hot path.

7. **Consult before freezing a design.** Three Amigos (`consult team`) on any epic
   or story design; add the live stakeholders when the artefact touches the running
   system. Concerns are advisory (record them); only a hard technical blocker stops.

8. **Default to TDD.** Author the `Verify:` expression / failing test first → green
   → refactor. Skip only for pure config/templates/docs. **Generated specs are
   migration blueprints, not documentation** – they MUST be validated by tests, and
   a generated artifact never auto-promotes to Done.

9. **Ship paperwork in the same commit as the code.** The structured tables (PRD
   feature inventory, TRD rows, capability lists) ARE the contract; the changelog is
   the audit trail. Never grow the agent-instructions file (`AGENTS.md` /
   `CLAUDE.md`) with per-ship narrative – that's what
   `git log` + spec detail blocks + `LATEST.md` are for.

10. **Query current API docs before using any library.** Training data is stale;
    verify current signatures before writing against a dependency.

11. **Consult `lessons/` before substantive decisions; promote what generalises.**
    The skill carries a cross-project lessons-learned folder. Recall relevant ones
    before deciding; when you learn something that applies beyond this project,
    promote it (`lessons add --global`). Project-specific facts go in the project's
    memory, not the cross-project folder.

12. **Don't stop mid-execution once a plan is approved.** The SDLC's own gates ARE
    the review (consult, verify, test, check, reconcile). Run each wave through to
    ship + reconcile. Stop only on: a genuine technical blocker the SDLC can't
    resolve, an explicit operator pause, or a destructive / hard-to-reverse action
    (force-push, branch/table deletion, sending external messages).

13. **Cross-repo artifact numbers.** If the CR/RFC namespace is shared across repos,
    `git fetch` and check the highest number on `origin/main` (not just the local
    tree) before assigning one; on collision renumber the unshipped / lower-priority
    side, and compare the *contracts*, not just the numbers.

14. **State files are precious.** `sdlc-studio/.local/{workflow,review,reconcile,
    project}-state.json` track resumable state – don't delete them; reconcile updates
    them.

## What is NOT in this doctrine (stays project-specific)

Architecture and design principles · config/secret handling specifics · deploy &
CI recipes · language/code-style rules (e.g. "no `any`", error shapes) · the
agents/services/topology · house language (British/American). Capture those in the
project agent-instructions file (`AGENTS.md`) + TRD. This doctrine + those specifics
together = a fully
onboarded Claude.
