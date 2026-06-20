<!--
Load when: /sdlc-studio autosprint or /sdlc-studio autosprint help
Dependencies: SKILL.md (always loaded first)
Related: reference-autosprint.md (full workflow), RFC0001
-->

# /sdlc-studio autosprint - Goal-Driven Development loop

Run a prioritised batch of work to a goal, autonomously. You set the goal and the
acceptance criteria; the loop drives the proven lifecycle (decompose -> TDD ->
verify -> conformance -> review) to it. See `reference-autosprint.md` for the full
workflow.

## Quick Reference

```bash
/sdlc-studio autosprint --crs proposed --goal done      # deliver the proposed CRs
/sdlc-studio autosprint --bugs open --goal done         # deliver the open bugs
/sdlc-studio autosprint --epic EP0007 --goal done       # deliver an epic
/sdlc-studio autosprint --crs proposed --goal design    # just the backlog (no code)
/sdlc-studio autosprint <worklist.md> --order wsjf       # a tranche file, WSJF order
/sdlc-studio autosprint --bugs open --autonomous         # unattended: deterministic guardrails on
```

Natural language works too: "do an autosprint to deliver all open bugs".

## Flags

| Flag | Description | Default |
| --- | --- | --- |
| `<batch>` | a worklist file, or `--bugs`/`--crs`/`--stories <status>` / `--epic EPxxxx` | required |
| `--goal` | `triage` (plan only) / `design` (Ready backlog) / `done` (delivered) | `done` |
| `--order` | `priority` / `wsjf` (priority over RFC0009 complexity) / `manual` | `priority` |
| `--autonomous` | unattended mode: the deterministic guardrails (cap, repetition-breaker, completion oracle) enforce stop/stall instead of model discretion | off |

## What happens

1. **Plan** - `autosprint plan` selects + orders the batch.
2. **Tranche audit** - `audit.py check` grooms the batch for readiness (weak-AC,
   unmet-deps, already-terminal, link-integrity) before you approve it.
3. **Triage STOP** - the groomed plan is shown; you approve, then it runs
   autonomously, re-pausing only on a material issue.
4. **Per unit** - `cr action` -> `epic implement --agentic` (TDD) -> `verify_ac` ->
   `conformance check` (hard-fail gate) -> independent critic -> green commit.
   Each ruling is appended to the decisions `ledger` so it survives compaction.
5. **Stall** - `loop_guard` quarantines a unit at the cap (3 attempts) or on a
   repeated failure signature: it is marked Blocked, logged, skipped; the run
   continues. The completion oracle declares the batch done only when every unit
   is terminal (Done or Blocked).
6. **Sprint review** - every run ends with a mandatory `reconcile` + `review`.

In `--autonomous` mode steps 4's guardrails are deterministic scripts the model
cannot skip; without it they are model-instructed (the portable Phase-1 path).

## Prerequisites

- A batch to run (CRs/bugs/stories on disk, or a worklist file).
- The scripts: `autosprint.py`, `conformance.py`, `ledger.py`, `loop_guard.py`,
  plus the reused `verify_ac`, `reconcile`, `review`.

## See Also

- `reference-autosprint.md` - full workflow and guardrails
- `/sdlc-studio status` - shows Blocked units after a run
- `RFC0001` - the design and decisions
