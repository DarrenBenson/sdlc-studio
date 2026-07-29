<!--
Load when: /sdlc-studio sprint or /sdlc-studio sprint help
Dependencies: SKILL.md (always loaded first)
Related: reference-sprint.md (full workflow)
-->

# /sdlc-studio sprint - Goal-Driven Development loop

## You can just ask

SDLC Studio is model-invoked - say it in plain language:

| Just say... | Runs |
| --- | --- |
| "Do a sprint to deliver all the open bugs" | `/sdlc-studio sprint --bugs Open --goal done` |
| "Plan and break down the next sprint, but don't write code" | `/sdlc-studio sprint --crs Proposed --goal design` |
| "Build out epic 7 from end to end" | `/sdlc-studio sprint --epic EP0007 --goal done` |
| "Turn this PRD into epics and stories" | `/sdlc-studio sprint prd.md --goal design` |
| "Select and estimate a sprint, then stop for my sign-off" | `/sdlc-studio sprint --crs Proposed --goal plan` |
| "Run the whole thing unattended" | `/sdlc-studio sprint --bugs Open --autonomous` |

Run a prioritised batch of work to a goal. You set the goal and the acceptance
criteria; the loop drives the proven lifecycle (decompose -> TDD -> verify ->
conformance -> review) to it. Add `--autonomous` to run unattended. See
`reference-sprint.md` for the full workflow.

> **Renamed from `autosprint`.** `/sdlc-studio autosprint ...` still works as a
> **deprecated alias** (the command is now the whole sprint lifecycle - `--goal plan` /
> `design` / `done` - so autonomy is the `--autonomous` flag, not the name). Prefer `sprint`.

## Quick Reference

```bash
/sdlc-studio sprint --crs Proposed --goal done      # deliver the proposed CRs
/sdlc-studio sprint --bugs Open --goal done         # deliver the open bugs
/sdlc-studio sprint --bugs Open --crs Proposed      # one mixed backlog-clear tranche
/sdlc-studio sprint --epic EP0007 --goal done       # deliver an epic
/sdlc-studio sprint --crs Proposed --goal design    # just the backlog (no code)
/sdlc-studio sprint --crs Proposed --goal plan       # select+sequence+estimate a sprint, stop
/sdlc-studio sprint prd.md --goal design             # greenfield: PRD -> epics -> stories
/sdlc-studio sprint <worklist.md> --order wsjf       # a tranche file, WSJF order
/sdlc-studio sprint --bugs Open --autonomous         # unattended: deterministic guardrails on
/sdlc-studio sprint decision defer --unit US0001 --question "..." --option "a|..." --option "b|..."  # set the unit aside, batch continues
/sdlc-studio sprint decision list                    # every accumulated decision, asked together, structured
/sdlc-studio sprint decision resolve --index 1 --choice a   # record the operator's ruling (run state + ledger)
/sdlc-studio sprint close                            # scaffolds the retro, then stops for you to fill it
/sdlc-studio sprint close --retro RETRO0001          # the close ceremony as one command (retro already filled)
/sdlc-studio sprint close --retro RETRO0001 --file-and-close  # bounded exit: file the ceremony debt, close honestly (refused while a hard gate is red)
/sdlc-studio sprint close --retro RETRO0001 --apply-signoff --principal "You"  # fan your approval into per-unit sign-offs + Done
/sdlc-studio sprint plan --cycles 3 --goal done      # a standing policy: roll 3 cycles, regenerating the plan each time
/sdlc-studio sprint boundary --retro RETRO0001       # close this cycle down and open the next from the live backlog
/sdlc-studio sprint report --id RETRO0001             # the end-of-sprint report (the close draws it too)
```

**`/sdlc-studio sprint report --id RETROxxxx`** composes the end-of-sprint report - delivered units
and points, measured cost with rework counted, velocity, estimate-versus-actual, lessons and tickets
raised - from the retro, `retro accuracy` and the telemetry evidence log. Run it once the retro is
filled: after a close, or any time later to re-read what a past sprint delivered and cost. The close
ceremony draws the same page for you, so this is for a sprint you are revisiting or a run whose page
you want in another shape (`--format json`). The close captures an interactive sprint's
harness-tracked token cost itself - this run's DELTA from the baseline stamped when it opened, not
the session total, since one session can hold several sprints and the meter is cumulative. A run
with no baseline reports not-attributable rather than a number, and it states plainly when it
cannot attribute, so `--tokens N` is the manual override and `--elapsed-hours H` supplies the
elapsed the run-state cannot know. Read-only.

**`--apply-signoff --principal "<you>"`** turns the close's decision brief into an action: instead
of hand-running `critic signoff` and `transition` for every unit, one command records your
reviewer-of-record sign-off per story unit, transitions each Done (AC-verify gated, cascading its
parent), then writes the run's velocity row and a final reconcile. Story-scoped (bugs are already
terminal), idempotent (a re-run resumes, skipping already-done+signed units), and it stops loudly at
the first refusal - a principal that is an authoring-session subagent, or a unit whose Done gate is
red - leaving the completed units done. It never runs without an explicit `--principal`.

