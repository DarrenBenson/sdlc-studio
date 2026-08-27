# RETRO-0110: Zero open High, and a backfill that made the record prettier rather than truer

> **Date:** 2026-08-27
> **Batch:** BG0621, BG0615, BG0618, BG0607
> **Goal:** Zero open finding at High or Critical severity at close, with NO exceptions - measured on a checker hardened first so its green is evidence, and with any High raised during the run fixed inside it.
> **Delivered:** 4 / 4   **Blocked:** 0   **Verdict:** achieved

## Delivered

- BG0621 - the release bar could report MET while a High was open. Three ways, all in one file and duplicated across its two population readers: severity matched case-sensitively over a corpus holding seven bugs written `high`, only the literal status `Open` counted, and 21 files were skipped whole for a hyphenated heading. One shared reader now, status tested as NOT-TERMINAL, and a finding neither reader can parse is named rather than dropped.
- BG0615 - a guided-onboarding marker outranked the entire hint ladder for ever, because the check decided from its own `status` field and never from whether the stage's output existed. A marker written 2026-08-14 made `hint` answer `init guided` for twelve days in a project with 218 epics.
- BG0618 - a repair's evidence was split on a bare `;` and any fragment without a separator was DROPPED silently, so evidence containing a semicolon was truncated and 73 characters vanished with exit 0. Escapable separator, a scanner rather than a lookbehind, a JSON document route with no delimiter at all, and refuse-on-write with report-on-read.
- BG0607 - a unit's standing verdict was the last row written, so a panel's verdict was a fact about the order the recorder was invoked in. It is now the latest UNANSWERED rejection, keyed on the brief fingerprint rather than the reviewer's name.

## Blocked / deferred

- Nothing was blocked. All four reached Fixed.
- BG0620 was SUPERSEDED into BG0607 before any code was written: two pre-code reviews proved the two could not be separate units, because `record_repair` refuses a unit with no live REJECT and all nineteen read APPROVE under the shipped roll-up, so the backfill was not recordable until the roll-up shipped - while the roll-up was not shippable until the backfill landed.
- BG0607's residue is CARRIED as nineteen recorded waivers rather than repaired. Those rejections are real and cannot be answered retroactively without fabricating evidence.

## What went well

- The pre-code goal review earned its place twice over. It found the BG0607/BG0620 dependency INVERTED, found that reaching the bar would falsify both disclosure surfaces with no unit declaring them, and found two criteria that could not fail. Every one of those would have surfaced mid-run or at the close.
- Ordering by what the run itself depends on: BG0621 first, so the checker the goal is measured on was trustworthy before anything was measured on it. Its first run over real data found BG0131, unreadable by both readers since 2026-07-14.
- Every unit was reviewed at its own boundary and every review found something. Four reviews, four REJECTs, and not one was cosmetic.

## What was hard / what stalled

- The backfill. 53 closures written in one pass, 24 of them citing evidence the unit's own code declares invalid. It cost a full build-and-revert cycle and it is the single largest correction of the run.
- Repeated markdown and ratchet refusals on artefact prose - a literal pipe inside a table cell, nested code spans, a blank line inside a blockquote, a duplicate criterion glued onto a verifier line by a bad insert. Each is trivial and together they cost several commit attempts.
- One review agent stalled silently at 149 bytes for twenty minutes. LL0049 says to check the transcript's mtime rather than wait for a notification, and doing so is what caught it.

## Lessons

