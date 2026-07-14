# Sprint Reference - Goal-Driven Development loop

<!-- Load when: /sdlc-studio sprint - the autonomous delivery loop -->

`sprint` runs **Goal-Driven Development**: you set the goal and the acceptance
criteria, the loop drives the proven SDLC lifecycle to it. It is a prioritised
batch of work delivered to a goal - a sprint, run by an agent. The decisions
below are settled in the design home (D1-D7).

## Precondition - a runnable gate (cold start)

The loop (implement -> test -> gate -> critic -> commit-green) leans on a quality gate it
can **actually run** each iteration. On a greenfield repo that gate does not exist yet, so
sprint cannot bootstrap itself. **Do not invoke sprint before the gate is runnable
and green.** The canonical greenfield handoff: build the **foundation epic by hand** to a
green gate (the toolchain + test harness - an in-memory substitute like `pg-mem` is enough;
the gate need only run - and the conventions every later story inherits), commit it, *then*
hand subsequent epics to `sprint --epic EPxx --goal done`. See `help/getting-started.md`.

## Invocation

```bash
/sdlc-studio sprint <batch>  --goal done   [--order priority]

  <batch>   --worklist <file> (a tranche file: unit ids one per line, markdown
            bullets/comments tolerated), OR status queries: --bugs <status> |
            --crs <status> | --stories <status> | --epic EP00xx. The status
            queries are COMBINABLE - `--bugs Open --crs Proposed` is one merged,
            dependency-waved mixed tranche (the common backlog-clear sprint),
            and --write persists that merged plan.
  --goal    triage | plan | design | done     (default: done)
  --order   priority (default) | wsjf | manual
```

Natural language resolves to the same: "do an sprint to deliver all open bugs"
-> `sprint --bugs open --goal done`.

**One weight scale across types.** In a mixed tranche, bug `Severity` and CR/story
`Priority` (either the `High/Medium/Low` or the `P1-P4` form) order on one
documented rank: `Critical`/`P1` = 0, `High`/`P2` = 1, `Medium`/`P3` = 2,
`Low`/`P4` = 3 (unknown values rank Medium; matching is case-tolerant). Cross-type
`Depends on` edges (a CR depending on a bug) order and wave like any other edge.

**Conformance is story-scoped.** `conformance.py check` judges stories only; a
bug/CR tranche carries no per-unit conformance verdict and relies on the
independent critic plus the gate - the check's output states this scoping.

## The loop

0. **Reconcile before plan.** `scripts/sprint.py plan` runs `reconcile detect` first
   and surfaces index drift (warns; refuses under `--strict`) - the plan reads each unit's file
   `Status`, so a stale index misleads selection. Mechanical drift only; **semantic** staleness
   (a unit whose feature shipped under a different artifact) still needs the audit + grooming.
1. **Define the batch.** `scripts/sprint.py plan <query> --order <order>`
   returns the dependency-ordered, priority-sorted worklist (the triage plan).
2. **Tranche audit (pre-flight).** `scripts/audit.py check <query|--ids>` grooms the
   batch for readiness *before* the triage STOP, so work never starts on a unit that
   would pass the downstream gates vacuously. Per unit it flags, deterministically,
   **weak-AC** (no checkable AC or the tautology placeholder), **unmet-deps** (a
   `Depends on` referent not yet delivered - a referent that sits in the SAME batch
   is the planner's waves doing their job and reports as informational
   `sequenced-in-batch` instead), **already-terminal** (close it, do not
   re-work), and **link-integrity** (reuses `scripts/integrity.py`). Not-ready units
   are sharpened, closed, or flagged-and-deferred; findings go to the decisions
   ledger. The adversarial "is the problem still real, the change still sound" lens
   is model-instructed (delegates to the adversarial audit when built).
3. **Clarify + Triage STOP (D1).** First, batch **every clarifying question** (scope
   boundaries, priority conflicts, ambiguous AC) into one numbered list, answered once.
   Then present the groomed plan + the audit verdict and **stop for operator approval**.
   After approval the loop runs autonomously, re-pausing only on a **material issue**
   (scope change, broken interface/contract, contradicts a triage answer, no safe
   reversible default).
