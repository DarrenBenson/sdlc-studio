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
  --goal    triage | design | done            (default: done)
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
   review), **regardless of `--goal`**. This is the sprint review and it produces
   the conformance `reviewed` signal. For `--goal design` it reviews the produced
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
   the gitignored `sdlc-studio/.local/telemetry.jsonl`. Advisory -
   it never affects the close; it feeds the deferred calibrate step.
7. **Retro lifecycle (a hard gate, not doctrine).** The batch retro carries a 'critic loop, observed' section (findings, refutations, survivors of the adversarial pass) so its value stays visible sprint over sprint. The close runs a five-step learning loop,
   each step script-backed so it cannot be silently skipped:
   1. **Hard close gate.** The close runs `gate --require-retro RETRO{next}` and **fails loud**
      (non-zero, no success report) until the batch retro exists in `sdlc-studio/retros/`, mirroring
      the reconcile-drift-0 gate. "Unconditional" is now mechanical, not a habit.
   2. **Review + write lessons.** Durable lessons from the wave's `.local/lessons.md` are written
      into the committed retro (delivered, blocked, lessons).
   3. **Re-validate open lessons.** `lessons revalidate` lists open lessons; the stale ones are
      closed by validity (`lessons revalidate --close L-NNNN`), generalising `prune --older` so the
      log does not grow into noise.
   4. **Refresh the rolling summary.** `lessons summary` regenerates the committed
      `sdlc-studio/retros/LESSONS-SUMMARY.md` from the still-valid lessons - the cheap, high-signal
      digest (progressive disclosure: the full log is the archive, the summary is what is loaded).
   5. **Read the summary at the start.** A new sprint reads `LESSONS-SUMMARY.md` plus `lessons recall`
      at the **start** - not the full log - and surfaces generalisable lessons for `lessons add --global`.
   The retro is a general capability, reused here, not sprint-only.

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
dependency, and **estimate** it - reusing `--order wsjf` + the complexity-weighted budget and `project plan`'s dependency order + wave estimation. `sprint.py plan --write`
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
  repetition-breaker, the completion oracle (`scripts/loop_guard.py`), and the
  **conformance check** (`scripts/conformance.py`).
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
| `scripts/sprint.py plan` | select + order the batch (the triage plan) |
| `scripts/audit.py check` | tranche audit: weak-AC, unmet-deps, already-terminal, link-integrity |
| `scripts/integrity.py check` | referential integrity (required links + dangling refs) |
| `scripts/conformance.py check` | the lifecycle-conformance gate (hard-fail; incl. reconciled + critiqued) |
| `scripts/critic.py record` | the committed independent-critic verdict per unit (D3) |
| `scripts/route.py` | difficulty estimate + tier pick + escalation stepper (advisory) |
| `scripts/loop_guard.py` | iteration cap, repetition-breaker, completion oracle |
| `scripts/ledger.py` | append-only per-tranche decisions ledger (survives compaction) |
| `reconcile` / `review` / `verify_ac` | the closing gate + per-unit oracle (reused) |

## See Also

- `reference-project.md` - the wave engine sprint wraps
- `reference-cr.md` - `cr action` (CR -> stories)
- `help/sprint.md` - command quick reference
