# SDLC Studio Operating Doctrine

<!-- Load when: onboarding to a project or applying the operating doctrine -->

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

5. **One command before every release tag: `scripts/gate.py --release`.** The standard gate
   PLUS an executing pass over every story's `Verify:` DSL, failing as ONE exit code and
   naming every red AC. So tagging over a rotted verify layer means ignoring a failing
   command, rather than misreading a passing-looking one - the gate and the verify run are
   no longer two exit codes an operator has to remember to read. The lane **executes** the
   verifiers rather than reading the stored report (a merged report carries a stale green
   forward), and writes nothing back. **Nothing to prove is not proof:** no stories, no
   executable `Verify:` line, or a verifier the trust boundary refused to run all FAIL the
   lane, and deselecting it under `--release` is refused rather than honoured. This is what
   makes "Done" mean done. Author a `Verify:` line on every AC.

6. **Full review set between releases – including a CODE leg.** A fast ship train
   accumulates drift that mechanical reconcile and doc-only review both miss. Run
   **all legs (PRD · TRD · TSD · Persona · CODE)**, ideally fanned out as parallel
   review subagents, then triage + FIX findings before new feature work. The CODE
   leg is non-negotiable – reconcile/doc-review will never find a crash bug, a
   deploy gap, or an untested hot path. For high-stakes units, prefer **cross-model
   review**: a separate instance of the same model is the independence floor, but it
   shares that model's blind spots - a critic seat run on a different model or agent
   runtime also catches shared misreadings.

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

15. **Reach for the script before hand-doing a mechanical task.** The toolbox is
    deterministic and collision-safe: `artifact.py new`/`batch` creates (id + index
    row allocated), `file_finding.py` files a finding, `transition.py` moves status,
    `reconcile.py` syncs, `validate.py check` diagnoses, `verify_ac.py` verdicts,
    `gate.py` gates. The router's "Deterministic Entry Points" card is the quick
    map; `reference-scripts.md` is the full catalogue. Hand-allocating an id or
    hand-authoring an index a script owns is an error, not a shortcut.

16. **The engagement floor: multi-file changes in a spec-bearing repo get the
    planning pass, not a judgement call.** Measured, not asserted: on the base
    models most teams run, leaving pipeline engagement to the model's own
    scale-to-size judgement produced the same defect rate as no process at all,
    while a mandated planning pass cut it by 4-5x at ~1.1-1.2x tokens
    (the skill repository's 2026-07-10 benchmark rerun). So the floor is a rule: when a change
    touches more than one source file in a repo that carries a numbered spec or an
    sdlc-studio workspace, derive the spec delta FIRST - naming every existing
    requirement the change interacts with and how each interaction is resolved -
    and write acceptance criteria (one per interaction) before any code. Judgement
    still scales everything above the floor (a single-file fix in an unspecced
    repo needs no ceremony), and an operator who accepts the risk may opt out with
    `engagement_floor: judgement` in `.config.yaml`. The default is the floor. Where
    an sdlc-studio workspace exists this is mechanically checked, not just asked for:
    the `engagement-floor` gate lane refuses a shipped multi-file unit that carries no
    acceptance criterion, `Verify:` line, or linked plan (see reference-config).

17. **Close the learning loop: a retro must produce work, not just prose.** A team
    that inspects and never adapts is holding a ceremony, not a retrospective. So
    the retro is checked on its CONTENT, not its existence - a gate that tests for
    a file is satisfied by `touch` - and every finding it records takes a
    disposition: **filed** as a Bug or CR, or **declined with a reason**. Both are
    green. Declining must cost exactly what filing costs, or the gate teaches people
    to file rubbish to go green; what is refused is silence, a finding written down
    and left to rot. The lessons a retro records are then lifted into the store
    (`retro extract`), because a lesson that stays in the retro file is read by
    nobody after the sprint that wrote it - and the store is printed into the next
    sprint's plan unasked, including the cross-project registry a new project
    inherits on day one. The reasoning is the engagement floor's: a process step
    gated on judgement is the step that gets skipped. The evidence is not yet the
    engagement floor's, and that distinction is kept honestly - the claim that the
    loop reduces repeat defects is registered as a claim to be measured, not asserted
    as a finding. Opt out with `lessons.loop: judgement`; the lane then reports and
    never blocks. The default is the loop.

## Project constitution {#constitution}

A project may declare its inviolable principles in an optional
`sdlc-studio/constitution.md` (seed from `templates/constitution.md`). It is loaded as a
generation constraint, and `constitution check` (`scripts/constitution.py`)
asserts the **machine-checkable** principles across the artifact graph - a principle
carries a `` `rule:` `` from a fixed vocabulary (e.g. `story-requires-epic`,
`ac-requires-verify`, `status-in-vocab`, `no-index-drift`) that maps onto the existing
integrity / conformance / validate / reconcile checks; principles with no rule are
advisory (loaded, listed, not gated). Enforcement is advisory by default; set
`constitution.enforce: true` in `.config.yaml` to make a violation fail the check. Keep
the set small - the handful of rules that must never be violated, not a style guide.

## What is NOT in this doctrine (stays project-specific)

Architecture and design principles · config/secret handling specifics · deploy &
CI recipes · language/code-style rules (e.g. "no `any`", error shapes) · the
agents/services/topology · house language (British/American). Capture those in the
project agent-instructions file (`AGENTS.md`) + TRD, and the inviolable, checkable ones
in the [project constitution](#constitution). This doctrine + those specifics
together = a fully
onboarded Claude.
