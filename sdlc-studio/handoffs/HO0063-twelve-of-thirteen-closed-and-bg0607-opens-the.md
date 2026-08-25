# HO-0063: Twelve of thirteen closed, and BG0607 opens the next run

> **Date:** 2026-08-25
> **Created-by:** sdlc-studio new
> **Run:** RUN-01M0WCCG (started 2026-08-25T12:03:39Z)
> **Outcome:** stopped
> **Batch source:** run-state.json

## Where to pick up

**BG0607 opens the next run - D0152.** The run's goal was zero open High and it was NOT reached:
BG0607's fix shipped here, was withdrawn when an independent pass measured it taking whole-workspace
conformance from 608/690 to 579/690 on a lane that blocks at `--release`, and the bug was dropped
from the batch and re-opened at High. `known_issues.py --bar` refuses a release tag while it stands,
and the v5.0.1 notes name it.

Read BG0607's re-opening note before scoping anything. Its work is TWO HALVES and both must land in
one go: key the verdict retraction on the ledger's `Brief` fingerprint - measured to take the
unanswered-REJECT set from 81 units to 49, recovering 32 and losing none - AND backfill the residue
by recording the repair that answered each remaining rejection. Landing the roll-up alone reddens the
conformance lane on every unit the backfill has not reached, which is exactly what happened the first
time.

The other twelve units are terminal, signed off by the operator, and their evidence was re-executed
and re-registered against the tree as it stands at close. Three findings were filed from the review
round and are open: BG0613, BG0614, CR0558.

## Appetite

- **Declared:** wall-clock 5760 min, units 64 unit(s)
- **Spent:** 408.9 min, 12 unit(s) terminal
- **Delivered:** 12 unit(s)
- **Token forecast:** ~3,316,373 tokens - a plan-time estimate, never a gate (the total is transcript-measured but a LOWER BOUND - delegated spend is supplied, not observed)

## Delivered (12)

| Unit | Type | Status | Evidence |
| --- | --- | --- | --- |
| [BG0606](../../sdlc-studio/bugs/BG0606-six-test-plan-rows-across-us0671-us0674-and.md) | bug | Fixed | 3/3 AC(s) verified; critic REJECT (engineering seat (subagent, repair round)) |
| [BG0592](../../sdlc-studio/bugs/BG0592-the-corpus-red-criteria-metric-counts-unbuilt-stories.md) | bug | Fixed | 15/15 AC(s) verified; critic REJECT (engineering seat (subagent, repair round)) |
| [BG0611](../../sdlc-studio/bugs/BG0611-the-verdict-ledger-is-re-parsed-and-re.md) | bug | Fixed | no verifier or verdict on record |
| [BG0609](../../sdlc-studio/bugs/BG0609-transition-py-annotate-has-no-fields-file-so.md) | bug | Fixed | no verifier or verdict on record |
| [BG0605](../../sdlc-studio/bugs/BG0605-the-repair-ledger-computes-outstanding-findings-per-record.md) | bug | Fixed | no verifier or verdict on record |
| [BG0604](../../sdlc-studio/bugs/BG0604-the-oracle-procedure-tells-a-reviewer-to-revert.md) | bug | Fixed | no verifier or verdict on record |
| [BG0610](../../sdlc-studio/bugs/BG0610-a-fields-file-scalar-where-a-list-is.md) | bug | Fixed | no verifier or verdict on record |
| [BG0600](../../sdlc-studio/bugs/BG0600-the-unnameable-test-plan-exemption-is-still-held.md) | bug | Fixed | no verifier or verdict on record |
| [BG0581](../../sdlc-studio/bugs/BG0581-the-goal-review-brief-states-a-reachable-end.md) | bug | Fixed | 4/4 AC(s) verified; critic REJECT (engineering seat (subagent, repair round)) |
| [BG0586](../../sdlc-studio/bugs/BG0586-a-design-rung-that-groomed-nothing-closes-exactly.md) | bug | Fixed | no verifier or verdict on record |
| [BG0587](../../sdlc-studio/bugs/BG0587-two-answers-to-the-grooming-question-inside-one.md) | bug | Fixed | 3/3 AC(s) verified; critic REJECT (engineering seat (subagent, repair round)) |
| [BG0588](../../sdlc-studio/bugs/BG0588-the-design-rung-has-no-terminal-check-so.md) | bug | Fixed | no verifier or verdict on record |

## Remaining (0)

_Nothing remains: every unit in the batch reached a terminal status._

## Open decisions

| Ref | Decision | Where |
| --- | --- | --- |
| D0050 | BG0246's fix stands as ruled in D0047 (include interactive sprints, derive per-unit from the total, label each row), but D0047's RATIONALE contained a false claim which is withdrawn: including those sprints does NOT unstick the 'N units of its own evidence' counter | decisions.md (`sdlc-studio/decisions.md`) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Generated at the run close (`handoff generate`) |
