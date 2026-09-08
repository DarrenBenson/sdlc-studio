# RETRO-0115: RUN-01M1YK70: the delivery loop learned to refuse, and the seats still found the branches the fixtures could not reach

> **Date:** 2026-09-08
> **Batch:** BG0653, BG0652, BG0614, US0818, US0815, US0816
> **Goal:** the delivery loop refuses before the seats do
> **Delivered:** 6 / 6   **Blocked:** 0

## Delivered

- **BG0653** (cd064d55, 79f306b3) - a staged test rename or deletion that orphans a stamped
  `Verify:` selector is refused at pre-commit by the new `stamps-staged` lane, which resolves the
  index blobs by AST in all four selector shapes and reports a stamp already dead at HEAD rather
  than refusing it. The rename that started this went unseen for three weeks because the corpus
  lane that would have caught it was red and unread.
- **BG0652** (6958c360) - `status.py hint` runs inside one `corpus_cache()` sweep: 57 s to under
  a second on this corpus, pinned by a bound and by an identity check that the same cache object
  reaches every advisory.
- **BG0614** (ae8a1c5b, 82b57ae8) - `mutation.py audit` names every `(unit, criterion, row)` key
  the ledger holds more than one live row for, with each row's verdict, test, target, hash and
  mutant description, tags rows whose entry is stale or whose target is missing, and refuses a
  ledger it cannot parse instead of reading it as clean.
- **US0818** (d97530bb, b328a7f0, 9d468790) - `register` replaces the identical live row instead
  of appending a duplicate, refuses a disagreeing verdict or test, and prints the retraction as a
  runnable command: every join field, the live row's own line and description, shell-quoted.
  Collapsing duplicates an older ledger already held takes their tallies down with them.
- **US0815** (73dcf877, 66751edb, a49a5244) - `verify_ac run --coverage` names every line a unit
  itself added that its own verifiers never executed, attributed by `git blame` to the unit's own
  commits or to the working tree, following child interpreters, refusing when the measurement
  cannot be trusted rather than reading a failure as zero.
- **US0816** (da7c3920) - the Fixed and Done gates read that measurement. `review.line_coverage`
  is `report` by default, `block` here from 2026-09-07, `off` collects nothing, and an unknown
  value is refused by name. A line ruled equivalent through `verify_ac coverage rule` is
  subtracted and counted in the depth field.

## Blocked / deferred

- **US0817** (CR0565, the self-run gate) - regroomed to 8 points at plan time and deferred: three
  8-point units in one batch did not fit the appetite, and the seats left four open design
  questions on it. It opens the next run.
- Nothing in the batch was blocked. Twelve commits stand unpushed at the close; the push is the
  operator's.

## What went well

- **The gate this batch built caught its own builders.** `verify_ac run --coverage` was run on
  US0815 and US0816 before either was briefed. On US0815 it named thirteen unexecuted added lines
  and a new file measured as zero statements, which produced six mutants and a real fix; on
  US0816 it named one line, an unused branch of the test's own fixture, removed rather than ruled.
- **Every rejection was repaired inside the run.** Eight of thirty-three delivery verdicts were
  REJECT, each on a branch a fixture could not reach, and each closed by execution in the next
  round rather than by argument.
- **The mutation ledger held under 87 live rows across six units** on shared files, with the rows
  of ten earlier units re-measured after every edit that drifted them. `mutation.py audit`, built
  in this batch, is what made the duplicate keys visible at all.

## What was hard / what stalled

- **Shared-file ports cost more than the units.** Every patch that touched `verify_ac.py`,
  `mutation.py` or `AGENTS.md` staled the rows of units delivered weeks ago, and the
  `evidence-drift` lane refused two commits until each was re-measured by hand. One refusal
  cost a full ten-minute hook run to learn.
- **A reviewer committed on live main.** A QA subagent's probe ran `cd` inside a `$(...)`
  substitution, so its `git commit` executed in the live repository and replaced this session's
  US0818 commit subject with a fixture id. Content was intact and the hooks had passed; the
  message was restored by amend on the unpushed commit.
- **A killed runner left a mutant in the tree.** `pkill` on a scratch mutant runner skips its
  `finally`, and twelve rows were then registered against the residue's bytes. The coverage join
  found it: an uncovered added line outside the unit's own function.

## Lessons

- **A criterion that says "X, or Y" needs a fixture for both.** Six of the eight rejections were
  one clause of a criterion with no case reaching it: an uncommitted edit to a TRACKED file where
  the fixture used an untracked one, a stale data file the fixture wrote as prose that
  `coverage combine` cannot read, a ledger that cannot be parsed, a missing target beside a stale
  one. The mutant table written at plan time cannot name a branch that does not exist yet.