4. **Per unit, in order:**
   - `cr action` - decompose a CR into stories under an existing epic (a new one
     only if none fits, D-decomposition). Stories carry implementation-ready AC and
     a `Verify:` line. Plans (PL) are not created in agentic mode (D7).
   - **Plan-review gate (schema v3, before implementation).** A story with spec-derived
     ACs cannot enter implementation until an independent reviewer has challenged its ACs
     against the source spec. The trigger is **deterministic** (`plan_review.py`; fires on a
     spec-citation, `affects_files` threshold, or difficulty band - no model judgement in
     fire/skip, TRD ADR-006), so it is not skipped under effort pressure. The reviewer is the
     **QA seat's review render**, a separate instance from the plan's author, working to the
     Plan-Review Charter (`reference-agent-prompt-template.md#plan-review-charter`); it records
     with `plan_review record` (the verdict is pinned to the reviewed ACs by fingerprint, so a
     later AC edit invalidates it). The gate is wired into `transition.py` at entry to In
     Progress/Review/Done; the only sanctioned skip is a recorded `> **Plan-Review-Override:**`.
     This closes the N=5 **R5-inversion** failure - a planner inverted a spec rule in the ACs
     and the delivery critic (whose oracle IS the ACs) approved the wrong plan; a future fixture
     rerun can measure whether the gate catches the seeded inversion.
   - `epic implement --agentic` - implement under **TDD** (failing test first), the
     default. Wraps the existing wave engine (`reference-project.md`); does not
     reinvent it. Each worker is **framed as an amigo seat**, not a generic agent:
     append `persona_resolve.py resolve --seat engineering --render build` after the
     contract (and `--seat qa` for the test author). See
     `reference-agent-prompt-template.md#seat-framing` - the stance never overrides the
     contract, and the reviewer is always a separate seat instance.
   - `verify_ac` - run the AC oracle; back-annotate `Verified:`.
   - **Independent critic (D3), scaled to stakes** - the review depth matches the unit's
     risk, so tokens are spent in proportion. **Independence is the floor, not the variable:**
     the reviewer is always a *separate instance* from the author (the gate proves `reviewer !=
     author`, CR0117); only the *depth* scales:
     - **Code / logic / parser / security / data-loss-risk** -> a full **independent adversarial
       sub-agent** that did not write the diff judges it against AC intent, plus adversarial/mutation
       checks. Reject -> repair.
     - **Pure-doc / template / mechanical / config** -> a **lighter independent review** (a quick
       pass by a different instance), not a full adversarial sub-agent - cheaper, but still not the
       author grading their own work.
     Either way the verdict is recorded with `critic.py record` (committed) with both the **reviewer
     and author ids** and the **tier noted in the issues field**, so the `critiqued` gate requires a
     recorded APPROVE whose reviewer differs from the author - the depth scales, independence and
     honesty never do. When unsure of the risk band, use the full critic.
     **The reviewer is a living persona, not a hand-typed name:** resolve the reviewing seat with
     `persona_resolve.py resolve --seat qa --render review` (product/engineering for their
     domains) and give the critic that framing - the seat's goals and refusal instincts are the
     review lens, and the recorded reviewer id is the seat's name. A hand-typed identity is the
     fallback when no seat card fits, never the norm.
     **Cross-model review is the stronger form of independence:** a separate instance of the
     same model is the floor, but it still shares one model's blind spots - where the
     operator's setup allows it, run the critic seat on a different model or agent runtime
     for high-stakes units. Prompt-level independence catches self-favouritism; cross-model
     independence also catches shared misreadings.
   - `conformance check` - the deterministic gate (`scripts/conformance.py`):
     decomposed -> AC -> tested -> verified -> **reconciled** (no index drift) ->
     **critiqued** (a committed critic APPROVE) -> **documented** (the doc-coverage floor:
     every Type-Reference command catalogued in help, every script in reference-scripts).
     **Hard-fail**: a unit cannot reach Done with a stage skipped - including the
     critic and the docs (D-conformance).
   - **Update the docs in the same unit.** A unit that adds a command/script/flag updates
     its user docs (help catalogue + reference) before it is Done - the `documented` stage
     enforces the floor deterministically; content accuracy is judged by the closing review.
   - Commit the unit green (trunk-based by default, D6).
