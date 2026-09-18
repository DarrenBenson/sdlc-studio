# RETRO-0118: RUN-01M2SPNS: the close splits, and the run ends with one page and one act

> **Date:** 2026-09-18
> **Batch:** US0832 US0833 US0834 US0835 US0836 US0837 US0844 US0845 US0846
> **Goal:** done
> **Delivered:** 9 / 9   **Blocked:** 0

## Delivered

- US0832 - `sprint close` becomes PREPARE and a new `sprint sign` becomes SEAL. The close runs every step that can change a fact, files the report, and leaves the run OPEN; `sign` writes the per-unit rows, the transitions, the cascades and the run's signature, and stops. `--apply-signoff` exits 2 and names `sign` rather than surviving as an alias.
- US0833 - the seal is a transaction: one principal, the signature recording the report's own fingerprint, the principal judged across the WHOLE batch before anything is written, a sealed run refusing the writes that would move its facts, and a re-open that is recorded and keeps the signature it breaks.
- US0834 - PREPARE refuses to produce a report over an unmet terminal gate, an unanswered review or index drift, naming every failure at once and reporting each hold as passed by its own name.
- US0835 - the report JSON of record, every figure carrying a source that resolves, refusing to build a run it cannot report honestly.
- US0836 - the Markdown twin and the HTML rendering, generated from the shipped templates; an absent figure reads NOT MEASURED by name.
- US0837 - the page opens with the sprint goal verbatim and carries the four DORA keys with each mapping stated.
- US0844 - the token meter stamped per session, the total naming the sessions it covers, and NOT MEASURED where it cannot be read.
- US0845 - a report whose figures no longer re-derive renders an INVALIDATED banner, and `status` names it.
- US0846 - the change failure rate computed from this run's own push-triggered CI runs.

## Blocked / deferred

- None. Every unit of the batch reached a cleared terminal gate.

## What went well

- **The split was judged by what each half WRITES**, never by its help text, and that is what made it falsifiable. Every criterion named a production change that must redden a test, and all 33 were applied and killed.
- **Parallel delegation held its shape.** Five subagents ran on file-disjoint surfaces - the composer, the ledger re-registration, the sealed-run guard, the mutant sweep and two review seats - and the one contamination risk that materialised (a suite running while another agent mutated its imports) was caught by re-running clean rather than by reading the first result.
- **The report composer's 19 mutants were executed but never registered**, so the evidence did not exist as far as the tooling was concerned. Asking `mutation.py run --from-plan` per unit found that in one command; nothing in the prose would have.

## What was hard / what stalled

- **Delivery review round 1 rejected six of nine units, and every rejection was real.** Two
  independent seats found defects no test in the batch could see: `stamp_tokens` had shipped
  with a test as its only caller, so the report-time stamp was never taken and every run would
  have reported its cost as zero; the DORA window stayed open while the run was open, so
  committing the report invalidated the report and no operator could have obtained a signable
  page; the CI cache nothing wrote meant every re-derivation was a fresh network call with a
  different answer. The batch was green on 33 criteria and 2,036 tests at the moment those were
  found.
- **The root cause was one question asked too narrowly.** The first repair asked "which figures
  does the SEAL move?" and excluded three. The question that decides whether a page can be
  signed is "which figures does anything but the delivered work move?", and the answer also
  included the live transcript, the open git window and the live forge. A fix that answers a
  smaller question than the defect is a fix that has to be made twice.
- **Two declared mutants SURVIVED their execution**, and both survivals were assertions that
  looked stronger than they were: one searched a whole page for a unit id the close pre-flight
  also prints, and one narrowed on a sentence no fixture ever put two requirements into.

- **Exercising the shipped CLI found a defect no test in the batch could see.** `sign` then `sprint_report.py check` reported INVALIDATED on a legitimate seal: three figures in the digest were facts the seal itself writes. Nine units of tests were green at that moment. The rule that caught it is the repo's own - put every claim through the shipped entry point before asking for review - and it earned its place again.
- **A mutant SURVIVED its first execution** (US0834 AC1). The assertion searched the whole page for a unit id, and the close pre-flight prints the same ids, so a hold that stopped at the first failure still passed. The repair was to assert against the hold's own line.
- **The mutation ledger keyed to file content cost three re-registration rounds.** Registering a row for a unit on a target whose bytes have moved does not merely go stale: a later registration for the SAME unit on that target drops it. Register after the last edit, not before, is not a preference here - it is the only order that works.
- **The coverage gate cannot be cleared by this batch as it stands.** Three units declare `sprint.py` and `tests/test_sprint.py`, and uncommitted lines are attributed to every unit that declares the file, so each is charged with its siblings' additions - 432 uncovered lines for US0832, almost all of them executed by another unit's tests in the same suite. Recorded as the wall it is: BG0706 already holds it.

## Lessons