Natural language works too: "do a sprint to deliver all open bugs"; "plan and break down the
next sprint" resolves to `--goal design` (the goals are cumulative stop-points).

## Flags

| Flag | Description | Default |
| --- | --- | --- |
| `<batch>` | status queries (`--bugs`/`--crs`/`--stories <status>` - **combinable** into one mixed tranche), `--worklist <file>` (ids one per line), `--epic EPxxxx`, or a **PRD path** (greenfield authoring) | required |
| `--goal` | `triage` (plan) / `plan` (sprint plan) / `design` (Ready, estimated backlog) / `done` (delivered) | `done` |
| `--sprint-goal TEXT` | the Sprint Goal - one product-outcome sentence unifying the batch, judged at the closing review (`sprint goal-verdict --verdict achieved\|partial\|missed --note "..."`) and shown on the sprint report. Prompted interactively when absent; never invented | none |
| `--order` | `priority` / `wsjf` (priority over complexity) / `manual` | `priority` |
| `--epic EPxxxx` | (with `--stories`, repeatable) scope a story plan to one or more epics, not the whole status class | all epics |
| `--write` | (with `plan`) persist the sprint plan to `.local/sprint-plan.json` | off |
| `--strict` | (with `plan`) refuse to plan when the index has drift (reconcile-before-plan) | off |
| `--autonomous` | unattended mode: the deterministic guardrails (cap, repetition-breaker, completion oracle) enforce stop/stall instead of model discretion | off |

## One run slot

A project holds **exactly one run at a time**. What planning a second batch while a run is open
does depends on whether it overlaps the open run:

- A batch sharing **no unit** with the open run is **refused, not merged**. Folding an unrelated
  batch into the open run would leave it with one Sprint Goal describing a fraction of the work and
  a closing verdict that could not be given honestly, so `sprint plan --write` exits non-zero and
  changes nothing.
- An **overlapping re-plan** - a re-cut, or a blocker sweep pulling work in - **accumulates** into
  the same run under its unchanged id and start time. This needs no flag; it is the normal way a
  run's batch grows.

When a disjoint batch is refused there are **two ways forward**, and the refusal prints them as
runnable commands:

- **close the open run**, then plan this batch as its own run: `sprint close`
- **or re-plan the open run deliberately**, folding the batch in by planning a worklist that also
  names one of its units: `sprint plan --worklist <file> --write`

A run whose only close artefact is a **failed close attempt** is still open and protected, so it is
covered by this refusal rather than absorbing the next batch silently.

## The breakdown gate

`sprint plan` **refuses** a batch whose units are not groomed: every unit must declare
`Affects:` (the files it will touch) and `Points:` (its size on the modified Fibonacci scale -
one size vocabulary, every unit type). A unit above the split threshold is refused too. Ungroomed,
it exits non-zero and prints **no plan at all** - a
plan over unsized units cannot be sized or safely parallelised, and looks authoritative anyway.
The refusal names each unit, what it lacks, and the fix. `sprint breakdown <batch>` reports the
same census read-only. Opt out only as a recorded decision: `sprint.breakdown: judgement` in
`sdlc-studio/.config.yaml` makes the lane report instead of block.

## What happens

1. **Plan** - `sprint plan` selects + orders the batch, refusing an ungroomed one.
2. **Tranche audit** - `readiness.py check` grooms the batch for readiness (weak-AC,
   unmet-deps, already-terminal, link-integrity) before you approve it.
3. **Triage STOP** - the groomed plan is shown; you approve, then it runs
   autonomously, re-pausing only on a material issue.
4. **Per unit** - `cr action` -> `epic implement --agentic` (TDD) -> `verify_ac` ->
   `conformance check` (hard-fail gate) -> independent critic -> green commit.
   Each ruling is appended to the decisions `ledger` so it survives compaction.
5. **Stall** - `loop_guard` quarantines a unit at the cap (3 attempts) or on a
   repeated failure signature: it is marked Blocked, logged, skipped; the run
   continues. The completion oracle declares the batch done only when every unit
   is terminal (Done or Blocked). With `routing.enabled` (see below), a failed
   attempt escalates one model tier before the cap quarantines
   (`reference-sprint.md#model-tier-routing`).
6. **Pre-flight** (optional, read-only) - `sprint preflight --retro RETROxxxx` reports
   **every** unmet close prerequisite in one pass: the gate lanes, the retro's missing
   sections, an unjudged goal, and the per-unit sign-off prerequisites (critic verdict,
   adversarial evidence, independent reviewer-of-record). Those last ones otherwise
   surface only after the whole chain has passed, so a close took as many runs as it
   had unmet prerequisites, each costing a full gate run. Writes nothing, so it can be
   asked before committing to a close. `close` runs it automatically and prints the
   same list up front; it reports, it never adds a refusal.
