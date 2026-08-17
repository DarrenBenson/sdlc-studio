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
   lane, and deselecting it under `--release` is refused rather than honoured. A red AC blocks
   when its story CLAIMS completion - a failing criterion on `Ready`, `Superseded` or
   `Won't Implement` work was never claimed finished, so it is reported with its status rather
   than counted, and any status the vocabulary cannot resolve counts as a claim. This is what
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

   **A lane writes a FRAGMENT, never the `[Unreleased]` section.** One file per unit
   under `changelog.d/`, named for the unit, with a `<!-- section: Added|Fixed|... -->`
   marker. `changelog compose` folds the fragments at the release cut. This is the rule for a
   lane because `[Unreleased]` is one region of one file: two lanes editing it collide,
   and the collision surfaces as a merge conflict in the paperwork rather than in the
   work. Editing `[Unreleased]` directly is a RELEASE step, not a delivery step.

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

18. **The adversarial review sits at the delivery batch boundary, not at the close.**
    Where the review runs decides what its findings COST. Run it at the close and every
    defect it finds is close work by definition: it arrives after the sprint is nominally
    over, is repaired fast and late by whoever is still holding the context, and lands in
    the most load-bearing code in the project. One measured run here delivered in five
    hours and took six and a half to close, of which only about 18% was gate and suite
    time - the rest was repair generated by a close-time review. A human sprint that spent
    two weeks delivering and two weeks closing would not survive the quarter.

    So the review point is the batch boundary the project already commits on. Reviewed
    there, a finding is delivery work in the batch that caused it, priced against that
    batch, and fixed by a context that still holds it. Record the pass with
    `sprint review-batch --reviewer <who> --author <who> --verdict APPROVE --findings
    "<what was probed>"`; reviewer and author must differ, because a self-review is the
    context that wrote the code agreeing with itself. `sprint close` then REFUSES a batch
    carrying units no independent pass covered, and names them: **the close asserts that
    coverage exists, it does not perform the review.** A repair written in response to a
    finding is itself covered by a later batch review - repairs are the least-reviewed
    code in any sprint and they land in guards.

19. **A review judges the unit's own diff, and only what the unit broke may block it.**
    The scope of a review is that unit's declared `Affects` against the run's base ref -
    `git diff <base>..HEAD -- <the Affects paths>` - and nothing wider. Every finding is
    then classified by whether this unit caused it: a **regression** (the diff broke
    something that worked), **new** (the diff introduced a defect that did not exist), or
    **pre-existing** (already true of the tree at the base ref). Decide which by execution,
    `git log -S` or a re-probe at the base commit, never by impression.

    **Only regression and new may hold the gate.** A pre-existing finding is reported with
    its classification and its artefact id, and does not block. Anything already recorded
    in an open Bug or CR is pre-existing by definition, so cite the id rather than
    rediscovering it.

    Without the bound, a review of a five-point unit becomes an audit of the repository,
    and the gate stops being passable by any correct increment. That is not strictness; it
    is a review that has stopped discriminating, because a verdict that fails every unit
    carries the same information as one that passes every unit. The scope rule is what
    makes a REJECT mean something: it says this change made the tree worse, not that the
    tree has problems. An unjustified REJECT is as much a failure as an unjustified
    APPROVE, and only a bounded review can tell the two apart.

