# RETRO-0063: RUN-01KY1WCR: three tests were half the suite, and the premise was wrong three times

> **Date:** 2026-07-21
> **Batch:** US0284, US0285, US0286, US0287
> **Goal:** done
> **Delivered:** 4 / 4   **Blocked:** 0

## Delivered

- **US0284** (3pts) - `GateRealWrapperTests` ran the full ~35s gate over this repo twice: once to assert shape, once to learn that `main` returns 0 or 1. One lazy run now serves both, with `main` pinned against a stub. `test_gate.py` 72.2s -> 36.2s; the stubbed test alone 35.451s -> 0.001s. One unstubbed end-to-end run kept deliberately.
- **US0285** (2pts) - the never-rolled evidence-log pin drove 5,050 records through `record()`. It now seeds the log past the cap in one write and appends one record: identical failing condition, sharper attribution. 10.4s -> 0.259s.
- **US0286** (5pts) - `engagement_floor.detect` ran `git log --grep` once per shipped unit (842 subprocesses); `project_override` re-parsed `.config.yaml` on every call (4,495 times per validate run). One git pass; parse memoised on file content. `run_gate` 35.6s -> 6.95s.
- **US0287** (2pts) - RFC0048 D6 closed: a 120s per-commit budget against a measured 93.1s baseline, advisory, reporting trend not just verdict, reading the latest run not the median.

**Whole gate: 196.7s -> 93.1s per commit. Suite: 153.1s -> 78.6s over 3,418 tests (up from 3,409).**

## Blocked / deferred

- None delivered short. `test_sprint.py`'s 19.3s was deliberately left out of scope at plan time: it is diffuse (~100ms across 238 tests, no hotspot), so it is a different problem from the three concentrated ones and would have been a worse ratio.
- The run is built and adversarially reviewed (REJECT round 1, repaired) but NOT closed: it still needs a reviewer of record to sign off before the four stories reach Done.

## What went well

- **Measuring before planning changed the plan.** RFC0048's cost table was two days old. Re-measuring found `test_gate.py` had grown 28% in that time, and profiling INSIDE the files found three tests were 53% of the suite - a target the file-level view could not see.
- **Every unit was mutation-checked during the build, per-unit, as it landed.** 9 mutants killed. No separate close-time pass was needed, and each kill was cheap because the context was live.
- **Equivalence was proven on the real corpus, not just the suite.** `gate --format json` byte-identical before and after US0286 across all 15 lanes - evidence the unit tests structurally cannot provide.
- **The budget lane reported on its own commit** (`99s of a 120s budget, +6% since`), so D6's mechanism was dogfooded the moment it existed.

## What was hard / what stalled

- **All three substantive stories were planned on a premise the build falsified.** US0286: the cost was not corpus re-walking (0.105s) but per-unit git subprocesses and per-call YAML re-parsing. US0285: the planned small-injected-cap test would have passed whether or not the log rolled, because `roll_jsonl`'s default binds at definition time. US0287: the planned shipped `gate.py` lane would have been permanently silent in every consuming project, because the hook machinery is repo-only. Each cost a rewrite of the story mid-build.
- **Planning artefacts needed a grooming pass the scaffold could not give.** `artifact.py new --ac` pairs with `--verify` positionally, not via a `|` separator, and it auto-backticks identifiers inside what I intended as commands - so all four stories' AC blocks had to be hand-rewritten into Given/When/Then form.
- **`Affects` was under-declared at plan time** on US0286, so the planner reported it as safely parallel with US0284 when both would edit `test_gate.py`. Caught by re-reading the waves, not by a tool.

## Lessons

- **Profile inside the file before optimising it.** The file-level table said "attack test_gate.py"; the profile said "two tests". The same table said "three lanes re-walk the corpus"; the profile said "842 git subprocesses and 4,495 YAML parses". A cost attributed to the wrong cause produces a plausible plan that fixes nothing.
- **Read the binding rules of the thing you intend to inject before designing a test around injecting it.** A default argument binds at definition time, so patching the module constant it was defaulted from changes nothing - and the resulting test passes whether or not the behaviour is present. Making a test cheaper is exactly when vacuity is easiest to introduce, because the change looks like a simplification.
- **Ask where the data lives before deciding where the check lives.** A check placed away from the data it reads is not wrong so much as inert: it degrades to permanent silence, which reads identical to permanent success.
- **A trend against a dated baseline catches what a ceiling cannot.** `test_gate.py` grew 28% in two days while under every threshold in force. A budget that reports only pass or fail would have stayed green throughout.
- **Narrowing an exception clause is a behaviour change, not a tidy-up.** Moving a read out of a broad `except` and catching only `OSError` let `UnicodeDecodeError` - a `ValueError` - escape a function documented as never raising. The refactor looked like it only changed cost.
- **A guard must be tested for the MECHANISM, not the spelling that prompted it.** The structural check matched one literal call form; the regression it existed to prevent used another, and walked straight back in. Where a guard can be a runtime refusal on the path everything shares, prefer that to a source-text match.
- **A baseline the check cannot itself reproduce is not a baseline.** 93.1s was a hand-sum of three separately timed runs; the hook's own measurements of the same work were 99s and 83s. Measure the thing with the instrument that will do the measuring.
- **Prose written to justify code is code that has not been reviewed - for the third sprint running.** Two of this review's three MAJORs were comments asserting a property the code did not have ("same answer as before"; "the expensive lanes ran either way"). Both read as reassuring and both were false.

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

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US0284 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0285 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0286 | 5 | 125,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0287 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 4 unit(s) measured; 4 of 4 forecast at plan time.**
Unmeasured: US0284, US0285, US0286, US0287. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- {{what the ratio implies - which units the estimate missed, and why}}

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?**

Every finding gets a disposition: **file it**, or **decline it with a reason**. Both are green.
What does not pass is silence.

| Finding | Disposition |
| --- | --- |
| 9 mutants were killed this run and none is recorded anywhere but prose; the close lane still reads a report from two sprints ago | already filed as **BG0238** (High) - this run is its third consecutive confirming instance |
| Two of the review's three MAJORs were false claims in comments, third sprint running | declined as a new backlog row: it is L-0146 recurring, already a standing lesson, and the countermeasure is RFC0050's plan-time pass plus the existing close review. Recorded here as its third confirming instance rather than refiled |
| `artifact.py new` accepts a pipe-separated `--ac` and emits a malformed AC silently | filed **CR0381**. My first statement of this finding was WRONG - I claimed the paired `--verify` was being backticked. Probing it showed a correctly paired `--verify` is emitted clean; the mangling came from my own misuse, cramming the command into `--ac`. The real finding is the silent acceptance, and it is smaller. A finding is a hypothesis (L-0136) |
| All three substantive stories were planned on a falsified premise, each caught only during the build | declined as a defect: it is the case FOR **RFC0050**'s plan-time adversarial pass and belongs there as evidence, not as a separate backlog row. Recorded in RFC0050 as this run's supporting data |
| `test_sprint.py`'s diffuse 19.3s remains unattacked | declined for now: no hotspot, so it is a broad refactor with a worse ratio than anything delivered here. RFC0048 D1 records it as deliberately out of scope, not forgotten |

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
