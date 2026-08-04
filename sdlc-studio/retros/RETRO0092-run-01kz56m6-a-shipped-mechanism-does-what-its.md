# RETRO-0092: RUN-01KZ56M6: a shipped mechanism does what its record claims - seven units, four inert verifiers repaired

> **Date:** 2026-08-04
> **Batch:** BG0419, BG0477, BG0485, BG0494, BG0501, BG0506, US0467
> **Goal:** A shipped mechanism does what its own record claims: for every unit in this batch the gap between the claim and the behaviour is closed and proven by execution - an executed mutant where the claim is a verifier, a reproduced wrong result where the claim is behaviour.
> **Delivered:** 7 / 7   **Blocked:** 0

## Delivered

- BG0419 - four delivered mechanisms whose verifiers passed with the mechanism removed are now held by tests that fail without them; each mutant demonstrated surviving before and dying after
- BG0477 - `refine` fills the User Story fields it mints, at both mint sites, and reports the grooming it leaves owed using the planner's own census
- BG0485 - closed with NO code: both halves shipped in e9dd8317, four days before the bug was filed
- BG0494 - a skill-relative `Affects` path no longer resolves to a consuming project's own file of the same name
- BG0501 - the shared points reader learns the `Story Points` spelling 20 stories use, so `batch add-epic` stops pricing epics at zero
- BG0506 - a repeated single-valued metadata field is refused, with the plural set declared rather than inferred; the two live offenders repaired
- US0467 - `status` names the open run on its first line, so a session re-anchors from one command

## Blocked / deferred

- none - every unit in the batch reached a terminal state

## What went well

- The plan-time goal review earned its cost three times over, BEFORE any code. It caught a criterion that would have reinstated the fix commit 7ef88707 deliberately made, three units whose criteria `transition` would have refused at the very end, and a filed fix that did not fix its own bug (BG0501's "route through the shared reader" - the reader could not read the field either).
- Verifying a premise before building on it saved a whole unit. BG0485's two defects did not reproduce, and `git log -S` dated their fix four days before the bug was filed. It is closed on that evidence, with the record saying plainly that no code was written - a closure that reads like a repair when nothing was repaired is how a backlog stops meaning anything.
- Gates refused this work five times and were right every time: the lane-check (five verifiers that never entered `main()`), the repo-hygiene sweep (a bare artefact read), the verify-ratchet (two ACs sharing one selector - the very defect US0635 exists for), the transition depth gate, and the suite-claim lane (a verdict the tree had moved past).

## What was hard / what stalled

- The batch review REJECTED round 1 on a regression this run introduced: `status.open_run` died on a run state that parses but is structurally malformed, taking the four-pillar dashboard and `hint` with it. Base exit 0, HEAD exit 1, on the command AGENTS.md makes step two of every session.
- Worse than the crash was its cause. `open_run` hand-rolled a SECOND reader of `run-state.json` while `run_state.read` already implemented exactly those states with a typed error - the defect BG0501 repaired elsewhere in the SAME batch. The sprint contradicted itself in one commit.
- Two repairs were defective on their first draft, both caught by running them rather than reading them: the `derived-only` census leg shipped inert behind a bare `except` with a wrong import, and AC4's replacement pin used a guessed ceiling and SURVIVED its own mutant.

## Lessons

- A test that opens the mechanism itself proves the mechanism and never its CALLER. Eleven tests each opened `corpus_cache()` inside their own fixture, so neutering the production wrapper in `reconcile.detect_all` left every one of them passing. The caller is the part a fixture-built sweep cannot see.
- A postcondition cannot express an ordering. "Nothing landed" holds equally when every write was attempted and every write failed; if the claim is that the refusal arrives FIRST, the write path has to be observed, not its aftermath.
- A ceiling you guessed is a ceiling that passes both cases. The first draft of the cache pin used a round number and survived its own mutant; measuring the two bounds (157 cached, 283 uncached) is what made it discriminate.
- Two readers of one file will disagree eventually, and the second one is written by whoever did not know the first existed. Both defects this run introduced were that shape.

## Carried lessons

The 5 that matter most for the NEXT batch.

- A test that opens the mechanism itself proves the mechanism and never its caller.
- Verify the premise before building on it - a bug can be filed after its own fix shipped.
- A guessed threshold passes both cases; measure the two bounds and put the ceiling between them.
- Two readers of one file will disagree eventually; find the shared one before writing a second.
- An enumerated list silently exempts what it forgot.

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
| US0467 AC5's doc verifier is presence-only - survives an anchor rename and an added-but-unemitted documented field | not-stop-ship | claude-opus-5-author | 2026-08-04 |
| BG0419 AC5 is pinned by a grep over the unit's own prose | not-stop-ship | claude-opus-5-author | 2026-08-04 |
| `batch add-epic` and `batch swap` mutate a live batch without the ungroomed census | not-stop-ship | claude-opus-5-author | 2026-08-04 |

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
<!-- accuracy:end -->

- 22 points across 7 units. The two units that cost most were not the largest: BG0419 (5) needed four separate repairs each with a before-and-after mutant, and US0467 (5) was rejected and repaired. The three 2-pointers landed almost exactly as sized. What the points missed is REVIEW cost, not build cost.

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
| status.open_run crashed the dashboard on a structurally malformed run state | fixed-in: 060b8bd4 |
| open_run hand-rolled a second reader of run-state.json | fixed-in: 060b8bd4 |
| Three units over-declared their Affects | fixed-in: 060b8bd4 |
| BG0477's second mint site was wired but unexercised | fixed-in: 060b8bd4 |
| US0467 AC5's doc verifier is presence-only | declined: the anchor clause is gated by the check_links pre-commit lane, and the prose-against-prose shape belongs with BG0457 |
| BG0419 AC5 is pinned by a grep over its own prose | declined: same shape, same home |
| batch add-epic and batch swap skip the ungroomed census | BG0512 |

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