20. **A finding surfaced during a close is FILED and deferred, never repaired inline.**
    The close writes an account of the batch and then stamps the ledger that says the batch
    is accounted for. Anything reaching a terminal status after that stamp is, by
    construction, unaccounted - so a repair made *inside* the ceremony invalidates the
    account written moments earlier and re-opens the ledger the close just satisfied.

    The failure this produces is not an error message. It is a close that appears never to
    finish: every mechanical check passes, the run reads closed, and the ledger still says a
    close is owed. One run hit it twice in a single close, and the reading from outside was
    that the sprint was never being closed. It was - repeatedly - and each close was undone
    by the next repair.

    So the ceremony has a **fixed point**, and it is gated rather than asked for:
    `sprint close` and `sprint stop` both refuse while the working tree carries an
    uncommitted change to a file one of the batch's own units declares. The refusal names
    the unit, the path, and the two ways out - commit it as batch work before the ceremony
    starts, or file it and let the next run carry it. Scoped to the batch's own declared
    surface, never to any dirty file: a guard that stopped every close over an unrelated
    edit would be switched off within a sprint, and then it would guard nothing.

    This punishes no instinct worth keeping. Finding a defect during a close is what a
    careful close is *for*; the rule is only about where the repair lands. Filing it loses
    nothing and keeps the account true, and the close-owed ledger reports a repair that
    still had to happen as a close-time repair rather than as work nobody accounted for -
    visible and countable, without holding the gate.

21. **A fix's author is not sufficient evidence for that fix.** {#repair-evidence}
    Every other kind of change is held by a test written before anyone knew which way the
    implementation would go. A repair is not: the defect is already understood, the fix is
    written fast under the belief that understanding is complete, and the test is written
    afterwards by the person who just decided what the answer is. It is the most
    defect-dense work in a sprint and the only work whose evidence is authored with the
    answer already in hand.

    So a repair carries evidence its author could not have manufactured: a mutant applied to
    the repair's own changed lines, and the repair's test observed to fail on it. A test that
    cannot fail on the change it guards is not evidence about that change - it is evidence
    that somebody wrote a test. The distinction is invisible in a green suite and it is
    exactly the distinction that matters here.

    This is mechanised, and what the mechanism DOES is the project's choice. On a terminal
    transition `transition.py` runs `mutation_evidence_lane`, which composes
    `repair_mutation_gate` over the repair's recorded evidence and `verify_no_surface_claim`
    over any exemption it claims. `review.mutation_evidence` decides the consequence:

    + **`report`, the default.** A survivor becomes a severity-rated bug in the backlog and
      the transition proceeds. A team then decides in its next sprint whether to fix it or
      live with it. A gate that turns every survivor into an immediate stoppage is one that
      gets switched off wholesale, and then it holds nothing.
    + **`block`.** No evidence, stale evidence or a survivor refuses the transition. Set this
      if your project wants what earlier versions described. The demand is now derived from
      the DIFF against the run's base ref, not from the unit's declared `Affects`: a
      declaration can only ever SHRINK the derived surface, so a unit that declared a surface
      it did not change used to escape the demand entirely. It no longer does.

      **This mode requires an open run.** Deriving from the diff means there must be a base
      ref to diff against, so under `block` a repair transitioned with no run open is refused,
      naming that as the reason. The refusal is deliberate rather than incidental: a
      derivation that cannot run yields no surface, and no surface is indistinguishable from
      nothing to mutate - which would put the fail-open back within reach of anyone who simply
      did not open a run. If your project transitions repairs outside a run, stay on `report`,
      where the same condition is reported and the transition proceeds.
    + **`off`.** The lane stands down.

    Two things ignore the setting. A claimed exemption re-derived and found FALSE refuses in
    `report` too, because that is not a bar being applied - it is a written claim shown to be
    untrue. And a ledger recording one mutant as both killed and survived refuses in every
    mode including `off`, because `off` says evidence must not hold your transitions, not that
    the instrument may lie: every figure derived from a false verdict is wrong, and nothing
    downstream can tell.

    **If you installed an earlier version and read this rule as a refusal, it no longer is by
    default.** Set `review.mutation_evidence: block` in `sdlc-studio/.config.yaml` to keep the
    bar you were promised. A project that sets nothing gets `report`. Saying so here is the
    point: a documented refusal quietly becoming a documented report lowers a bar on somebody
    else's project without their knowing, and a rule that changes direction owes its existing
    readers the sentence that tells them.

    A rule stated here with no mechanism behind it is a rule this doctrine is explicit about
    distrusting - so the mechanisms are named above, and a guard asserts each one is reached
    from the gate ladder rather than merely defined.

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