5. **Stall handling (D2).** After 3 failed green attempts a unit is marked
   **Blocked**, logged, and skipped; the run continues. Blocked units surface in
   `status`. Never thrash; never silently drop.
   **With routing enabled, escalation happens INSIDE that cap**: the first
   `routing.escalation.max_same_tier` (default 2) failed attempts run at the assigned
   tier; the next attempt escalates one declared tier up (`route.py escalate`). A
   repeated identical failure signature at a sub-maximum tier is the "model too small"
   fingerprint - escalate once *instead of* quarantining on the first repeat; the same
   signature repeating again at the escalated tier quarantines as usual. loop_guard's
   arithmetic is untouched - the total attempt budget still bounds thrash
   deterministically. Each escalation appends a ledger entry, and the close records
   `tier_recommended` vs `tier_delivered` + `escalated` in telemetry.
6. **Closing gate - the sprint review.** Every run ends with a mandatory
   `reconcile` (fix any drift) + `review` (the unified PRD/TRD/TSD/persona plus CODE
   review), **regardless of `--goal`**. The review is the sprint review; it produces the
   conformance `reviewed` signal.
   **Mutation evidence first (mechanical, `--goal done` only):** before the retro gate, run
   a bounded `mutation.py run --since <sprint base ref> --test "<the suite>"` (ceiling from
   `quality.mutation_max`) so `sdlc-studio/.local/mutation-report.json` exists for THIS
   diff and the gate's mutation lane reads evidence instead of warning "not run" - a lane
   that always warns trains agents to skim warns. Survivors are findings for the critic
   pass below, not an automatic block (the lane stays advisory in v1). For `--goal design` it reviews the produced
   backlog; for `--goal done` the delivered increment.
   The CODE leg of a `--goal done` close is the **adversarial full-diff critic pass** -
   a sharpening of the per-unit critic step already in the loop, never a second
   parallel gate. Its shape is exact: an INDEPENDENT critic instance (author never
   reviews its own diff) reads the whole sprint diff, framed to REFUTE rather than
   confirm; every finding carries a reproduction; fixes are made test-first (seen
   red against the unfixed code); and the SAME critic instance re-runs its own
   reproductions before recording approve. In the field this pass caught what unit
   tests, per-unit review, and the gate all missed (a closed bug still reproducible
   through a sibling parser; a mutation gate counting unviable mutants as kills) -
   the re-run-your-own-repro step is where those escapes died. **The critic runs
   AS the QA seat's review render** (resolve the card via `persona_resolve` -
   the project's QA seat, or the QA amigo default): the seat's Lens and
   Pushes-Back-When list are its attack angles, and the verdict is recorded
   under the seat so the audit trail reads as the seat's sign-off. `critic.py
   record` warns when the reviewer names no declared seat - the persona lens
   drifting out of the loop must be visible, never silent. Verdicts are
   recorded per unit (`critic.py record`, author != reviewer), which is what the
   conformance `critiqued` stage reads. The closing gate also emits the
   **final report** (items actioned / rejected with rationale / blocked with blocker /
   assumptions / decisions-ledger reference / anything needing the operator).
   On each unit **close** (`artifact close`), a telemetry event (id, type, plus any run
   metrics passed: `--iterations`/`--verdict`/`--wall-time-s`/`--stages`) is appended to
   the committed evidence log `sdlc-studio/retros/evidence/actuals-*.jsonl`. Advisory -
   it never affects the close; it is the measured half of the estimate-vs-actual report.
7. **Retro + lessons lifecycle (a hard gate, not doctrine).** The batch retro carries a 'critic loop, observed' section (findings, refutations, survivors of the adversarial pass) so its value stays visible sprint over sprint. The close runs a five-step learning loop. **Every step of it is mechanical:** one command,
   `gate --require-retro RETRO{next} --require-review`, is the whole close gate, and it fails loud
   (non-zero, no success report) on any of the artefacts being absent or stale. The close is
   reconcile + review + retro: reconcile blocks on drift (the standard gate), `--require-review`
   fails unless `reviews/LATEST.md` is at least as new as every artefact (run `review` to refresh
   it - currency, not mere presence), and `--require-retro` carries the retro + lessons loop below.
   A step that is only described is a step an agent under effort pressure skips - so nothing here is
   only described:
   1. **The retro exists.** The gate fails until the batch retro is in `sdlc-studio/retros/`. Create
      it with `artifact new --type retro --title "..."` so the id is tool-allocated and the index row
      appended (never hand-author either); `reconcile` then covers the retro index for row-presence
      drift like every pipeline type.
   2. **Review + write lessons.** Durable lessons from the wave's `.local/lessons.md` are written
      into the committed retro (delivered, blocked, lessons). Each lesson is stamped with a validity
      horizon when `lessons add` records it.
   3. **Re-validate open lessons - gated.** The gate fails while any open lesson sits past its
      validity horizon, or carries none at all. `lessons revalidate` lists them with their horizon;
      each is then **closed** (`--close L-NNNN`, no longer true), **extended** (`--extend L-NNNN`,
      still true - the horizon moves out), or **stamped** (`--stamp`, the backfill for a log written
      before horizons existed). The log cannot silently grow into unread noise.
   4. **Refresh the rolling summary - gated.** The gate recomputes the digest from the lessons log
      and fails while the committed `sdlc-studio/retros/LESSONS-SUMMARY.md` disagrees with it -
      a lesson **closed** since the last regeneration fails it exactly as an added one does. Fix:
      `lessons summary`. The summary is derived output, like an `_index.md`: nothing is stamped and
      nothing is trusted, so there is no freshness claim to forge - the only way to green is for the
      file to say what the log implies. (Progressive disclosure: the full log stays the archive, the
      summary is what is loaded.)
   5. **Read the summary at the start - emitted, not requested.** `sprint plan` **prints the
      still-valid lessons in the plan itself** (the JSON form carries them all), so the batch an
      agent approves already contains the lessons the last sprints paid for; it does not point at a
      file the agent may not open. It reads the log when there is one and the committed summary
      otherwise (the log is gitignored, so a fresh clone has only the summary). Pair it with
      `lessons recall` for the cross-project tier. Lessons are recorded on the **project tier**
      (`lessons add`, the default); a lesson is promoted with `lessons add --global` only once it
      clearly generalises beyond this repo, and promotion needs `skill_source_repo` set - see
      `help/lessons.md`.

   The lessons lanes ride on `--require-retro` deliberately: the close is ONE obligation, and a
   separate flag per step is a flag that gets forgotten. `gate --require-lessons` runs the lessons
   half alone (a close with no retro due). Deselecting a bound lane (`--skip lessons-summary`) is
   refused, not honoured - a close verdict is never printed over the thing it claims to have
   checked. The retro is a general capability, reused here, not sprint-only.

8. **The handoff - when the run stops SHORT of its goal (a gate, not doctrine).** A run that
   reached its goal owes a retro. A run that stopped for any other reason - budget spent, a unit
   blocked, an operator stop - owes a human one more thing: the single document that says where to
   pick it up. Until it exists, that tail is scattered across hints, the tranche ledger and the
   retro, and the person joining an unattended run has to reconstruct it.

   ```bash
   handoff generate --title "<what this run was>" --outcome budget-spent --retro RETRO{this}
   gate --require-retro RETRO{this} --require-handoff HO{this}
   ```

   `handoff generate` is a JOIN over evidence the run already produced (loop-state, verify-report,
   the tranche audit, conformance, the run state) - it invents nothing. It names **every**
   non-terminal unit with a pointer to start from (the failing AC, the check it stalled at, the
   blocker, or the file), tags each `copilot-tail` or `judgement` with the reasons that produced the
   tag, records the open decisions, links itself from the retro, and emits
   `.local/handoff-worklist.txt`. The next run reads that back with the documented batch source -
   `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt` - and `sprint plan` surfaces the
   pending handoff unasked, so the tail is not a file someone has to remember to open.

   `gate --require-handoff` fails unless the handoff exists AND a retro links it: a handoff nobody
   links is a document nobody reads, and presence alone would certify exactly that. Deselecting the
   bound `handoff` lane is refused, like every other bound lane.

   **The run object.** `sprint plan --write --goal <rung>` opens the run in
   `.local/run-state.json` (id, start time, approved batch, goal); the handoff closes it with its
   outcome (`goal-reached` / `budget-spent` / `blocked` / `stopped`). A run nobody opened still gets
   a handoff - it says the run was not opened rather than inventing a start time.

## Definition of Done

A tranche is Done when (aligned to the operator's orchestrator discipline):

- every worklist item is **implemented, raised** as a tracked CR/bug, or **explicitly
  rejected/blocked** with rationale (verified against source of truth - "partly done" is
  not "done");
- all sdlc-studio artefacts are complete + internally consistent (`reconcile` drift 0);
- a **reconcile-and-review** pass ran against main with the full suite + **gate** green;
- **user and operator documentation updated** to reflect the changes - the deterministic
  doc-coverage floor (`documented` stage) plus review-judged content accuracy;
- a **final report**: items actioned / rejected (rationale) / blocked (blocker named) /
  assumptions / decisions-ledger reference / anything needing the operator afterwards.

A unit-level Done is the per-unit conformance gate (decomposed -> ... -> documented), all green.

## Goals

The goals are **cumulative stop-points** - how far the loop drives. Natural language maps to
the furthest named rung ("plan the next sprint" -> `plan`; "plan **and break down**" ->
`design`; "run it" -> `done`); the operator need not name the flag (NL resolution).

| `--goal` | The loop stops when... | Output | Operator phrase |
| --- | --- | --- | --- |
| `triage` | the plan is approved | the ordered worklist (readiness of the given batch) | - |
| `plan` | a sprint-sized batch is selected + sequenced + estimated | a committed **sprint plan** | "plan the next sprint" |
| `design` | every unit is decomposed to Ready stories with AC **and story points** | a reviewable, estimated backlog | "break it down, make it ready" |
| `done` | every unit is implemented, verified, conformant, reviewed | the delivered increment | "run the sprint" |

### `--goal plan` - sprint planning

From a backlog, **select** a sprint-sized batch (capacity / budget fit), **sequence** it by
dependency, and **size** it - reusing `--order wsjf` + the measured batch rate and `project plan`'s dependency order + wave estimation. `sprint.py plan --write`
persists the sprint-plan artifact; then stop for review. (Distinct from `triage`, which grooms
the *whole given batch* for readiness; `plan` selects a sprint's *worth*.)

**Dependency waves.** For `priority`/`wsjf` order, the plan emits **waves** - the
dependency levels - alongside the flat order: wave 1 is the units with no in-batch dependency,
wave *n+1* is everything whose deps all sit in earlier waves, and units in one wave are
independent (parallelisable). `plan --write` persists them, so the operator no longer hand-derives
the L1/L2/L3 structure; `--agentic` execution runs these same levels as its waves.

The waves are only as real as the declared `Depends on:` metadata. When the batch is >1 unit
and **no** in-batch `Depends on:` is declared, the planner collapses to a single flat parallel
wave - which means "no one declared a dependency", not "no dependencies exist". In that case
`plan` prints a hint naming the missing `Depends on:` field, so a flat list is not mistaken for a
genuinely independent batch. The fix is to declare the dependencies (the `--goal design` rung
below), then re-plan.

**Shared-file clusters.** A `Depends on:` edge is a *declaration*; a shared file is a *fact*. The
planner therefore also derives clusters from the `Affects` it already parses: units touching the
same file are **one cluster**, not independent parallel work, and a wave holding more than one
member of a cluster is called out as NOT safely parallel (run them in sequence, or declare the
edge so the waves say so). Without this the planner reported two units as safely parallel while
both rewrote the same module.

**Scope by epic.** A sprint is usually the next epic or two, not a whole status class, so
`plan --stories <status> --epic EPxxxx [--epic EPyyyy]` restricts the batch to stories in the named
epic(s) - repeatable, union. Without it, `--stories Draft` selects every Draft story across all
epics (the friction that forces hand-scoping). Dependency ordering, `--write`, and WSJF all operate
on the scoped batch. Epic-scoping is story-only (it errors with `--crs`/`--bugs`).

**Seat-scored WSJF.** Sprint planning is a value/effort/risk judgement, not a bare
priority sort. At the plan rung, consult the review seats - **Product Owner** for value
(+ time-criticality, risk-reduction), **Engineering** for effort (an optional `size` per unit -
story-point scale - which OVERRIDES the complexity seed), **QA** for risk - and write their
scores to `sdlc-studio/.local/wsjf-inputs.json`
(`{<id>: {value, time_criticality, risk_reduction, size?}}`). Without a seat size the score
divides by the declared neutral default - never by the complexity signal, which measures the
cognitive complexity of the EXISTING files touched (blast-radius RISK, kept as the
within-priority tiebreak and the token-budget input, not effort: a one-line fix in a complex
file is not a big job). Unknown effort is never treated as minimal. `sprint plan
--order wsjf` then orders by
**WSJF = (value + time-criticality + risk-reduction) / size**, recording the components in the
sprint-plan artifact. With no seat inputs (or `--skip-personas`) it degrades gracefully to
priority + complexity. The seat consult is the isolated-subagent consult; the planner
math is deterministic.

### `--goal design` - establish the dependency graph

Grooming a backlog Draft -> Ready is also where the **inter-story dependency graph** is
established. As each story is sharpened, declare its `Depends on:` against the sibling stories it
truly needs first - a story that consumes another's schema, endpoint, or migration depends on it.
This is model-instructed grooming: read the story prose, decide the real ordering, and write the
`Depends on:` field by construction so a designed backlog already carries the graph the planner
needs. Without it, `plan` degrades to a flat single wave and only the prose holds the W1-W4
sequence - the hand-derivation the waves feature exists to remove. Declare the edges at design,
and the existing wave computation produces the real levels at plan.

## The breakdown gate - `plan` refuses an ungroomed batch {#breakdown}

Grooming has to be **unavoidable**, so it is enforced in the command people actually invoke.
A separate breakdown step nobody runs is doctrine, and doctrine is what gets skipped under
effort pressure: the `--goal design` rung above is *specified* to produce a reviewable,
estimated backlog, and in practice a backlog reaches `plan` ungroomed anyway. So `plan`
itself is the gate.

**A unit is groomed when it declares both:**

| Field | Why the planner cannot work without it |
| --- | --- |
| `Affects:` | The files the unit will touch. Nothing can see that two units touch the same file - so the planner reports them as safely parallel when they will collide - and nothing can order the batch by blast radius. It does NOT price the unit: no plan-time signal predicts a unit's cost well enough to try (see the token forecast below). |
| a size | `Effort: S\|M\|L` (bug/CR - the job size of the work, not its urgency), or `Points:` (story), or a review-seat score in `sdlc-studio/.local/wsjf-inputs.json`. Without one, WSJF divides by a neutral default and the "estimate" is a placeholder wearing an estimate's clothes. |

**Refused, not warned.** With any ungroomed unit in the batch, `sprint plan` exits non-zero and
prints **no plan at all**: it names each offending unit, says what it lacks, and names the
command that fixes it. A plan over unsized units is exactly the false authority the gate exists
to abolish, and an advisory lane is the one that gets scrolled past.

**The escape is a recorded decision, never an omission.** An operator who knowingly accepts an
ungroomed batch sets `sprint.breakdown: judgement` in `sdlc-studio/.config.yaml`; the lane then
REPORTS and does not block. With no config at all the gate BLOCKS, and an unknown mode falls
back to `enforce` - the same shape as the engagement floor and the lessons loop.

**Decompose a CR into stories where the work warrants it.** Only a story carries executable
`- **Verify:**` lines, so an un-decomposed CR reaches Done on prose alone. The plan flags a CR
that is declared Large, or touches five or more files, and that no story yet cites: run
`cr action CR....` to cut it into stories whose Done is gated on real verifiers.

`sprint.py breakdown --crs Proposed` (also `--bugs`/`--stories`/`--worklist`) reports the same
census read-only - ungroomed units, shared-file clusters, decomposition candidates - so a
backlog can be groomed against exactly what the gate reads. It never blocks and never writes.

## Authoring mode - greenfield, from a PRD

The batch source can be a **PRD** instead of existing units: `sprint <prd.md>
--goal design` drives **PRD -> epics -> stories** to a reviewable, estimated backlog, then
stops - never implementing (that is a later `--goal done`). It reuses the existing generation
core (`epic`-from-PRD + `story`-from-epic + `cr action`), not a parallel path (D5).

1. **Decomposition phase.** Decompose the PRD into epics, then each epic into Ready
   stories created through the **batch** path - so ids, slugs, filenames, epic links,
   and indexes are wired by construction and delegated agents fill content only.
2. **Two STOPs.** (1) Present the **epic cut** (count, titles, PRD-feature mapping) and
   stop for approval before any story is authored. (2) Surface the PRD's **open questions** -
   the operator answers, or the assumptions are recorded (`decisions.py promote`) -
   before story authoring. Under `--autonomous` both become record-the-assumption-and-proceed
   (logged to the ledger), per the autonomy ceiling - never silent.
3. **Story points at `design`.** Each story gets a `**Story Points:**` estimate (seeded
   from the complexity signal); `reconcile fields` projects them into the index - no
   hand-copying.
4. **Test-spec bridge authored at design.** Author each epic's **test-spec** with its
   **AC Coverage Matrix** - every story AC mapped to a *planned* test case/title - and write the
   stories' `Verify:` lines as runner-targeted DSL pointing at those planned titles (or `manual`
   where no runner can run the AC). This shifts the AC↔test bridge **left**: implement
   then binds tests to the matrix by construction instead of reverse-engineering the mapping and
   repointing dozens of Verify lines at delivery time. Epic scope (single-story exempt).
   The test-spec the Done-gate / `epic-ts` requires is thus produced here, not
   discovered missing at Done.
5. **Closing consistency pass.** The closing gate runs `ac_scope` (cross-epic
   AC references), `reconcile`/`reconcile fields` (drift 0, index derived), `validate` (0
   errors), `integrity` (every epic link resolves), `verify_ac lint` (no non-executable Verify
   lines), and `ts-check` over the test-spec authored in step 4. Structural failures
   block the "reviewable backlog" sign-off; advisory findings are reported. This is the check
   that replaces the operator as the structural coordinator.

## Guardrails

- **Never deploys.** `deploy` is a stop-condition (hard-to-reverse) action: the loop may prepare up
  to "gate green, artefact ready" and **hand back**, but it never runs `/sdlc-studio deploy` and the
  triage approval never authorises a production rollout. Deploy is operator-triggered and
  interactive, always.
- **Deterministic** (the model cannot skip them): the iteration cap, the
  repetition-breaker, the completion oracle, the **appetite breaker**
  (`scripts/loop_guard.py`), and the **conformance check**
  (`scripts/conformance.py`).
- **Model-instructed:** the autonomy ceiling and escalation policy.
- **Decisions ledger (D4):** a committed, append-only per-tranche log
  (`scripts/ledger.py` -> `sdlc-studio/decisions/<tranche>.md`); survives context
  compaction.

## Autonomous mode (`--autonomous`)

The default loop runs autonomously after the triage STOP but leaves the
cap/repetition/completion judgements to the model. `--autonomous` hands those three
to the deterministic scripts so an unattended overnight run cannot thrash, silently
drop a unit, or declare itself done early:

- **Per failed attempt:** `loop_guard.py record --unit <id> --signature <test::name>`
  persists the attempt to `sdlc-studio/.local/loop-state.json` and exits non-zero
  (3) when the unit must quarantine - at the cap (3 attempts) or on a repeated
  failure signature. The loop marks that unit **Blocked** and continues (D2).
- **Every ruling** (a scope call, an interface decision, a quarantine) is appended
  to the `ledger` so a context reset resumes from disk, not a lost transcript.
- **Done means done:** the completion oracle (`is_complete`) passes only when every
  batch unit is terminal (Done or Blocked), never while one is still In Progress.
- **The closing gate is unconditional:** `reconcile` + `review` + retro run at the
  end regardless of `--goal`, producing the conformance `reviewed` signal.

Without `--autonomous` the same guardrails apply as model-instructed policy - the
portable Phase-1 path for tools without the scripts.

## Appetite (the run-level circuit breaker) {#appetite}

A per-unit quarantine bounds one unit; it does not bound the RUN. An unattended run
otherwise has two outcomes only - it finishes, or it fails - with no way to say "spend
this much and no more", which is the precondition for trusting it to go unattended. The
appetite is that ceiling (Shape Up's fixed timebox: appetite is fixed, scope flexes).

- **Declared at plan time:** `sprint plan --write --appetite-minutes N --appetite-units N`
  records the appetite on the run state (either axis, or both; omit for an unbounded run).
  The project default lives in `appetite.*` (`.config.yaml`); the flags override it.
- **Evaluated at unit BOUNDARIES:** between units the loop runs
  `loop_guard.py budget --root .`. It reads elapsed wall-clock from the run's `started_at`
  and the units spent from those now terminal - both deterministic and harness-independent,
  neither self-reported. When the appetite is spent it exits **4** (a distinct code); the
  loop stops cleanly, the current unit is never abandoned mid-implementation.
- **Not quarantine:** budget-exhausted has its OWN exit code (4, vs quarantine's 3) and
  marks nothing - the units keep their true status rather than being flipped Blocked. The
  loop then generates the handoff with `--outcome budget-spent`, which reports the appetite
  declared vs spent vs delivered and names what remains.
- **Never auto-extended:** a spent appetite is not topped up mid-run. Extending it is an
  explicit operator action - a fresh `sprint plan --write` opens a new run with a new
  appetite and a new clock.
- **Tokens are a FORECAST, never a gate:** a script cannot observe token spend, so a token
  ceiling would depend on the actor self-reporting the budget meant to constrain it. The
  plan reports a token forecast, labelled an estimate; the close repeats it. It never
  stops a run.
- **There is no per-unit estimate.** The forecast is the unit COUNT times a measured
  per-unit rate, and it does not claim to tell the units apart. It used to: the seed was
  the blast-radius complexity of the files a unit touched, and measured against 18 units of
  real telemetry it correlated with actual cost at r = +0.03 - no signal at all. Every other
  plan-time signal was then tested; the best reached a leave-one-out r of 0.42 against a bar
  of 0.50, so the per-unit number was dropped rather than re-seeded. **Read the batch
  history the plan prints - what sprints have actually cost - and treat the forecast as the
  weaker number.** A per-unit figure that has never once been right is not a planning input.

## Model-tier routing {#model-tier-routing}

With `routing.enabled` in `.config.yaml` (**advisory - no gate reads a tier**),
the plan stamps each unit with a `tier` + `model` recommendation alongside its always-present
`difficulty` band, and the orchestrator spawns each delivery worker on the recommended model.
The policy, in order:

1. **Band -> tier** from the deterministic difficulty score (`route.py estimate`):
   trivial->tiny, low->small, medium->medium, high->large, extreme->xlarge
   (cutpoints: `routing.thresholds`).
2. **Kind floors** lift below-floor bands: a bug is never routed tiny; a high
   churn-weighted risk band floors at the security floor (default medium). The
   orchestrator may additionally flag a unit security/data-loss by judgement - that
   flag floors at medium too.
3. **Low confidence bumps up one tier** - two or more unresolved signals mean the
   score is a guess, and a too-small model risks quality where a too-large one only
   costs money.
4. **The critic is never a smaller tier than the author** (`routing.critic_tier`:
   `match` floors code units' critics at medium; `above` lifts one step). Independence
   (reviewer != author, CR0117) stays the enforced floor regardless of tier.
5. **Scope: code-delivery workers only** (build, test, per-unit critic). The
   orchestrator itself, the closing-gate adversarial critic, and authoring/design
   workers always run at the session's own model.

The recommendation is advisory: the orchestrator may override it, and **an override is
recorded in the decisions ledger** so tier_recommended vs tier_delivered stays auditable.
The prompt contract is byte-identical across tiers
(`reference-agent-prompt-template.md#tier-routing`) - if a unit only succeeds on a bigger
model because the contract was vague, fix the contract. Escalation on failure is defined
in loop step 5; per-tier escape/escalation rates accumulate in telemetry
(`telemetry show --summary`, the `by_tier` block) and are the calibration signal for
`routing.thresholds`.

