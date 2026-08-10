# RETRO-0100: RUN-01KZM49Y: a new project can plan its first sprint, and five review rounds all found the same thing

> **Date:** 2026-08-10
> **Batch:** BG0558, BG0559, BG0560, US0662, US0663, US0664, US0665, US0666
> **Goal:** {{goal}}
> **Delivered:** {{n_done}} / {{n_total}}   **Blocked:** {{n_blocked}}

## Delivered

- BG0558 (5) - a greenfield project can plan its first sprint. The rule now catches a TYPO, by
  basename match, not a path that does not exist yet - which is every path a new project declares.
- BG0559 (3) - the `doc-surface` gate lane is undefined outside the skill repo rather than broken
  there. One applicability predicate, three readers.
- BG0560 (5) - `docs/existing-users.md` describes v5, and is checked by PARSING its own upgrade
  steps out of the page and executing them against a v4-era fixture.
- US0662 (5) - a project that has closed no sprint gets the plan-review requirement as a report.
- US0663 (3) - the softening expires on the first retro, and no config key can hold it open.
- US0664 (5) - the greenfield rehearsal, proven to FAIL on the tree as it shipped.
- US0665 (5) - the upgrade rehearsal, against a baseline that reddens in BOTH directions.
- US0666 (3) - the lane binds at the push and release boundaries, never per commit.

44 points against a plan of 18. The batch grew from 5 units to 8 when CR0542's rehearsal stories
were unblocked mid-run, and BG0558 and BG0559 each grew during their own plan review.

## Blocked / deferred

- All 8 units - the reviewer-of-record sign-off is OWED and is structurally unavailable to the
  authoring session. That is the two-role gate working, not failing.
- The upgrade path does not reach a green gate: conformance, reconcile and index-derived still
  fail after a clean `migrate --apply`. Recorded in `tools/release-rehearsal-baseline.txt`
  against CR0497, which is SC0004's work, not this run's.

## What went well

- The plan-review round rejected all five original plans BEFORE a line of code existed, and it
  cost a fraction of what the same findings cost after the code shipped. Every finding was
  established by execution.
- The instrument outlived the bugs. `tools/rehearse-release.sh` now drives the two paths a user
  arrives on at every boundary, and it is proven to fail on the tree as it shipped - which is the
  only thing that makes its green worth anything.
- Every retraction was made ON THE ARTEFACT, before the change, rather than explained afterwards.
  A round-4 seat was asked specifically whether they were honest or convenient and judged them
  honest.

## What was hard / what stalled

- FIVE review rounds. The tooling escalated non-convergence to the operator after the third, and
  it was right to: rounds 2, 3 and 5 each found the previous round's repair correct but UNGATED,
  or relocated one clause over.
- The author committed 41 files of mutation residue to `main`, created by US0664 AC3's own
  declared mutant and swept in by `git add -A`, in the commit whose AC3 asserts nothing is written
  inside the repository. A later run of the same mutant deleted a reviewer's git worktree.
- Roughly twenty full-suite runs at 13 minutes each. The gate budget lane reported OVER on most
  commits - 492s, 626s, 688s against a 380s ceiling.

## Lessons

- **A repair that is correct and ungated is not a repair.** Rounds 3 and 5 each reverted the
  previous round's fix against a green suite and watched nothing fail: the boundary regression,
  the spurious advisory, and the bytecode residue were all fixed and all unguarded. The question
  after any repair is not "is it right" but "what fails if it comes back".
- **A presence check can never detect an addition.** US0663 AC3 asserted two strings were PRESENT
  while its own declared mutant was an ADDITION, so adding the forbidden key made the test pass
  harder. An absence-shaped criterion needs an absence-shaped assertion and a control that adds
  the thing.
- **A guard that hides a fault also hides the evidence of it.** Gitignoring the residue path
  stopped it being committed and stopped `git status` seeing it, in the very criterion the ignore
  rule was added to harden. Every suppression is also a blindfold; ask what stopped being visible.