- A verifier that stands in for a lane protects nothing, and the test that does protect it must be BOUND to a criterion. US0844 AC1's When named PREPARE building the report; its verifier called the library function directly. The lane test was written, observed to fail when the call was removed, and then attached to no criterion - so `verify_ac` never ran it for that criterion and the `stamps-staged` guard would not have refused its deletion. Writing the right test is half the job; binding it is the other half.
- A harness stub lands on the module object it names, which is not always the one the code under test reads from. `test_autosprint`'s stub patched `sys.modules["sprint"]`; a sibling suite loads sprint.py through `spec_from_file_location` and REPLACES that entry, so once both ran the stub landed where nothing looked for it. Invisible module-alone and invisible in isolation - it appears only in discovery order. Patch the function's own `__globals__`.
- A page cannot be signed over facts the signature itself writes. Three figures in this report's digest - each unit's Status, the run's end time and a delivered count taken from statuses - are set BY sealing, so every signed report re-derived to a different fingerprint and read INVALIDATED from the moment it was signed. The digest has to cover what is true when the page is derived: here, that each unit CLEARED ITS TERMINAL GATE. Found by running `sign` then `check` on a throwaway fixture, with 33 criteria and 2,036 tests green.
- A test that searches a whole page passes on somebody else's output. US0834 AC1's mutant survived because the assertion looked for a unit id anywhere in stdout, and the close pre-flight prints the same ids for its own reasons. Assert against the line the code under test wrote, not the transcript it wrote it into.
- A content-keyed evidence ledger has an ordering rule, not a preference: register a unit's mutants AFTER the last edit to their target. A stale row survives another unit's registration but is DROPPED by its own unit's next one, so a partial re-registration silently destroys the evidence it was meant to complete.
- Splitting one command into two halves is a claim about what each half WRITES. Stating it that way made every criterion falsifiable by a production change; stating it as "close prepares and sign seals" would have been unfalsifiable prose, and the gate that catches the difference is the mutant, not the review.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- A mechanism that reaches no caller is inert, however well it is tested - exercise every claim through the shipped entry point before asking for review.
- A criterion's words routinely outrun its fixture: ask what could be deleted from the production code with the test still green.
- Never repair the gate that is refusing your own run. Record the wall and leave the run open.
- Fixture-green is not target-green: run the shipped lane against this repository, not only against a temporary directory.
- Register mutation evidence last, after the final edit to the file it is evidence about.

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
| BG0706 | not-stop-ship | delivery, RUN-01M2SPNS | 2026-09-18 |
| BG0713 | not-stop-ship | delivery, RUN-01M2SPNS | 2026-09-18 |

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
(`accuracy --tokens-from-harness`, run by `sprint close` as it PREPARES the run) and the velocity row
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
| US0832 | 8 | 404,144 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0833 | 5 | 252,590 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0834 | 3 | 151,554 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0835 | 5 | 252,590 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0836 | 5 | 252,590 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0837 | 3 | 151,554 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0844 | 3 | 151,554 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0845 | 3 | 151,554 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0846 | 2 | 101,036 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 9 unit(s) measured; 9 of 9 forecast at plan time.**

Review passes, by phase - read from the two verdict ledgers:

  test-plan review: 9 pass(es) over 9 unit(s), 3 rejected

  code review: 9 pass(es) over 9 unit(s), 6 rejected

  ratio: 1.00 code-review pass(es) per test-plan pass - the claim EP0207 is judged on, as a number
Unmeasured: US0832, US0833, US0834, US0835, US0836, US0837, US0844, US0845, US0846. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
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
| Plan review round 1: US0844 AC1's verifier was a library call while its When named the PREPARE lane, and the lane test that existed was bound to no criterion | fixed-in: US0844 |
| Plan review round 1: US0832 AC2's Then both permitted and forbade the velocity row, and the test allowlisted what the criterion forbade | fixed-in: US0832 |
| Plan review round 1: US0832 AC4 stated a clause false of its own Given (`VELOCITY.md` holds one row, in a fixture that never creates it) | fixed-in: US0832 |
| Plan review round 1: US0834 AC3's defining property - refuse rather than defer - was never exercised, because no test passed `--file-and-close` | fixed-in: US0834 |
| A test harness stub landed on the wrong module object once a sibling suite had replaced `sys.modules["sprint"]` - invisible module-alone, visible only in discovery order | fixed-in: US0832 |
| Five repo guards caught conventions the batch had broken: raw git calls outside the confined helper, a writer with no confinement case, a `--format` flag that did not conform to the family grammar, and two close harnesses whose fixtures the new holds refused | fixed-in: US0832 US0834 US0835 |
| Delivery review round 1: the report-time token stamp reached no caller, so every run would have reported a cost of zero | fixed-in: US0844 |
| Delivery review round 1: the DORA window stayed open while the run was open, so committing the report invalidated the report | fixed-in: US0845 |
| Delivery review round 1: the CI cache was never written, so every re-derivation was a fresh network call with a different answer | fixed-in: US0845 |
| Delivery review round 1: one open stamp reported a total of 0 rather than NOT MEASURED | fixed-in: US0844 |
| Delivery review round 1: `transition requirements` raised an uncaught refusal for every unit of a sealed run | fixed-in: US0833 |
| Delivery review round 1: the drift hold named the artefact type rather than a path, and its test monkeypatched the predicate | fixed-in: US0834 |
| Delivery review round 1: the gate carve-out's narrowing was mutation-free, and re-parsed a sentence instead of reading the blocks | fixed-in: US0834 |
| Delivery review round 1: the source check accepted any non-empty string, and the test kept a stale second copy of the figure enumerator | fixed-in: US0835 |
| Delivery review round 1: PREPARE's last line was the sign-off brief, a second account closing with the per-unit signing route | fixed-in: US0832 |
| Signing a report invalidated it - three figures in the digest were facts the seal itself writes | fixed-in: US0835 |
| A declared mutant survived its first execution: the assertion searched the whole page rather than the hold's own line | fixed-in: US0834 |
| The composer's 19 mutants were executed but never registered, so the evidence did not exist as far as the tooling was concerned | fixed-in: US0835 US0836 US0837 US0844 US0845 US0846 |
| The per-unit coverage gate charges a unit for its batch siblings' added lines in a shared file | BG0706 |
| The new `sign` verb was a ceremony verb no checklist row named, so the cycle-drift guard failed | fixed-in: US0832 |

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

- [HO-0072](../handoffs/HO0072-a-run-ends-with-one-page-it-can.md) - 9 remaining item(s): 0 copilot-tail, 9 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
