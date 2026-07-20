# RETRO-0060: The sprint's instruments tell the truth and its stops respect the operator: mutation and velocity records are trustworthy, and a run asks bounded, structured questions instead of stalling in prose

> **Date:** 2026-07-20
> **Batch:** BG0215, BG0218, US0277, US0278, US0279, US0280, US0281, US0282, US0283
> **Goal:** The sprint's instruments tell the truth and its stops respect the operator: mutation and velocity records are trustworthy, and a run asks bounded, structured questions instead of stalling in prose.
> **Delivered:** 9 / 9   **Blocked:** 0

## Delivered

- BG0215 (3 pts) - a SIGKILLed mutation run no longer poisons the next run's restore:
  originals persisted to an in-flight sidecar before each mutant lands, recovered before the
  baseline, unreadable sidecar refuses with the git remedy named (f977d97)
- US0277 (2 pts) - the mutation report names the test files its command selects; a test pins
  the recorded test_cmd, which L-0149's check found already shipped (fda7a6a)
- US0278 (3 pts) - a test file referencing the target but outside the selection is warned as
  the manufactured-survivor condition; advisory, never blocking (fda7a6a)
- BG0218 (3 pts) - VELOCITY.md's Points column is the delivered-points series; ratio columns
  keep their forecast gate; RETRO0058 backfilled live, Points went from unrecorded to 14 (bb0fa03)
- US0279 (3 pts) - the close captures the harness-tracked token total itself, cache reads
  excluded, and the velocity row records the actual (9e236f3)
- US0281 (3 pts) - operator questions are structured decisions: named options with
  consequences, the recommendation marked with its reason (dee4747)
- US0280 (5 pts) - an undecidable unit is deferred and the batch continues; accumulated
  decisions asked together; the autonomous path records and blocks, never defaults (dee4747)
- US0282 (5 pts) - a blocked close offers file-and-close: administrative blockers filed as
  CRs linked to the run, deferrals named in retro and anchor, outcome closed-outstanding (ee517f8)
- US0283 (3 pts) - repeated closes report the outstanding-set trend; a hard correctness
  blocker refuses the file-and-close exit outright (ee517f8)

## Blocked / deferred

- none - every unit reached its gate

## What went well

- Dogfooding closed the loop inside the sprint: BG0218's fix backfilled RETRO0058's velocity
  row live, this close's mutation evidence run printed US0277/US0278's own selection listing
  and out-of-selection warnings, and the close itself exercises US0279's token capture
- L-0149 paid immediately: US0277's "record the test command in the JSON" was already
  shipped, so the story cost a pinning test instead of a rebuild

## What was hard / what stalled

- The pre-commit gate cost three blocked commits: the test-noise ratchet caught the new
  WARNING lines the moment they landed (fixed by capturing the two uncaptured main() call
  sites, baseline lowered 134 to 132), `git commit -a` leaked GIT_* env into the suite lanes
  and broke every git-invoking test in ways invisible standalone (filed BG0222), and
  reference-sprint.md hit its 600-line budget (allowlisted at 625, deliberately, for two new
  loop steps)
- The upsert trap: the first "already recorded - not overwritten" implementation dropped the
  recorded actual while claiming to protect it, because record_velocity rewrites the whole
  row; the guard's own red test caught it before it shipped

## Lessons

- The hook environment is part of the test environment: a suite green in a shell can fail
  under `git commit -a` because the hook inherits GIT_INDEX_FILE, and every git call inside
  a test's temp fixture then acts on the outer repo - sanitise the lane's env, or the
  failure reads as flaky tests
- An upsert that rewrites the whole record can erase the very field it was told not to
  overwrite: "do not overwrite" must be implemented as "reuse the existing value", never as
  "omit it"
- A mutant that lands in a test file and survives is expected, not a finding: stubbing a
  test's body makes the suite pass vacuously by construction - scope the evidence run's
  survivor reading to product files

## Estimate vs actual

**Were the estimates any good?** The plan forecast a token cost per unit; telemetry recorded
what each one actually cost. This section holds the comparison, so the question is asked every
sprint instead of only when someone remembers to ask it.

Generate it: `scripts/retro.py accuracy --id RETROxxxx --write` - it fills the block below from
the batch's telemetry and appends this sprint's row to `retros/VELOCITY.md`.

