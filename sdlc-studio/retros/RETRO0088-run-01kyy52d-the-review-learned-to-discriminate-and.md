# RETRO-0088: RUN-01KYY52D: the review learned to discriminate, and then failed its own new rule

> **Date:** 2026-08-01
> **Batch:** US0577, US0578, US0579, US0580, US0582, US0583, US0584, US0585, US0597
> **Goal:** make the review process discriminate - bound its scope, mechanise its inputs, and turn the rules that were read-and-skipped into refusals
> **Delivered:** 9 / 9 (36 points)   **Blocked:** 0

## Delivered

- US0577 (5) - a verdict records a sha256[:12] fingerprint of the brief the seat was given; pre-Brief logs are widened in place rather than broken
- US0578 (3) - `critic.py record` REFUSES a verdict with no brief provenance; the stand-down is a recorded config decision that is stated, never silent
- US0579 (5) - every finding declares its origin: `[regression]`, `[new]`, `[pre-existing]`; an untagged one is refused by name
- US0580 (5) - only regression and new hold a gate; an all-pre-existing REJECT covers the unit, and the two sets render apart with the reason
- US0582 (2) - the shipped doctrine states the scope rule (rule 19), guarded by a runnable `tools/doctrine_review_scope.py`
- US0583 (5) - the claim-drift lane: a diff whose code and whose own prose disagree
- US0584 (5) - the ticked-over-untouched detector, which survived every boundary probe an independent seat could build
- US0585 (3) - the lane runs in the commit gate, advisory, with its yield recorded
- US0597 (3) - the premise replayed against real commits, where it disproved itself three times

## Blocked / deferred

- None. Every unit reached Review and every finding raised against them was repaired inside the run, not carried.

## What went well

- **The review discriminated for the first time.** Bounded to each unit's `Affects` against the run's base ref and briefed by `critic.py brief`, the EP0195 pass APPROVED US0584 and rejected three, each blocking finding carrying an executed reproduction and a `git log -S` deciding its origin. It also explicitly CLEARED a finding it nearly filed after checking the numbers. Previously every review rejected everything, which carries the same information as approving everything.
- **Mechanising the input did the work, not loosening the criteria.** Hand-written prompts had produced eight sprawling repo-wide findings; the same units re-briefed from the shipped tool produced one precise finding each with no pre-existing noise.
- **The tooling refused me repeatedly and was right every time**: `mutation.py` would not mutate over uncommitted work, `file_finding.py` hit its triage cap, `verify-ratchet` caught two criteria sharing one selector, and `test_census` refused to let the unattributed baseline rise - which is why the doctrine guard became a runnable module instead of a test-only assertion.
- **Findings were repaired in-batch rather than at the close**, which is what rule 18 asks for and what keeps a finding priced against the batch that caused it.

## What was hard / what stalled

- **Two review rounds were needed on one batch, and the operator was right to call it out.** Needing a second round is verification handed to the reviewer. The cost lands on them every time.
- **A false claim shipped inside the epic built to catch false claims.** The changelog and commit message both said `critic.py brief` emits a fingerprint. It did not - `brief_fingerprint` had exactly one caller, and it was not the brief command. Nobody had run the feature through its front door.
- **The suite verdict was read through a pipe twice, and was wrong both times.** `npm test | tail` reports tail's exit status. A commit was reported as landed when the hook had refused it, and a suite was reported green with a real failure inside it.
- **The `claim_drift` premise was measured on one commit and shipped.** Replayed over forty it produced 215 findings, 135 of them naming no code at all. A premise measured once is an anecdote.
- **Fixtures had to be corrected rather than the code, three times** - synthetic diffs with no context line, and a fixture brief value that was not a valid fingerprint. Each time the check was right and the fixture was unrealistic, which is only obvious in hindsight.

## Lessons

- A library test cannot see a missing lane: the wiring between entry point and function is exactly the part it does not exercise, and it is where this defect class lives. State the ENTRY POINT a test enters through before writing it.
- A review that fails every unit carries the same information as one that passes every unit. Bounding the scope is what makes a REJECT mean something.
- A premise measured on one instance is an anecdote. Replay it over the corpus before building on it.
- Reading a command's verdict through a pipe reports the pipe's status. Redirect, then echo the code separately.
- Two copies of a rule drift apart: the coverage rule was restated in three modules and this diff falsified all three at once.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- Exercise every claim through the SHIPPED ENTRY POINT before asking for review. A library
  test cannot see a missing lane, and a review should confirm the work rather than discover
  it does not run.
- A premise measured on one instance is an anecdote. Replay it over the corpus before
  building on it, and record both arms.
- Read a command's verdict from its exit code directly. A pipe reports the pipe's status, and
  a red suite then reads as green.
- Bound a review to the unit's own diff. Only what this change broke may hold its gate, or
  the verdict stops carrying information.
