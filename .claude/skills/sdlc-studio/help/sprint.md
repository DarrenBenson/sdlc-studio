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
/sdlc-studio sprint --epic EP0007 --goal done       # deliver an epic
/sdlc-studio sprint --crs Proposed --goal design    # just the backlog (no code)
/sdlc-studio sprint --crs Proposed --goal plan       # select+sequence+estimate a sprint, stop
/sdlc-studio sprint prd.md --goal design             # greenfield: PRD -> epics -> stories
/sdlc-studio sprint <worklist.md> --order wsjf       # a tranche file, WSJF order
/sdlc-studio sprint --bugs Open --autonomous         # unattended: deterministic guardrails on
```

Natural language works too: "do a sprint to deliver all open bugs"; "plan and break down the
next sprint" resolves to `--goal design` (the goals are cumulative stop-points).

## Flags

| Flag | Description | Default |
| --- | --- | --- |
| `<batch>` | a worklist file, `--bugs`/`--crs`/`--stories <status>` / `--epic EPxxxx`, or a **PRD path** (greenfield authoring) | required |
| `--goal` | `triage` (plan) / `plan` (sprint plan) / `design` (Ready, estimated backlog) / `done` (delivered) | `done` |
| `--order` | `priority` / `wsjf` (priority over complexity) / `manual` | `priority` |
| `--epic EPxxxx` | (with `--stories`, repeatable) scope a story plan to one or more epics, not the whole status class | all epics |
| `--write` | (with `plan`) persist the sprint plan to `.local/sprint-plan.json` | off |
| `--strict` | (with `plan`) refuse to plan when the index has drift (reconcile-before-plan) | off |
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