## Scripts

| Script | Role |
| --- | --- |
| `scripts/sprint.py plan` | select + order the batch (the triage plan); emits the still-valid lessons digest; REFUSES an ungroomed batch |
| `scripts/sprint.py breakdown` | the read-only grooming census: ungroomed units, shared-file clusters, decomposition candidates |
| `scripts/lessons.py` | `revalidate` (close/extend/stamp by validity) + `summary` (regenerate the digest) |
| `scripts/gate.py --require-retro` | the sprint-close gate: retro present, lessons re-validated, summary current |
| `scripts/gate.py --require-handoff` | the stopped-short gate: the handoff exists and a retro links it |
| `scripts/handoff.py generate` | the run-close handoff: remaining work, per item, with its pointer and suitability tag |
| `scripts/audit.py check` | tranche audit: weak-AC, unmet-deps, already-terminal, link-integrity |
| `scripts/integrity.py check` | referential integrity (required links + dangling refs) |
| `scripts/conformance.py check` | the lifecycle-conformance gate (hard-fail; incl. reconciled + critiqued) |
| `scripts/critic.py record` | the committed independent-critic verdict per unit (D3) |
| `scripts/route.py` | difficulty estimate + tier pick + escalation stepper (advisory) |
| `scripts/loop_guard.py` | iteration cap, repetition-breaker, completion oracle, appetite breaker (`budget`, exit 4) |
| `scripts/ledger.py` | append-only per-tranche decisions ledger (survives compaction) |
| `reconcile` / `review` / `verify_ac` | the closing gate + per-unit oracle (reused) |

## See Also

- `reference-project.md` - the wave engine sprint wraps
- `reference-cr.md` - `cr action` (CR -> stories)
- `help/sprint.md` - command quick reference
