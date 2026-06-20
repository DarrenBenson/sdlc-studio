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
```

Natural language works too: "do an autosprint to deliver all open bugs".

## Flags

| Flag | Description | Default |
| --- | --- | --- |
| `<batch>` | a worklist file, or `--bugs`/`--crs`/`--stories <status>` / `--epic EPxxxx` | required |
| `--goal` | `triage` (plan only) / `design` (Ready backlog) / `done` (delivered) | `done` |
| `--order` | `priority` / `wsjf` (priority over RFC0009 complexity) / `manual` | `priority` |

## What happens

1. **Plan** - `autosprint plan` selects + orders the batch.
2. **Triage STOP** - the plan is shown; you approve, then it runs autonomously,
   re-pausing only on a material issue.
3. **Per unit** - `cr action` -> `epic implement --agentic` (TDD) -> `verify_ac` ->
   `conformance check` (hard-fail gate) -> independent critic -> green commit.
4. **Stall** - 3 failed attempts -> the unit is Blocked and skipped; the run continues.
5. **Sprint review** - every run ends with a mandatory `reconcile` + `review`.

## Prerequisites

- A batch to run (CRs/bugs/stories on disk, or a worklist file).
- The scripts: `autosprint.py`, `conformance.py`, plus the reused `verify_ac`,
  `reconcile`, `review`.

## See Also

- `reference-autosprint.md` - full workflow and guardrails
- `/sdlc-studio status` - shows Blocked units after a run
- `RFC0001` - the design and decisions