- **A repair that cites, as its evidence, the very thing the fix declares invalid has made the record prettier rather than truer.** BG0607 replaces a roll-up so that one seat's APPROVE cannot retire another seat's REJECT. Its backfill then closed 24 findings by citing exactly that: a later approval whose brief fingerprint differs from the rejection's. Nothing in the checker caught it, because a per-unit constant reads as evidence to anything looking for non-empty text. The test is not "is there evidence?" but "would this sentence read identically if the finding said something else?" - if yes, it is a formula.
- **A criterion whose subject is the CORPUS cannot be pinned by a mutant on the CODE.** AC5 asserted nineteen units were completely answered, and its declared code mutant survived: on a corpus where every unit is already complete, removing the completeness check changes nothing. Its mutant had to be a LEDGER mutant - delete a repair row. Three of BG0607's seven mutants ended up being document mutants for this reason, and that is a property of the criteria rather than a weakness in them.
- **When a model changes, the assumptions built on the old one become invisible rather than wrong.** `repair_state` read the single standing rejection. That was correct while a unit could carry only one live rejection, and the fingerprint-keyed roll-up ends that silently - 118 findings on six units became unreachable by the gate that decides whether a rejection was answered. Nothing failed. Ask, of any model change, which callers assumed the property you just removed.
- **A gate the run is measured on must be hardened before the run is measured on it.** BG0621 shipped first for that reason, and its first execution over real data found a finding invisible to both readers since 2026-07-14. A guard whose first run over the real corpus finds nothing has not been shown to look.
- **A test that drives the library while its mutant changes the CLI cannot fail.** This happened twice in one run - BG0618 AC5 and BG0621 AC7 - and both were found by re-executing the mutant rather than by reading the test. Re-execution is the only thing that distinguishes a passing test from a test that cannot fail.

## Carried lessons

- Verify the premise before building on it.
- A repair masks the defect beside it.
- A library test is not a lane test.
- An enumeration of a rule is a lower bound, not a boundary.
- Rule each repair CLOSED, OVER-CLAIMED or MOVED, not just reviewed.

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
| BG0490 | not-stop-ship | authoring session | 2026-08-27 |
| BG0493 | not-stop-ship | authoring session | 2026-08-27 |
| BG0567 | not-stop-ship | authoring session | 2026-08-27 |
| BG0578 | not-stop-ship | authoring session | 2026-08-27 |
| BG0591 | not-stop-ship | authoring session | 2026-08-27 |
| BG0601 | not-stop-ship | authoring session | 2026-08-27 |
| BG0603 | not-stop-ship | authoring session | 2026-08-27 |
| BG0608 | not-stop-ship | authoring session | 2026-08-27 |
| BG0612 | not-stop-ship | authoring session | 2026-08-27 |
| CR0496 | deferred | authoring session | 2026-08-27 |
| CR0497 | deferred | authoring session | 2026-08-27 |
| CR0499 | deferred | authoring session | 2026-08-27 |
| CR0503 | deferred | authoring session | 2026-08-27 |
| CR0504 | deferred | authoring session | 2026-08-27 |
| CR0507 | deferred | authoring session | 2026-08-27 |
| CR0509 | deferred | authoring session | 2026-08-27 |
| CR0511 | deferred | authoring session | 2026-08-27 |
| CR0523 | deferred | authoring session | 2026-08-27 |
| CR0524 | deferred | authoring session | 2026-08-27 |
| CR0528 | deferred | authoring session | 2026-08-27 |
| CR0529 | deferred | authoring session | 2026-08-27 |
| CR0530 | deferred | authoring session | 2026-08-27 |
| CR0531 | deferred | authoring session | 2026-08-27 |
| CR0533 | deferred | authoring session | 2026-08-27 |
| CR0534 | deferred | authoring session | 2026-08-27 |
| CR0536 | deferred | authoring session | 2026-08-27 |
| CR0539 | deferred | authoring session | 2026-08-27 |
| CR0540 | deferred | authoring session | 2026-08-27 |
| CR0543 | deferred | authoring session | 2026-08-27 |
| CR0544 | deferred | authoring session | 2026-08-27 |
| CR0545 | deferred | authoring session | 2026-08-27 |
| CR0546 | deferred | authoring session | 2026-08-27 |
| CR0551 | deferred | authoring session | 2026-08-27 |
| CR0552 | deferred | authoring session | 2026-08-27 |
| CR0553 | deferred | authoring session | 2026-08-27 |
| CR0554 | deferred | authoring session | 2026-08-27 |
| CR0556 | deferred | authoring session | 2026-08-27 |
| CR0557 | deferred | authoring session | 2026-08-27 |
| CR0535 | deferred | authoring session | 2026-08-27 |
| CR0547 | deferred | authoring session | 2026-08-27 |
| CR0548 | deferred | authoring session | 2026-08-27 |
| CR0550 | deferred | authoring session | 2026-08-27 |
| CR0555 | deferred | authoring session | 2026-08-27 |
| BG0613 | not-stop-ship | authoring session | 2026-08-27 |
| BG0614 | not-stop-ship | authoring session | 2026-08-27 |
| BG0616 | not-stop-ship | authoring session | 2026-08-27 |
| BG0617 | not-stop-ship | authoring session | 2026-08-27 |
| BG0619 | not-stop-ship | authoring session | 2026-08-27 |
| BG0622 | not-stop-ship | authoring session | 2026-08-27 |
| BG0623 | not-stop-ship | authoring session | 2026-08-27 |
| BG0624 | not-stop-ship | authoring session | 2026-08-27 |
| BG0625 | not-stop-ship | authoring session | 2026-08-27 |
| CR0558 | deferred | authoring session | 2026-08-27 |
| CR0559 | deferred | authoring session | 2026-08-27 |
| CR0560 | deferred | authoring session | 2026-08-27 |
| CR0561 | deferred | authoring session | 2026-08-27 |

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
| BG0621 | 2 | 75,774 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0615 | 3 | 113,661 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0618 | 3 | 113,661 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0607 | 3 | 113,661 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 4 unit(s) measured; 4 of 4 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes, by phase - read from the two verdict ledgers:

  test-plan review: NOT IN FORCE for this run - no verdict of that phase covers any of its units, which is not the same as a run that held them and spent nothing

  code review: 5 pass(es) over 4 unit(s), 5 rejected