- A rule restated in a second place drifts from the first. Pin every copy, or keep one.

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
| BG0470 | not-stop-ship | Claude Opus 5 | 2026-08-01 |
| BG0457 | not-stop-ship | Claude Opus 5 | 2026-08-01 |
| BG0462 | not-stop-ship | Claude Opus 5 | 2026-08-01 |
| BG0463 | deferred | Claude Opus 5 | 2026-08-01 |
| BG0469 | not-stop-ship | Claude Opus 5 | 2026-08-01 |
| BG0474 | not-stop-ship | Claude Opus 5 | 2026-08-01 |
| BG0475 | not-stop-ship | Claude Opus 5 | 2026-08-01 |
| CR0509 | deferred | Claude Opus 5 | 2026-08-01 |
| CR0510 | deferred | Claude Opus 5 | 2026-08-01 |
| BG0483 | not-stop-ship | Claude Opus 5 | 2026-08-01 |
| CR0522 | not-stop-ship | Claude Opus 5 | 2026-08-01 |
| BG0476 | not-stop-ship | Claude Opus 5 | 2026-08-01 |
| BG0477 | not-stop-ship | Claude Opus 5 | 2026-08-01 |
| BG0478 | not-stop-ship | Claude Opus 5 | 2026-08-01 |
| CR0518 | deferred | Claude Opus 5 | 2026-08-01 |
| CR0519 | deferred | Claude Opus 5 | 2026-08-01 |
| CR0520 | deferred | Claude Opus 5 | 2026-08-01 |

**BG0470 in particular, because it names the work this sprint shipped.** It warns that
`sdlc-studio/.local/sprint-base-ref.txt` is two weeks stale and that CR0512 - delivered here as
EP0194 - would fold a fortnight of unrelated commits into "this unit's diff". Checked rather
than assumed: nothing in the shipped code reads that file. `grep -rn "sprint-base-ref"` over
`scripts/*.py` returns no reader, and `critic.py` has no base-ref path at all. The origin
classification is made by the reviewer, who is given the base ref in the brief, and both
reviews this run used correct explicit refs (`3c195846` and `3570c94a`). So it is inert
today - and it becomes live the moment classification is automated from that file, which is
why it is carried as a named issue rather than closed.

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
| US0577 | 5 | 236,750 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0578 | 3 | 142,050 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0579 | 5 | 236,750 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0580 | 5 | 236,750 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0582 | 2 | 94,700 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0583 | 5 | 236,750 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0584 | 5 | 236,750 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0585 | 3 | 142,050 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0597 | 3 | 142,050 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 9 unit(s) measured; 9 of 9 forecast at plan time.**

**Velocity: 3.21 points/elapsed-hour** (36 points over 11.212h, run-state, ceremony included). This is the planning number - points per SESSION within the observed single-session envelope; it is NOT a linear per-point rate to extrapolate to a 1-point or 100-point sprint, and it is descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).
Unmeasured: US0577, US0578, US0579, US0580, US0582, US0583, US0584, US0585, US0597. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- The nine units were forecast on points at the calibrated rate. The cost this run was dominated by REPAIR rather than delivery: two review rounds and nine findings repaired in-batch, none of which the points priced. That is the number to watch, not the per-unit ratio.

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
| claim-drift emitted findings naming no code, 135 of 215 over the corpus | fixed-in: c906e153 |
| the lane's own comment and fragment described a scan `_standing_prose` had replaced | fixed-in: c906e153 |
| `record_yield` dirtied a tracked file on every commit | fixed-in: c906e153 |
| US0597's AC3 was ticked over a verifier that could not fail on its subject | fixed-in: c906e153 |
| `critic.py brief` never emitted the fingerprint the gate demands - a false shipped claim | fixed-in: a0e72a62 |
| the mandatory `--brief` value was unvalidated, so the gate was met by inventing one | fixed-in: a0e72a62 |
| the untagged-finding guard was load-bearing and pinned by nothing | fixed-in: a0e72a62 |
| three docstrings falsified by their own diff | fixed-in: a0e72a62 |
| the lane reads append-only ledgers as prose, matching verdict rows against the code they name | BG0483 |
| a test module importing a sibling fixture is unimportable under pytest | BG0476 |
| `refine` mints stories nothing can plan | BG0477 |
| `artifact.py new` mints a CR the commit gate then refuses on its own placeholder | BG0478 |
| no runbook answers "what is the next step and which command performs it" | CR0518 |
| a suite verdict read through a pipe reports the pipe's exit code | CR0519 |
| the repo-wide periodic review blocked a sprint whose own work was fully reviewed | CR0522 |
| a criterion verified only through the library is not evidence the feature ships | CR0520 |

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

- Tokens: not-yet-captured (interactive run; captured by `accuracy --tokens-from-harness` at close) · Duration: one interactive session · Critic rejects: 6 unit-level REJECTs across two boundary reviews, all repaired in-batch, both spans then cleared by a fresh pass

## Handoff

- [HO-0040](../handoffs/HO0040-a-review-costs-what-it-should-the-claim.md) - 9 remaining item(s): 0 copilot-tail, 9 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
