# RETRO-0057: A request closes itself when its children are all resolved, and the sweep that does it reports exactly what it did

> **Date:** 2026-07-20
> **Batch:** US0269, US0270, US0271
> **Goal:** A request closes itself when its children are all resolved, and the sweep that does it reports exactly what it did
> **Delivered:** 3 / 3   **Blocked:** 0

## Delivered

- **US0269** (3 pts) - `reconcile detect` reports `request-derivable`, asking
  `transition._request_terminal_gate` rather than deciding for itself whether the children are
  resolved. The gate IS the predicate, so the detector and the close it describes cannot drift.
- **US0270** (3 pts) - `reconcile apply` derives the terminal through `transition`, so the index
  row, the parent cascade and the telemetry event all happen exactly as a hand transition would.
- **US0271** (2 pts) - the derivation refuses what G2 refuses: no childless request, no unresolved
  child, and a no-op where the two-backlog workflow is unenforced.

Applied to this workspace: **35 requests derived Complete**, RFC0046 correctly refused. The
discovery backlog went 63 to 30. Suite 3,267 skill + 243 tools green.

## Blocked / deferred

- **RFC0046** - not blocked work, a correct refusal. Its children are all resolved but it carries
  an open decision D1, and the RFC accept gate deliberately cannot be `--force`d: the skip must
  leave its reason in the file. It stays as reported drift until someone closes D1 or records an
  override.

## What went well

- **The gate-as-predicate design held up under attack.** The reviewer tried to break the
  detector/gate agreement and could not: stubbing the gate's verdict moves the detector with it.
  This was the one structural decision made up front, and it is the one thing neither review round
  found fault with.
- **Two review rounds, both surfacing real defects, and the second was cheap** because the first
  had already forced the production-shaped fixture into existence.
- **The `_rfc_with_open_decision` fixture is the artefact that mattered.** Every prior fixture used
  a CR with a clean gate ladder, so not one of them could tell an honest preflight from a
  dishonest one.

## What was hard / what stalled

- **The change shipped claiming completions it had not verified.** Three of round 1's four MAJORs
  were honesty defects in a mechanism whose entire purpose is reporting what was closed: a
  preflight promising 36 where the run delivered 35, a refusal exiting 0 and absent from JSON, and
  a fix hint pointing at a command guaranteed to refuse.
- **The known defect class recurred inside the commit written to fix it.** `ac95397` fixed
  "tested the detector, claimed the apply path". Round 1 then found the apply-side `two_backlog`
  guard had no test at all - mutating both guards left the class green. Same class, same commit.
- **Two of my verification steps were themselves broken**, which is worse than a bug in the code.
  A mutation check ran a non-existent test class and the loader error read as a kill. A mutation
  run then timed out mid-flight, left the mutant on disk, and my restore copied that mutant into
  the backup - so the next "baseline" failure was the mutant, and I nearly diagnosed it as a
  regression.
- **The wrong reason nearly shipped as the record.** Round 2's only finding was a comment: I
  justified the gate not blocking with "no commit can clear it", which is false for the exact
  case it cites. The behaviour was right and the justification was wrong, which is the version a
  future maintainer inherits.

## Lessons

- **Establish the baseline before the mutant, and restore from a source the mutant cannot have
  touched.** A timed-out mutation harness leaves the mutant on disk; a `cp` restore then captures
  it, and every subsequent run measures the mutant while reporting on the code. Restore from git
  or a copy taken before the first mutation, and re-run the unmutated baseline first - a baseline
  that does not come back green means the harness is lying, not the code.
- **A test-runner error is not a test failure.** `FAILED (errors=1)` from a mis-named test class
  looks exactly like a kill. Any mutation result that does not name the specific test it killed
  is unverified.
- **Prose written to justify code is code that has not been reviewed.** Three sessions running,
  the surviving defect has been in a comment or a claim rather than in behaviour. A wrong reason
  attached to right behaviour is more dangerous than no reason: it is what the next person acts on.
- **Fixture noise hides vacuous assertions.** The shared story fixture wrote an unrewritable
  placeholder status, so every apply in the class emitted a spurious unapplied row - which meant
  the exit-code test would have passed on fixture noise rather than on the refusal it names. It
  was changed for tidiness and bought correctness by accident.
- A drift kind whose advertised remedy cannot clear it is worse than no hint: it sends the
  operator round a loop with no exit. Where a later gate refuses, name that gate.

## Estimate vs actual

**Were the estimates any good?** The plan forecast a token cost per unit; telemetry recorded
what each one actually cost. This section holds the comparison, so the question is asked every
sprint instead of only when someone remembers to ask it.

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US0269 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0270 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0271 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 3 unit(s) measured; 3 of 3 forecast at plan time.**

**675,000 tokens supplied, but no rate:** the batch has no delivered unit carrying Points, so there is no denominator. Size the delivered stories/bugs, or the rate stays uncomputable.
Unmeasured: US0269, US0270, US0271. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- 8 points delivered against a 675,000-token forecast for the batch. The build was a fraction of
  it; **the two review rounds dominated**, as they did in RETRO-0056 where three rounds cost over
  600,000 against a 425,000 forecast. That is now four consecutive runs where review, not
  construction, is the cost centre - the evidence base EP0085 / CR0358 exists to act on.
- The forecast treated this as unbuilt work when roughly 40 per cent was already delivered and
  committed. A plan that cannot see prior work over-forecasts the batch and under-forecasts the
  close.

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?**

| Finding | Disposition |
| --- | --- |
| Work was built and committed with no run open, so the planner read three delivered stories as unbuilt and forecast them | CR0366 |
| A mutation harness that times out leaves the mutant on disk; the restore then captures it, and later runs silently measure the mutant | BG0215 |
| `gate._reconcile` does not block on a derivable request behind a resolvable gate, so a delivered request can report PASS | declined: deliberate friction trade, cost stated in the code comment and `reconcile detect` still exits 1. Revisit if a real case is missed |
| `explain=True` costs ~0.1s per derivable item (~20 per cent on this repo's `detect`), paid in pre-commit | declined: acceptable at 36 items, and the alternative is restating each gate's precondition. Revisit if a consuming project reaches hundreds |
| RFC0046 will report drift indefinitely until D1 is closed or overridden | declined: that is the detector working. It is a real open decision, not noise |
| The lessons-summary gate lane cannot be satisfied when a lesson gist contains bold markup - the generator and the parser disagree, so the same lesson reports as both added and removed | BG0216 |

<!-- file one with: scripts/file_finding.py · check with: scripts/retro.py dispose --id RETROxxxx -->

## Close loop (gated)

`gate --require-retro RETRO0057` (this retro's id, file form) fails until all four are true:

- [x] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETRO0057`)
- [x] its lessons are in the project store, not just in this file (`retro.py extract --id RETRO0057`)
- [x] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [x] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: see Estimate vs actual · Duration: one session · Critic rejects: 1 (round 1, four MAJORs)
