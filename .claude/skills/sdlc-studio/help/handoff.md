<!--
Load when: /sdlc-studio handoff, a sprint/epic run stops short of its goal, or
"where do I pick this up?"
Dependencies: SKILL.md (always loaded first)
Related: reference-sprint.md, reference-scripts-domain.md, help/sprint.md, help/gate.md
-->

# /sdlc-studio handoff - the run-close handoff guide

## You can just ask

| Just say... | Runs |
| --- | --- |
| "The run stopped - what is left?" | `handoff.py show` |
| "Close this run and hand it over" | `handoff.py generate --outcome blocked --retro RETRO0021` |
| "We are out of budget, write the handoff" | `handoff.py generate --outcome budget-spent --retro RETRO0021` |
| "Pick up where the last run stopped" | `sprint.py plan --worklist sdlc-studio/.local/handoff-worklist.txt` |

An unattended run that stops leaves its tail scattered across hints, the decisions log and
the retro, and the human who joins next has nothing to start from. The handoff is that
document: **what was delivered with its evidence, what remains with a pointer per item, and
which of those items suit copilot-assisted completion rather than human judgement.**

## Quick Reference

```bash
python3 <skill>/scripts/handoff.py show                            # the join, nothing written
python3 <skill>/scripts/handoff.py generate --title "EP0031 run" \
    --outcome budget-spent --retro RETRO0021
python3 <skill>/scripts/sprint.py plan \
    --worklist sdlc-studio/.local/handoff-worklist.txt --order wsjf   # the next run
```

## What it does

1. **Joins the run's own evidence.** No new instrumentation: quarantined units and their
   failure signatures come from the loop guardrails, failing and unproven ACs from the
   verify report, per-unit issues from the tranche audit, the stage a unit stalled at from
   conformance, and the approved batch from the run state (then the persisted sprint plan).
2. **Names every remaining item.** A unit that is not terminal is listed with at least one
   pointer - the failing AC, the check it stalled at, the blocker that stopped it, or its
   own file. A batch id with no artefact on disk is listed too, as remaining-and-missing. A
   handoff that quietly loses an item is worse than no handoff.
3. **Tags each one `copilot-tail` or `judgement`,** seeded deterministically from the
   difficulty band, the quarantine reason, and the stage reached (see below), with the
   reasons printed alongside so the tag can be argued with.
4. **Creates the artefact through the tool machinery** - a tool-allocated `HO` id and an
   index row, like a retro - and **links it from the retro**, which is what the next person
   actually reads.
5. **Emits a worklist** (`sdlc-studio/.local/handoff-worklist.txt`) that
   `sprint plan --worklist` reads back as a batch, and **closes the run state** with its
   outcome.

## The suitability tag

| Signal | Reads as |
| --- | --- |
| Difficulty band `high` / `extreme` | judgement |
| The loop quarantined it (cap, or a repeated failure signature) | judgement |
| Stalled at `specified` (no AC) or `critiqued` (needs independent review) | judgement |
| A tranche-audit issue: weak AC, unmet or unresolved dependencies, cross-epic AC leakage | judgement |
| No artefact file on disk | judgement |
| Everything else | copilot-tail |

It is a **seed, not a verdict**. Every item carries the reasons that produced its tag and
the estimator's confidence; the closing model refines it, and an item with no signal at all
reads `judgement`, never a confidently-wrong `copilot-tail`.

## The run state

`sprint plan --write` opens the run (id, start time, approved batch, `--goal` rung) in
`sdlc-studio/.local/run-state.json`; `handoff generate --outcome <how it ended>` closes it.
Outcomes: `goal-reached`, `budget-spent`, `blocked`, `stopped`. A run nobody opened still
gets a handoff - the document says the run was not opened rather than inventing a start time.

## The gate

```bash
python3 <skill>/scripts/gate.py --require-retro RETRO0021 --require-handoff HO0001
```

`--require-handoff` fails unless the handoff exists **and a retro links it**. Presence alone
would certify a document nobody can find. Deselecting the bound `handoff` lane is refused.

## See Also

- `help/sprint.md` - the loop that produces the run
- `help/gate.md` - the close gate
- `reference-sprint.md` - the close sequence in full