Unmeasured: BG0621, BG0615, BG0618, BG0607. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- The run was forecast at 16 points and delivered 4 units. The estimate missed the REVIEW cost, not the build cost: four reviews produced four REJECTs and one of them - BG0607's backfill - cost a complete build-and-revert cycle that no point value anticipated.

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
| The backfill cited evidence the fix itself declares invalid - 24 of 53 closures | fixed-in: 1a503fd7, all 19 rows removed and the residue waived instead |
| `repair_state` saw only the standing rejection, so 118 findings were invisible to the gate | fixed-in: 1a503fd7 |
| The release bar could report MET while a High was open, three ways | fixed-in: 6a7162b1 |
| A finding unreadable by both population readers since 2026-07-14 | fixed-in: 6a7162b1, BG0131's heading repaired |
| An empty brief re-arms the whole roll-up defect for any project standing `--brief` down | BG0625 |
| `retitle` refuses precisely the malformed H1 it exists to repair | BG0623 |
| A severity in neither the barred nor the disclosed set is absent from BOTH surfaces | BG0624 |
| The declared Python 3.10 floor is stated six times and guarded nowhere | CR0561 |
| Filing a finding leaves the disclosure page stale, reddening the tree | CR0560 |
| One id-flag concept named three ways across the toolchain | CR0559 |
| The `derived-depth` lane certifies each span against its own seal rather than re-deriving | CR0558 |
| The advisory doc-surface, disclosure and mutation gate lanes | declined: advisory by design, reported at every boundary and not this run's to move |

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

- Critic rejects: 4 of 4 units rejected at first review, all repaired and all repairs recorded COMPLETE. Findings raised during the run: 9 bugs and 4 CRs, none at a barred severity.

## Handoff

- [HO-0064](../handoffs/HO0064-zero-open-high-for-the-first-time-since.md) - 0 remaining item(s): 0 copilot-tail, 0 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
