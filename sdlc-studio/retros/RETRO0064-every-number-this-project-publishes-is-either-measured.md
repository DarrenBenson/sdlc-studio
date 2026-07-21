# RETRO-0064: Every number this project publishes is either measured or refused, and the test suite cannot reach the repository that runs it

> **Date:** 2026-07-21
> **Batch:** BG0227, BG0235, BG0230, BG0236, BG0238, BG0228, BG0229, BG0233, BG0237, BG0239
> **Goal:** Every number this project publishes is either measured or refused, and the test suite cannot reach the repository that runs it.
> **Delivered:** 10 / 10   **Blocked:** 0

## Delivered

All ten, 21 points, one wave. The batch was the whole open-bug backlog, chosen because seven of
the ten were one defect class: a number or a gate reporting something that was never measured.

**Evidence honesty**

- BG0236 (3) - the close captured the harness meter's ABSOLUTE reading, which is cumulative per
  session, so a second sprint in one session booked the first's spend. `open_run` now stamps a
  baseline and the close reports the delta, with no fallback: a baseline-less run says
  NOT-ATTRIBUTABLE rather than producing a plausible number.
- BG0238 (3) - mutation evidence was one blob, last-write-wins, stale-keyed on a repo-wide
  `git_rev`, so per-unit runs never survived to the close. Now a bounded ledger keyed on each
  target's content hash, with the gate lane judging coverage of the changed surface.
- BG0239 (2) - the budget recorded a total whenever the suite lane was INVOKED. Now gated on a
  loader-error fact and a test-count floor, deliberately NOT on duration.
- BG0229 (2) - a missing `--spec` read as an empty spec and reported a clean matrix; now refused
  with exit 2, distinct from exit 1 and exit 0.

**Suite safety**

- BG0230 (3) - a fixture's git call could be redirected at the parent repo by the ambient
  environment. Variables dropped AND discovery fenced, with a sweep so a fifth scrub-list copy
  cannot arrive unpinned.
- BG0237 (2) - two tests failed from an installed copy; made hermetic rather than skipped, and the
  dev-repo rule single-sourced into the one helper that reaches the real gate.

**Pins, no behaviour change**

- BG0227 (1) - the code fix already existed at HEAD; only the pin was missing.
- BG0233 (2) - two named surviving mutants killed.
- BG0235 (1) - ceiling and neutrality classes pinned behaviourally rather than symbolically.
- BG0228 (2) - `repo_map` wrote its map relative to the cwd.

## Blocked / deferred

- None. No unit was quarantined and the loop guard never fired.
- RFC0048 D2 authorised test retirement but SEQUENCED it behind CR0377 and BG0238 rather than
  building it now, so that is a deliberate deferral rather than a blockage.

## What went well

- **The batch had a real theme, and it paid.** Selecting on defect class rather than on priority
  meant the ten units reinforced each other: BG0236, BG0238 and BG0239 are the same failure in
  three surfaces, and fixing them together made the shared principle explicit instead of leaving
  it implicit in three separate patches.
- **Mutation found what review and tests did not, again.** 75 mutants across the build; 5 SURVIVED
  first time and each drove a second fix. Every one of those five was a test that read as coverage
  while pinning nothing. No amount of reading found them; mutating did.
- **The parallel fan-out held.** Four file-disjoint clusters, no worktrees, no commits by workers,
  central index and CHANGELOG. Zero merge conflicts and zero index corruption.
- **Declining to reproduce a hazard the filed way was correct.** BG0230 is about git environment
  pollution and its filed steps would have run against the live repo; every reproduction went into
  a purpose-built victim repo instead. L-0158 exists because that lesson was learned the hard way.
- **Agents reported what they could NOT verify.** The bounded hole in BG0230 (35 bare git calls),
  the declined vacuity in BG0229, the out-of-scope edit in BG0233's cluster - all volunteered
  rather than discovered later. That is the difference between a report and a claim.
- **The pre-commit gate caught an accidental `git commit -a`** that this session triggered through
  shell command substitution while filing a bug. Nothing was committed.

## What was hard / what stalled

- **The review REJECTED, and it was right twice.** Both MAJORs were prose asserting a property the
  code did not have - the class this repo has now shipped for FOUR consecutive sprints.
- **MAJOR 1 was the sprint's own sin, inside the fix for it.** BG0238's coverage lane counted a
  file as covered when no mutant had run on it, because it overlaid the report's `target_hashes`
  (written for every target, unconditionally) on top of the ledger (which correctly applies the
  verdict rule). The careful rule was written in one place and bypassed in its consumer. On this
  repo it replaced an honest "STALE, this report is about another change" with a coverage
  percentage about the PREVIOUS sprint's file set.