- **A declared mutant is executed by strangers - write it so it cannot destroy their work.**
  "Change the fixture root to the repository root" met a `rm -rf "$WORK"` trap and deleted a
  reviewer's worktree. The harness now refuses that root before the trap is armed.
- **A test that passes only because a sibling ran first is not passing.** US0664 AC3 held for a
  whole round because two tests above it warmed the bytecode cache the harness itself wrote. Run
  the criterion alone, cold, which is how a reviewer will run it.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro.

- A repair that is correct and ungated is not a repair - revert it and see what fails.
- A presence check can never detect an addition.
- Every suppression is also a blindfold: ask what stopped being visible.
- A declared mutant is executed by strangers; write it so it cannot destroy their work.
- Drive the claim through the COMMAND, on a fixture built from nothing - it finds what the suite
  structurally cannot see.

## Known issues carried

Every finding this sprint leaves OPEN, with the ruling somebody made on it. This is the one
compulsory close item the tree cannot derive: whether an open defect stops the ship is a
judgement, so it is recorded here and the sprint checklist reads it back. An open finding
with no row is reported as UNRULED, because "we carried it" and "nobody looked" must never
read the same.

Ruling is one of `stop-ship`, `not-stop-ship`, `accepted-risk`, `deferred`. A `stop-ship`
ruling HOLDS the close, which is the point of being able to make one.

| Issue | Ruling | Ruled by | Date |
| --- | --- | --- | --- |
| BG0561 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, on the round-2 review record | 2026-08-10 |
| BG0562 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, on the round-1 review record | 2026-08-10 |
| BG0563 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, on the round-2 review record | 2026-08-10 |
| BG0564 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, on the round-2 review record | 2026-08-10 |
| BG0565 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, on the round-2 review record | 2026-08-10 |
| BG0566 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, on the round-3 review record | 2026-08-10 |
| BG0567 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, on the round-3 review record | 2026-08-10 |

> The rows below are the repository's whole OPEN finding set, not this run's. The checklist reads every open finding, and it is right to: an open defect with no ruling and one nobody looked at read the same. Each is `not-stop-ship` FOR THIS CLOSE and each one holds the v5 TAG, which is exactly what D0133 says - zero open bugs at tag - and what the SC0002 to SC0007 charter queue exists to clear. Ruling them here is a statement about this sprint's increment, never a waiver of the release bar.

| Issue | Ruling | Ruled by | Date |
| --- | --- | --- | --- |
| BG0350 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0406 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0421 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0457 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0463 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0469 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0486 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0488 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0490 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0491 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0493 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0497 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0508 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0509 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0512 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0519 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0522 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0523 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0526 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0528 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0529 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0531 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0532 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0534 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0535 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0536 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0537 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0538 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0539 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0540 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0542 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0543 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0544 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0545 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0546 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0547 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0548 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0549 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0550 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0551 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0552 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0553 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0554 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0555 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0556 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| BG0557 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - holds the v5 tag, not this close | 2026-08-10 |
| CR0424 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0441 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0445 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0496 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0497 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0499 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0503 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0504 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0507 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0508 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0509 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0511 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0512 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0513 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0515 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0523 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0524 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0526 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0528 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0529 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0530 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0531 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0533 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0534 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0535 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0536 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0539 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0540 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0541 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |
| CR0542 | not-stop-ship | Claude Opus 5 session 6ee2f0cb, under D0133 - a discovery-backlog request, not a defect holding this increment | 2026-08-10 |

## Estimate vs actual

**Were the estimates any good?** The plan forecast a token cost per unit; telemetry recorded
what each one actually cost. This section holds the comparison, so the question is asked every
sprint instead of only when someone remembers to ask it.

Generate it: `scripts/retro.py accuracy --id RETROxxxx --write` - it fills the block below from
the batch's telemetry and appends this sprint's row to `retros/VELOCITY.md`.

