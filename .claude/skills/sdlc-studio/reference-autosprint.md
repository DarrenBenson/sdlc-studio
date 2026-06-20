# Autosprint Reference - Goal-Driven Development loop

<!-- Load when: /sdlc-studio autosprint - the autonomous delivery loop (RFC0001) -->

`autosprint` runs **Goal-Driven Development**: you set the goal and the acceptance
criteria, the loop drives the proven SDLC lifecycle to it. It is a prioritised
batch of work delivered to a goal - a sprint, run by an agent. RFC0001 is the
design home; the decisions below are settled there (D1-D7).

## Invocation

```bash
/sdlc-studio autosprint <batch>  --goal done   [--order priority]

  <batch>   a worklist/tranche file, OR a query: --bugs <status> | --crs <status>
            | --stories <status> | --epic EP00xx
  --goal    triage | design | done            (default: done)
  --order   priority (default) | wsjf | manual
```

Natural language resolves to the same: "do an autosprint to deliver all open bugs"
-> `autosprint --bugs open --goal done`.

## The loop

1. **Define the batch.** `scripts/autosprint.py plan <query> --order <order>`
   returns the dependency-ordered, priority-sorted worklist (the triage plan).
2. **Triage STOP (D1).** Present the plan and **stop for operator approval**. After
   approval the loop runs autonomously, re-pausing only on a **material issue**
   (scope change, broken interface/contract, contradicts a triage answer, no safe
   reversible default).
3. **Per unit, in order:**
   - `cr action` - decompose a CR into stories under an existing epic (a new one
     only if none fits, D-decomposition). Stories carry implementation-ready AC and
     a `Verify:` line. Plans (PL) are not created in agentic mode (D7).
   - `epic implement --agentic` - implement under **TDD** (failing test first), the
     default. Wraps the existing wave engine (`reference-project.md`); does not
     reinvent it.
   - `verify_ac` - run the AC oracle; back-annotate `Verified:`.
   - `conformance check` - the deterministic gate (`scripts/conformance.py`):
     decomposed -> AC -> tested -> verified -> reconciled -> reviewed. **Hard-fail**:
     a unit cannot reach Done with a stage skipped (D-conformance).
   - **Independent critic (D3)** - a sub-agent that did not write the diff judges it
     against AC intent, plus adversarial/mutation checks. Reject -> repair.
   - Commit the unit green (trunk-based by default, D6).
4. **Stall handling (D2).** After 3 failed green attempts a unit is marked
   **Blocked**, logged, and skipped; the run continues. Blocked units surface in
   `status`. Never thrash; never silently drop.
5. **Closing gate - the sprint review.** Every run ends with a mandatory
   `reconcile` (fix any drift) + `review` (the unified PRD/TRD/TSD/persona plus CODE
   review), **regardless of `--goal`**. This is the sprint review and it produces
   the conformance `reviewed` signal. For `--goal design` it reviews the produced
   backlog; for `--goal done` the delivered increment.
6. **Retro (CR0018).** The closing gate also writes a sprint retro to
   `sdlc-studio/retros/` (delivered, blocked, lessons) and reads the recent retros
   plus `lessons recall` at the **start** - the learning loop. The retro is a
   general capability (CR0018), reused here, not autosprint-only.

## Goals

| `--goal` | The loop stops when... | Output |
| --- | --- | --- |
| `triage` | the plan is approved | the ordered worklist |
| `design` | every unit is decomposed to Ready stories with AC | a reviewable backlog |
| `done` | every unit is implemented, verified, conformant, reviewed | the delivered increment |

## Guardrails (settled in RFC0001)

- **Deterministic** (the model cannot skip them): the iteration cap, the
  repetition-breaker, the completion oracle, and the **conformance check**.
- **Model-instructed:** the autonomy ceiling and escalation policy.
- **Decisions ledger (D4):** a committed, append-only per-tranche log; survives
  context compaction.

## Scripts

| Script | Role |
| --- | --- |
| `scripts/autosprint.py plan` | select + order the batch (the triage plan) |
| `scripts/conformance.py check` | the lifecycle-conformance gate (hard-fail) |
| `reconcile` / `review` / `verify_ac` | the closing gate + per-unit oracle (reused) |

## See Also

- `RFC0001-autonomous-delivery-loop.md` - the design + decisions (D1-D7)
- `reference-project.md` - the wave engine autosprint wraps
- `reference-cr.md` - `cr action` (CR -> stories)
- `help/autosprint.md` - command quick reference