- **The deleted guard was deleted on evidence from the wrong surface.** BG0238's own resolution
  removed an `if not refused` check reasoning that the verdict rule already excluded refused
  targets. True of the ledger. False of the report the gate actually reads.
- **The unreachable-guard trap was hit twice in one sprint**, by two different authors, on two
  different files (BG0237's `_report()` guard and BG0236's `_session_baseline` backstop). Both
  survived their mutants because every caller guarded first, so the guard read as coverage while
  pinned by nothing.
- **Filing a finding executed a command.** Passing reproduction steps as a shell argument meant
  backticked prose was command-substituted: once silently deleting two commands from a bug's Steps
  section, once running `git commit -a` twice against the live repo. Filed as CR0384.
- **Capacity was over the configured appetite** (10 units against 8) and was raised deliberately
  rather than by drift. That was the right call on recent history, but it is the second lever
  after batch theme that made this a long sprint.

## Lessons

- **A rule enforced in the producer is not enforced in the consumer.** BG0238's ledger applied the
  verdict rule correctly and the gate then overlaid the raw report on top of it, so the careful
  rule was bypassed by the surface that reads it. When you write a rule about what counts as
  evidence, go and check every reader of that evidence, not just the writer.
- **Deleting a guard requires evidence from the surface the guard protects.** The `if not refused`
  check was removed because the ledger already excluded refused targets. That was verified against
  the ledger and never against the report. A guard's redundancy must be proven where it sits.
- **A guard every caller already short-circuits is not covered by its callers' tests.** Hit twice
  this sprint, by different authors. If deleting a guard leaves the suite green, the guard is
  either dead or untested - decide which, and never leave it reading as coverage.
- **Do not judge a measurement by the history of that same measurement.** BG0239's filed fix
  suggested a duration band to validate a duration; it is circular, and it would have rejected the
  real 196.7s -> 99s improvement as implausible. Judge a measurement by what the run DID.
- **Refuse a total rather than return a short one.** A skipped malformed record yields a quietly
  low sum, and a low baseline inflates every delta measured against it. Missing is cheap, wrong is
  expensive - the sprint goal, applied to the sprint's own fixes.
- **A literal count in prose rots.** "206 tests" was true when written, wrong when the reviewer
  read it, and wrong again an hour later. Put the count in the runner's output, not in a claim
  nobody re-runs.
- **Prose that justifies code is the least-reviewed code in the repo** - four sprints running now.
  Every comment asserting "this is equivalent", "nothing is lost" or "the fallback takes over" is
  an untested claim until something executes it.
- **Reproduction steps are executable content and must never be passed through a shell.** The
  field most likely to contain commands is the field most likely to be executed.
- **Building the recorder is not the same as recording.** BG0238 made mutation evidence able to
  accumulate, and the sprint still closed with none: the ledger is written by `mutation.py`, while
  the practice is a builder hand-applying a mutant. 75 mutants were applied and the lane reported
  0/4. Ask where the evidence is PRODUCED before deciding where it is stored.
- **A lane that reads red when the policy was followed will be ignored**, and is indistinguishable
  from a broken one. The remedy is a way for the practice to record itself, never a quieter lane.
- **When a gate reports an absence, check whether the absence is real before filling it.** The
  first reflex at this close was a blanket mutation sweep to make 0/4 go green - which would have
  mutated code no changed test pins, sampled under 1% of the enumerated mutants, and buried good
  per-unit evidence under weaker aggregate evidence. The operator caught it.

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
| BG0227 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0235 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0230 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0236 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0238 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0228 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0229 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0233 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0237 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0239 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 10 unit(s) measured; 10 of 10 forecast at plan time.**

**Velocity: 10.81 points/elapsed-hour** (21 points over 1.943h, run-state, ceremony included). This is the planning number - points per SESSION within the observed single-session envelope; it is NOT a linear per-point rate to extrapolate to a 1-point or 100-point sprint, and it is descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).
Unmeasured: BG0227, BG0235, BG0230, BG0236, BG0238, BG0228, BG0229, BG0233, BG0237, BG0239. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- **This sprint says nothing about estimate accuracy, and that is recorded rather than papered
  over.** 0 of 10 units carry per-unit telemetry, so no unit is rated and the batch ratio is n/a.
  All 10 were forecast at plan time (21 points at TOKENS_PER_POINT=25000 = ~525,000), so the
  forecast exists and simply has nothing to be judged against.