- **A message that claims to be runnable must be RUN by its test.** The refusal US0818 ships
  printed a `retract` command that a shell mangles, because 67 of the ledger's 430 live rows carry
  a backtick and a pasted argument is command substitution. The test now splits the printed line
  with `shlex` and executes it.
- **A tool failing between two calls is not an absence of findings.** Coverage's own `combine` and
  `json` verbs failing read as no data and therefore as zero added statements at exit 0 - the gate
  satisfied by the instrument breaking. Every such path now refuses by name.
- **Re-measure by target, not by unit.** Before porting a patch, list every delivered unit with
  live rows on each file it touches and chain their runners after it. `AGENTS.md` alone carries
  rows for four units.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- Run the shipped lane on THIS repository before briefing a unit, not only on the fixture.
- Write a fixture for every clause of a criterion, and a mutant for every branch of the diff.
- A message claiming a command is runnable is a claim its test must execute.
- An instrument that fails must refuse, never report zero: an absence is not a clean reading.
- Before porting a patch, re-measure every delivered unit holding rows on the files it touches.

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
| BG0490 | not-stop-ship | Claude Fable 5.1 | 2026-09-08 |
| BG0493 | not-stop-ship | Claude Fable 5.1 | 2026-09-08 |
| BG0567 | not-stop-ship | Claude Fable 5.1 | 2026-09-08 |
| BG0578 | not-stop-ship | Claude Fable 5.1 | 2026-09-08 |
| BG0591 | not-stop-ship | Claude Fable 5.1 | 2026-09-08 |
| BG0601 | not-stop-ship | Claude Fable 5.1 | 2026-09-08 |
| BG0608 | not-stop-ship | Claude Fable 5.1 | 2026-09-08 |
| BG0612 | not-stop-ship | Claude Fable 5.1 | 2026-09-08 |
| BG0627 | not-stop-ship | Claude Fable 5.1 | 2026-09-08 |
| BG0630 | not-stop-ship | Claude Fable 5.1 | 2026-09-08 |
| BG0633 | not-stop-ship | Claude Fable 5.1 | 2026-09-08 |
| BG0637 | not-stop-ship | Claude Fable 5.1 | 2026-09-08 |
| BG0638 | not-stop-ship | Claude Fable 5.1 | 2026-09-08 |
| BG0654 | not-stop-ship | Claude Fable 5.1 | 2026-09-08 |
| CR0511 | not-stop-ship | Claude Fable 5.1 | 2026-09-08 |

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
| BG0653 | 5 | 152,080 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0652 | 1 | 30,416 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0614 | 3 | 113,661 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0818 | 2 | 60,832 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0815 | 8 | 243,328 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0816 | 8 | 243,328 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 6 unit(s) measured; 6 of 6 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes, by phase - read from the two verdict ledgers:

  test-plan review: 29 pass(es) over 6 unit(s), 11 rejected

  code review: 24 pass(es) over 5 unit(s), 12 rejected

  ratio: 0.83 code-review pass(es) per test-plan pass - the claim EP0207 is judged on, as a number
Unmeasured: BG0653, BG0652, BG0614, US0818, US0815, US0816. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- The batch was 27 points against a 35-point appetite after US0817 was deferred, and it took one session. The per-unit ratio is read from the block above; where a unit carries no telemetry row the ratio is UNMEASURED rather than assumed.

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
| `close_owed.owed()` walks the whole corpus un-swept at three callers, 43 s per call | CR0511 |
| BG0652's identity pin compares `id()` of dicts with non-overlapping lifetimes | CR0511 |
| The audit's remedy names `retract` for rows whose provenance retract refuses | CR0511 |
| Two catalogue omissions in `reference-scripts.md`, one truncated since 2026-07-09 | CR0511 |
| A non-integer `row` in a hand-edited ledger crashes the audit with a generic error | CR0511 |
| `verify_ac run --coverage` without `--id` measures only the first unit | CR0511 |
| `register` says it replaced an identical row when only the verdict and test match | CR0511 |
| US0818 AC3 names `plan_execution` where its test asserts the ledger's row count | CR0511 |
| The catalogue splice that garbled two bullets, and the audit's unreadable-ledger exit | fixed-in: 82b57ae8 |
| A printed retraction a shell mangles, and the unpinned live-row claim | fixed-in: 9d468790 |
| Two unpinned attribution branches, a verifier cut short, a base ref off HEAD's history | fixed-in: a49a5244 |
| An unused `raw=` branch in US0816's own config fixture | fixed-in: da7c3920 |
| A reviewer subagent committing on live main through `cd` inside a substitution | declined: a prompt rule now forbids writing git verbs outside the worktree, and the harness cannot gate a subagent's shell |

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

- Tokens: captured at the close from the harness meter · Duration: one session, 2026-09-07 to 2026-09-08 · Critic rejects: 8 of 33 delivery verdicts, plus 12 plan-review rejections before any code