A unit with no per-unit telemetry record has its PER-UNIT ratio reported as **UNMEASURED** and
excluded from that ratio - it is never counted as accurate. But the token count itself is NOT
unmeasurable: the harness tracks it deterministically. An INTERACTIVE sprint (no runner) records no
per-unit actual, so the close captures the harness-tracked sprint total itself (`accuracy
--tokens-from-harness`, run by `sprint close --apply-signoff`) and the velocity row records it; when
the capture fails, the close states why and `accuracy --tokens N` remains the manual override.
Report it as **not-yet-captured** only while neither has happened, never as if the number were
unknowable. That figure is DESCRIPTIVE, never a target (see CR0273).

The forecast is a hypothesis, not a settled calibration. Read the ratio, write down what it
implies, and change the constants only on evidence a human has looked at - a fit to a couple of
sprints fits noise.

<!-- accuracy:begin (generated by retro.py accuracy --write) -->
<!-- accuracy:end -->

- The plan forecast 750,000 tokens (30 points at the ~25,000/pt seed). The block above is
  generated at close with the harness-captured actual - the first calibrated Fable row in
  this project's history, to be read against the operator's own heuristic (Opus measured
  ~50k/pt on RETRO0028; Fable hours run roughly double Opus, tokens previously uncalibrated)

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?**

This is the question that turns a retro into work. Every finding gets a disposition:
**file it**, or **decline it with a reason**. Both are green. What does not pass is
silence - a finding written down and left to rot.

To say "nothing worth raising", say so in a row and give the reason. An empty table is
not an answer.

| Finding | Disposition |
| --- | --- |
| refine --into appends a duplicate epic-level AC heading, failing MD024 in the repo's own markdown gate | BG0221 (filed at plan time) |
| suite lanes break under `git commit -a`: hook GIT_* env leaks into the tests' own git calls | BG0222 (filed mid-sprint) |
| interactive token capture records the total but not the delivering model, so the velocity row books under the unrecorded-model cell | CR0373 (filed at close; operator's cross-model calibration needs it) |
| test-noise baseline moved 134 to 132 by capturing, not raising | declined: the ratchet worked exactly as designed - nothing to file |
| round-2 MINOR: the file-and-close re-run refusal over-reaches for budget-spent/stopped runs, with a false already-closed message | BG0223 (filed at close) |
| round-2 NOTE: an explicit `--tokens 0` cannot clear a recorded velocity actual | BG0224 (filed at close) |
| a live mutation run mutates the shared working tree with nothing surfacing the window - the whole session froze by hand and the review was delayed to keep its evidence clean | CR0374 (filed at close) |
| the close-owed detector token-matches the Batch line, so 'EP0090 (US0276)' left US0276 reading owed until reworded | BG0225 (filed at close) |
| bare `status.py` errors instead of defaulting to the pillars dashboard - one retry at every session start | CR0375 (filed at close) |

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

- Tokens: captured at close by `--tokens-from-harness` (accuracy block above) · Duration: one
  session, 2026-07-20, run-state elapsed recorded at close · Critic rejects: 1 (round 1
  REJECT, 2 MAJOR + 5 MINOR + 2 NOTE, all repaired test-first in one round)

## Critic loop, observed

Round 1 (independent QA-seat instance, refute framing, full diff) REJECTed: both MAJORs were
truths this sprint creates being destroyed by an ordinary re-run - the recorded interactive
token actual erased to 0 by a plain `accuracy --write` (the guard lived only inside the
capture flag; moved into the writer itself), and `--file-and-close` re-runnable against a
closed run, duplicating the CR set and both annotation sections (now refused on a terminal
outcome or an existing filing). MINORs: a valid-JSON-non-object sidecar crashed instead of
refusing; a goal-less run could file-and-close (sprint-goal is now a hard stage); `--ignore`d
pytest paths counted as selected, silencing the manufactured-survivor warning; `decision`
tracebacked on a corrupt run state; and nothing mechanically asked the pending decisions at a
stop (the close now renders the queue). Every repair was seen red first. Round 2: the same
reviewer instance re-ran all seven round-1 reproductions verbatim against the repaired tree
and probed the repairs for what they created - APPROVE, with one non-blocking MINOR (the
re-run refusal over-reaches for budget-spent/stopped runs, BG0223) and one NOTE (an explicit
`--tokens 0` cannot clear a recorded actual, BG0224) filed rather than repaired in-round.
The recurring pattern held a fifth consecutive round: the sharpest defects sat between the
code and its own prose claims.
