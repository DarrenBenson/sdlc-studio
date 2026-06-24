<!--
Load when: /sdlc-studio sprint or /sdlc-studio sprint help
Dependencies: SKILL.md (always loaded first)
Related: reference-sprint.md (full workflow), RFC0001
-->

# /sdlc-studio sprint - Goal-Driven Development loop

Run a prioritised batch of work to a goal. You set the goal and the acceptance
criteria; the loop drives the proven lifecycle (decompose -> TDD -> verify ->
conformance -> review) to it. Add `--autonomous` to run unattended. See
`reference-sprint.md` for the full workflow.

> **Renamed from `autosprint` (CR0087).** `/sdlc-studio autosprint ...` still works as a
> **deprecated alias** (the command is now the whole sprint lifecycle - `--goal plan` /
> `design` / `done` - so autonomy is the `--autonomous` flag, not the name). Prefer `sprint`.

## Quick Reference

```bash
/sdlc-studio sprint --crs proposed --goal done      # deliver the proposed CRs
/sdlc-studio sprint --bugs open --goal done         # deliver the open bugs
/sdlc-studio sprint --epic EP0007 --goal done       # deliver an epic
/sdlc-studio sprint --crs proposed --goal design    # just the backlog (no code)
/sdlc-studio sprint <worklist.md> --order wsjf       # a tranche file, WSJF order
/sdlc-studio sprint --bugs open --autonomous         # unattended: deterministic guardrails on
```

Natural language works too: "do an sprint to deliver all open bugs".

## Flags

| Flag | Description | Default |
| --- | --- | --- |
| `<batch>` | a worklist file, or `--bugs`/`--crs`/`--stories <status>` / `--epic EPxxxx` | required |
| `--goal` | `triage` (plan only) / `design` (Ready backlog) / `done` (delivered) | `done` |
| `--order` | `priority` / `wsjf` (priority over RFC0009 complexity) / `manual` | `priority` |
| `--autonomous` | unattended mode: the deterministic guardrails (cap, repetition-breaker, completion oracle) enforce stop/stall instead of model discretion | off |

## What happens

1. **Plan** - `sprint plan` selects + orders the batch.
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
- The scripts: `sprint.py`, `conformance.py`, `ledger.py`, `loop_guard.py`,
  plus the reused `verify_ac`, `reconcile`, `review`.

## See Also

- `reference-sprint.md` - full workflow and guardrails
- `/sdlc-studio status` - shows Blocked units after a run
- `RFC0001` - the design and decisions