A unit with no per-unit telemetry record has its PER-UNIT ratio reported as **UNMEASURED** and
excluded from that ratio - it is never counted as accurate. But the token count itself is NOT
unmeasurable: the harness tracks it deterministically. An INTERACTIVE sprint (no runner) records no
per-unit actual, so the close captures this RUN's share of the harness-tracked total itself
(`accuracy --tokens-from-harness`, run by `sprint close --apply-signoff`) and the velocity row
records it. The meter is per-SESSION and cumulative, so what is captured is the delta from the
baseline stamped when the run opened - not the session total, which in a session holding more than
one sprint counts the earlier ones again. A run with no baseline (opened before the baseline
existed, or closed from a different session) reports **not-attributable** rather than a number:
there is no fallback to the raw total, because a plausible-looking figure that is not this sprint's
cost is worse than an absent one. When the capture cannot attribute, the close states why and
`accuracy --tokens N` remains the manual override.
Report it as **not-yet-captured** only while neither has happened, never as if the number were
unknowable. That figure is DESCRIPTIVE, never a target (see CR0273).

The forecast is a hypothesis, not a settled calibration. Read the ratio, write down what it
implies, and change the constants only on evidence a human has looked at - a fit to a couple of
sprints fits noise.

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BG0558 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0559 | 2 | 88,854 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0560 | 5 | 222,135 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0662 | 5 | 222,135 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0663 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0664 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0665 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0666 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 8 unit(s) measured; 5 of 8 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes, by phase - read from the two verdict ledgers:

  test-plan review: 14 pass(es) over 8 unit(s), 9 rejected

  code review: 29 pass(es) over 8 unit(s), 21 rejected

  ratio: 2.07 code-review pass(es) per test-plan pass - the claim EP0207 is judged on, as a number
Unmeasured: BG0558, BG0559, BG0560, US0662, US0663. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: US0664, US0665, US0666. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- {{what the ratio implies - which units the estimate missed, and why}}

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?**

This is the question that turns a retro into work. Every finding gets a disposition:
**file it** (a BG/CR id), **record it fixed in-sprint** (`fixed-in: <sha or unit>`), or
**decline it with a reason**. All three are green. What does not pass is silence - a
finding written down and left to rot. The three are counted separately at close: a sprint
that repaired eleven findings reads as eleven fixed, not eleven declined.

To say "nothing worth raising", say so in a row and give the reason. An empty table is
not an answer.

All three accepted dispositions are shown below, filled in rather than described - the
vocabulary is exact and a refusal is a poor place to meet it for the first time. Replace
every EXAMPLE row; a row left in place is reported at the close, and a retro still carrying EVERY demonstration line this template ships is REFUSED by it.

| Finding | Disposition |
| --- | --- |
| `markdownlint --fix` rewrites every metadata line of an artefact whose title holds a dunder, and `validate` then finds no Status | BG0566 |
| The rehearsal wrote `__pycache__` into the repository, and its criterion passed only because a sibling test warmed the cache | fixed-in: 3253c126 |
| BG0558 AC4's declared mutant describes a case-sensitivity the shared predicate does not have | declined: the shipped test pins the invariant by patching the predicate, so the wording is wrong and the criterion is not |

<!-- file one with: scripts/file_finding.py · check with: scripts/retro.py dispose --id RETROxxxx -->

## Close loop (gated)

`gate --require-retro RETROxxxx` (this retro's id, file form) fails until all four are true:

- [ ] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETROxxxx`)
- [ ] its lessons are in the project store, not just in this file (`retro.py extract --id RETROxxxx`)
- [ ] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [ ] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: {{tokens}} · Duration: {{duration}} · Critic rejects: {{rejects}}

## Handoff

- [HO-0057](../handoffs/HO0057-a-user-who-has-never-run-sdlc-studio.md) - 5 remaining item(s): 0 copilot-tail, 5 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