- **The token actual is NOT-ATTRIBUTABLE, by design and for the right reason.** This run was
  opened before BG0236's baseline existed, so the delta cannot be derived, and no baseline was
  retrofitted because a baseline invented after the fact is the same lie in a new place. That is
  the third consecutive close with no token figure - the first two because the capture was wrong,
  this one because the capture correctly refuses.
- **The close then published a false zero anyway**, in a different column: `Actual (tokens)` is
  fed by the sum over RATED units, which is 0 when none are rated. Corrected by hand for the third
  sprint running and filed as BG0244. The estimator's own series is still the least trustworthy
  number this project produces, and it will stay that way until a sprint runs with a baseline
  stamped at plan time - which the next one will be the first to have.

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
| Two more scripts write relative to the cwd, ignoring or failing to discover the root | BG0240 |
| A spec that is present and readable but has no AC Coverage Matrix still reports clean, exit 0 | BG0241 |
| 35 bare `subprocess` git calls in 8 modules bypass the confined helper; BG0230 does not reach them | BG0242 |
| A token delta can be stamped on a retro other than the open run's | BG0243 |
| RFC0048 D4: a test audit lens profile, for the prose defects mutation cannot detect | CR0382 |
| 62 scripts declare `--root` and one discovers it - a missing convention, not 3 separate bugs | CR0383 |
| Filing a finding passes every field through a shell, so reproduction steps get executed | CR0384 |
| Four doc surfaces still describe only the single-blob mutation report | CR0385 |
| The mutation coverage lane counted unmutated files as covered (review MAJOR 1) | BG0238 - repaired in round 2, in the unit it was raised against |
| `session_tokens` raised on a malformed transcript, so no run could be minted (review MAJOR 2) | BG0236 - repaired in round 2, in the unit it was raised against |
| `ScopeTests` sat below the main block, invisible to a direct run (review MINOR 3) | BG0239 - repaired in round 2, in the unit it was raised against |
| The cross-session token guard disabled itself on a sourceless baseline (review MINOR 4) | BG0236 - repaired in round 2, in the unit it was raised against |
| `repo map build` changed its input surface, not only its output path (review MINOR 6) | declined: it is the root-discovery convention the project is moving towards, so it was DOCUMENTED in the CHANGELOG as a deliberate behaviour change rather than reverted |
| A literal test count in a bug's Resolution had already rotted (review MINOR 7) | declined: correcting the number would only reset the clock, so the rotting claim was removed instead and the count left to the runner |
| `wsjf-inputs.json` is 11 days stale, so ordering fell back to priority | Declined: the whole backlog was in the batch and nothing declared `Depends on:`, so ordering could not change the outcome. It matters again the moment a batch is a subset |
| The velocity row published `Actual (tokens) = 0` when no unit was rated - an absence rendered as a measurement, found by dogfooding this sprint's own close, and the hand correction was then OVERWRITTEN by apply-signoff rewriting the same row | BG0244 |
| BG0238's ledger records only `mutation.py` runs, but the per-unit practice is hand-applied mutants, so the lane reads 0/N after a sprint that followed policy | BG0245 |
| 208 units are grandfathered under the engagement floor's `adopt_after` | Declined: pre-existing debt, unchanged by this sprint, and forward-only by design |

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

- **Tokens:** NOT-ATTRIBUTABLE. The run predates BG0236's baseline, so its delta cannot be
  derived and none was retrofitted. Not "unmeasured" and not zero - refused, which is the
  behaviour this sprint shipped.
- **Duration:** not recorded. An interactive sprint's wall-clock counts operator-away gaps as
  sprint time, so no elapsed was supplied rather than a wrong one being invented.
- **Critic rejects:** 1 (round 1 REJECT, 2 MAJOR + 7 MINOR; round 2 APPROVE by the same reviewer
  re-running its own reproductions, 3 further MINOR all fixed before close).
- **Mutants:** 75 in the build with 5 surviving first time, 12 across repair and re-verification,
  1 surviving at re-verification. Every survivor was a test that read as coverage while pinning
  nothing; all six are now pinned.
- **Gate:** 110s against a 120s budget (baseline 99s, +11%), recorded because the suites ran their
  full scope. Suites 3,524 skill + 273 tool green, noise 132/132, drift 0.

## Handoff

- [HO-0018](../handoffs/HO0018-every-number-this-project-publishes-is-either-measured.md) - 0 remaining item(s): 0 copilot-tail, 0 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
