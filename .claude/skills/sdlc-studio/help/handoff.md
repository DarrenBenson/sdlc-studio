<!--
Load when: /sdlc-studio handoff, a sprint/epic run stops short of its goal, or
"where do I pick this up?"
Dependencies: SKILL.md (always loaded first)
Related: reference-sprint.md, reference-scripts-domain.md, help/sprint.md, help/gate.md
-->

# /sdlc-studio handoff - the remaining-work join, read-only

## You can just ask

| Just say... | Runs |
| --- | --- |
| "The run stopped - what is left?" | `handoff.py show` |
| "Pick up where the last run stopped" | `sprint.py plan --worklist RPTxxxx` (the last signed report) |

**No command writes a handoff.** A run ends with its signed sprint report, whose `Known issues
handed over` section lists every open finding raised in the run and every carried unit. The next
`sprint plan` names that report and its open items unasked, and `--worklist RPTxxxx` plans them. A
run ended by `sprint.py stop --force` files no report, so the plan names the units that stop waived
from the run record instead.

The HO files written before this change stay in `sdlc-studio/handoffs/` with their index rows:
they still resolve by id and reconcile cleanly, and nothing rewrites them.

## Quick Reference

```bash
python3 <skill>/scripts/handoff.py show                            # the join, nothing written
python3 <skill>/scripts/handoff.py show --format json
```

## What `show` prints

A join over the run's own evidence, with no new instrumentation: quarantined units and their
failure signatures from the loop guardrails, failing and unproven ACs from the verify report,
per-unit issues from the tranche audit, the stage a unit stalled at from conformance, and the
approved batch from the run state (then the persisted sprint plan). Every unit that is not
terminal is named with at least one pointer - the failing AC, the check it stalled at, the
blocker, or its own file - and a batch id with no artefact on disk is listed as
remaining-and-missing. The units the close's own predicate holds (unfinished and unruled, or
carrying a standing REJECT) are listed as unanswered. `status.py` reads the same remaining
count for its `Run:` line.

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
the estimator's confidence, and an item with no signal at all reads `judgement`, never a
confidently-wrong `copilot-tail`.

## See Also

- `help/sprint.md` - the loop that produces the run, and the signed report that ends it
- `reference-sprint.md` - the close sequence in full
