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
2. **Tranche audit (pre-flight).** `scripts/audit.py check <query|--ids>` grooms the
   batch for readiness *before* the triage STOP, so work never starts on a unit that
   would pass the downstream gates vacuously. Per unit it flags, deterministically,
   **weak-AC** (no checkable AC or the tautology placeholder), **unmet-deps** (a
   `Depends on` referent not yet delivered), **already-terminal** (close it, do not
   re-work), and **link-integrity** (reuses `scripts/integrity.py`). Not-ready units
   are sharpened, closed, or flagged-and-deferred; findings go to the decisions
   ledger. The adversarial "is the problem still real, the change still sound" lens
   is model-instructed (delegates to RFC0002's audit when built).
3. **Triage STOP (D1).** Present the groomed plan + the audit verdict and **stop for
   operator approval**. After approval the loop runs autonomously, re-pausing only on
   a **material issue** (scope change, broken interface/contract, contradicts a
   triage answer, no safe reversible default).
4. **Per unit, in order:**
   - `cr action` - decompose a CR into stories under an existing epic (a new one
     only if none fits, D-decomposition). Stories carry implementation-ready AC and
     a `Verify:` line. Plans (PL) are not created in agentic mode (D7).
   - `epic implement --agentic` - implement under **TDD** (failing test first), the
     default. Wraps the existing wave engine (`reference-project.md`); does not
     reinvent it.
   - `verify_ac` - run the AC oracle; back-annotate `Verified:`.
   - **Independent critic (D3)** - a sub-agent that did not write the diff judges it
     against AC intent, plus adversarial/mutation checks. Reject -> repair. Its
     verdict is recorded with `critic.py record` (committed) so the gate can require it.
   - `conformance check` - the deterministic gate (`scripts/conformance.py`):
     decomposed -> AC -> tested -> verified -> **reconciled** (no index drift) ->
     **critiqued** (a committed critic APPROVE). **Hard-fail**: a unit cannot reach
     Done with a stage skipped - including the critic (D-conformance, CR0023).
   - Commit the unit green (trunk-based by default, D6).
5. **Stall handling (D2).** After 3 failed green attempts a unit is marked
   **Blocked**, logged, and skipped; the run continues. Blocked units surface in
   `status`. Never thrash; never silently drop.
6. **Closing gate - the sprint review.** Every run ends with a mandatory
   `reconcile` (fix any drift) + `review` (the unified PRD/TRD/TSD/persona plus CODE
   review), **regardless of `--goal`**. This is the sprint review and it produces
   the conformance `reviewed` signal. For `--goal design` it reviews the produced
   backlog; for `--goal done` the delivered increment.
   On each unit **close** (`artifact close`), a telemetry event (id, type, plus any run
   metrics passed: `--iterations`/`--verdict`/`--wall-time-s`/`--stages`) is appended to
   the gitignored `sdlc-studio/.local/telemetry.jsonl` (CR0051 / RFC0014 WS2). Advisory -
   it never affects the close; it feeds the deferred calibrate step (WS3) + RFC0009 WS5.
7. **Retro (CR0018).** The closing gate also writes a sprint retro to
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

## Scripts

| Script | Role |
| --- | --- |
| `scripts/autosprint.py plan` | select + order the batch (the triage plan) |
| `scripts/audit.py check` | tranche audit: weak-AC, unmet-deps, already-terminal, link-integrity |
| `scripts/integrity.py check` | referential integrity (required links + dangling refs) |
| `scripts/conformance.py check` | the lifecycle-conformance gate (hard-fail; incl. reconciled + critiqued) |
| `scripts/critic.py record` | the committed independent-critic verdict per unit (D3) |
| `scripts/loop_guard.py` | iteration cap, repetition-breaker, completion oracle |
| `scripts/ledger.py` | append-only per-tranche decisions ledger (survives compaction) |
| `reconcile` / `review` / `verify_ac` | the closing gate + per-unit oracle (reused) |

## See Also

- `RFC0001-autonomous-delivery-loop.md` - the design + decisions (D1-D7)
- `reference-project.md` - the wave engine autosprint wraps
- `reference-cr.md` - `cr action` (CR -> stories)
- `help/autosprint.md` - command quick reference