7. **Close** - `sprint close` runs the close ceremony as one deterministic chain
   (goal-verdict, retro validate + extract, lessons summary, the close gate, handoff,
   reconcile), stopping loudly at the first failing step with the remedy named, and
   prints the sign-off decision brief. Run it with **no `--retro`** the first time and it
   **scaffolds the retro for you** (allocated id + template + index row, Batch/Goal
   pre-filled from the run), then stops so you fill it; re-run with the id it prints
   (`sprint close --retro RETROxxxx`) to finish. Never hand-author the retro - the
   scaffold is the one path that also wires its index row.
8. **Sprint review** - every run ends with a mandatory `reconcile` + `review`; the
   CODE leg is the adversarial full-diff critic pass (independent instance, refute
   framing, findings with repros, fixes seen red first, the SAME critic re-runs its
   own repros before approve - see `reference-sprint.md`).

In `--autonomous` mode steps 4's guardrails are deterministic scripts the model
cannot skip; without it they are model-instructed (the portable Phase-1 path).

**Model-tier routing (opt-in):** with `routing.enabled` in `.config.yaml`, the plan
stamps each unit with an advisory `tier`/`model` recommendation (difficulty-scored by
`route.py` from complexity, scope, novelty and spec size), so cheap units run on your
smaller model and hard ones on your bigger one. Map tiers to your own models in
`routing.models`; see `reference-config.md#routing`.

## How big should a batch be

There is a trade-off, and no number is prescribed for it. The fixed per-sprint cost - the
ceremony, the one close, the review setup - is spread over the batch's points, so its share
per point falls as the batch grows. Review convergence cost pulls the other way: a bigger diff
carries more surface and more findings, so it takes more rounds to converge. Both directions
show in this project's own measured history (the eight build sprints in `retros/VELOCITY.md`
that carry a measured tokens/pt), but the sample is small and noisy and the arms point opposite
ways, so it fixes no optimum. Picking a batch-size number off this few measured sprints would
invent a target the data cannot defend. Read `retro.py velocity` and decide per batch.

## The review point: `review-batch`

The adversarial review runs at the DELIVERY BATCH BOUNDARY, not at the close. Where it runs
decides what its findings cost: at the close, every defect it finds is close work by
definition. At the batch boundary, the same defect is delivery work in the batch that caused
it, priced there, and fixed by a context still holding it.

Open a span over the units a batch will land, and review it when the batch is committed:

```bash
# open the span as the batch starts
sprint.py review-batch --open US0560,US0561,US0562,US0563

# ... deliver ...

# record the INDEPENDENT pass and close the span
sprint.py review-batch \
  --reviewer "the fresh context that did not write this" \
  --author   "whoever wrote it" \
  --verdict  APPROVE \
  --findings "what was probed, and what was found - 'none blocking' is a finding"
```

`--units` overrides the span's unit set; without an open span it is required, because a
review must name what it covers rather than guess. Reviewer and author must differ - a
self-review is the context that wrote the code agreeing with itself, and it clears nothing.
A `REJECT` is recorded (the range WAS reviewed) but clears no gate.

Any finding filed while a span is open is stamped `Raised-in-batch` and recorded against that
span, so a sprint can report where its defects were found. Filed with no span open, the
artefact says so rather than being attributed to the last one.

`sprint close` refuses a batch carrying units no independent pass covered, and names them:
**the close asserts that coverage exists, it does not perform the review.**

## Prerequisites

- A batch to run (CRs/bugs/stories on disk, or a worklist file).
- The scripts: `sprint.py`, `conformance.py`, `ledger.py`, `loop_guard.py`,
  plus the reused `verify_ac`, `reconcile`, `review`.

## See Also

- `reference-sprint.md` - full workflow and guardrails
- `/sdlc-studio sprint report --id RETROxxxx` - the end-of-sprint report, composed from the
  retro, the accuracy pass and telemetry (`report.enabled: false` turns the page off)
- `/sdlc-studio status` - shows Blocked units after a run

## Lanes: dispatching work and accepting it back

A delivery lane is dispatched with a brief and accepted back with evidence. Both are commands, so
the obligations travel with the work rather than with whoever wrote the prompt.

```bash
sprint lane brief  --units US0123 US0124     # the contract, the obligations, the proof owed, the carried lessons
sprint lane return --units US0123 --proof unit="<evidence>"   # runs the unit's OWN criteria and reports each
```

`lane brief` **refuses** a unit that carries no authored acceptance criteria, or criteria the
verifier cannot read, and exits non-zero naming it. There is nothing to deliver against, and a
contract inferred from the summary is the lane's guess rather than the unit's specification.

`lane return` runs every executable criterion and reports each with the runner's own output and
exit code, not a summary. It forces the outcome to `blocked` whenever a criterion did not pass,
**whatever the lane claimed** - a lane cannot inflate its own result. An unresolvable selector is
reported `unresolved` and blocks: an unanswerable check is not a passed one. Shell verifiers obey
the same provenance rule the authoritative runner uses, so an externally ingested artefact cannot
reach a shell through this path either.

An orchestrator should call `lane brief` before dispatching and `lane return` before accepting a
lane's work. Skipping them is how a unit with no contract reaches Fixed.
