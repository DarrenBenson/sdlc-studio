# RETRO-0081: RUN-01KYKVZM: the in-lane quality sprint - the lane that graded its own homework

> **Date:** 2026-07-28
> **Batch:** RUN-01KYKVZM - 31 units, 102 points: US0508, US0509, US0510, US0511, US0512, US0513, US0514, US0515, US0516, US0517, US0518, US0519, US0520, US0521, US0522, US0523, US0524, US0525, US0526, US0527, US0528, US0529, US0530, BG0313, BG0319, BG0331, BG0336, BG0341, BG0351, BG0352, BG0353
> **Goal:** A defect is caught by the lane that made it, the loop measures what it costs, and a lesson carried forward is read by the work that would repeat it
> **Delivered:** 31 / 31   **Blocked:** 0

## Goal verdict, by clause

The goal held three clauses and landed differently on each, which no field in the close can
currently express - filed as CR0469, the operator's ask for a stakeholder-panel goal verdict.
Recorded here by hand in the meantime:

| Clause | Verdict | Evidence |
| --- | --- | --- |
| A defect is caught by the lane that made it | **Partially achieved** | All 31 units ran their own acceptance criteria before returning and two blocked themselves. But BG0370 leaves a hole through the terminal criteria floor on the tool's own default path, verified live on a fresh project. |
| The loop measures what it costs | **Achieved** | The overhead ratio reports its bound, names each unmeasured component and states that the true ratio is higher. Two narrower defects remain (BG0366, BG0372), neither falsifying the clause. |
| A lesson carried forward is read by the work that would repeat it | **Achieved** | The carried set reached the plan and every delivery lane brief this sprint. BG0365 is fragility in how it is stored, not a failure to read it. |

## Delivered

The batch, named in full so the close can attribute its cost: US0508, US0509, US0510, US0511,
US0512, US0513, US0514, US0515, US0516, US0517, US0518, US0519, US0520, US0521, US0522, US0523,
US0524, US0525, US0526, US0527, US0528, US0529, US0530, BG0313, BG0319, BG0331, BG0336, BG0341,
BG0351, BG0352, BG0353.

- **EP0178 US0508-US0517** - the lane stops being where defects are made and review where they are
  found. A lane refuses to start on a unit with no readable acceptance criteria, runs its unit's own
  criteria before returning, returns the proof the test strategy assigned it, and carries those
  obligations in the dispatch prompt so they do not depend on who wrote the brief. A unit adding a
  mechanism must name the caller that consumes it, or say explicitly there is none yet and name the
  follow-up. A bug reaching terminal with no criteria is refused, with the existing corpus baselined.
- **EP0179 US0518-US0524** - the learning loop closes. The retro curates a fixed-size carried set, a
  lesson earns a place only by displacing one, the sprint reads the set at plan and in every lane
  brief, a lesson violated again after being carried is reported at close naming the unit, and a
  repeatedly violated lesson can propose a change request. The close reports delivery against
  overhead as a ratio, with an unmeasured component reported as unmeasured rather than as zero.
- **EP0180 US0525-US0530** - waivers are read and reported by the conformance lane, a waiver naming
  no reason or an unknown rule is refused at record time, validate can be pointed at one artefact,
  a Draft story declaring a file it will create is no longer warned as unresolvable, and `init`
  derives the artefact tree from the shipped type list.
- **8 bugs** - BG0351 (the constitution lane at 81% of a gate documented as one second), BG0313 (a
  verifier evaluating neither the gate nor the transition it claimed), BG0319 (the RFC index's false
  Spawned-CRs column), BG0331 and BG0341 (two more enumerated-list exemptions), BG0336 (a
  direction-blind carve-out), BG0352 (the two suites pytest cannot collect together) and BG0353 (an
  ISO-8601 offset stamp that voided a whole sprint report).

## Blocked / deferred

- None blocked. Two lanes correctly blocked themselves mid-flight on their own acceptance criteria
  and were re-dispatched - the sprint goal working, not a failure.

## What went well

- **The sprint applied its own rules by hand before it had built them.** All 31 units ran their own
  criteria before returning, because the operator's instruction could not wait for EP0178 to ship.
  Two units caught themselves. First sprint in this series where a lane refused its own work.
- **The review reproduced rather than believed.** The most serious finding was not read off the diff:
  a reviewer built a story with an external provenance stamp and a shell verifier in a temp
  repository and watched the lane execute what `verify_ac` refuses.
- **The friction instruction produced eight findings without stopping delivery** (BG0360-BG0364,
  CR0465-CR0467), all raised by lanes as they hit them, none absorbed silently.

## What was hard / what stalled

- **The sprint that built name-your-caller shipped its own verb with no caller.** `sprint lane
  brief|return` appeared in no help file, reference or prompt template, and the sprint's own check
  reported five of its six units caller-unnamed. Carried lesson 1, violated by the units enforcing it.
- **A trust boundary was open.** `lane_verify` re-derived the shell rule instead of importing it and
  was more permissive than the definition it mirrored, so a unit carrying externally ingested content
  could execute a shell verifier through the lane path. Reproduced live; repaired with one shared
  predicate and a differential test.
- **One question, two parsers.** `lane_contract` decided with one parser and built with another, so
  475 live units would have dispatched with an empty contract.
- **A guard that resolved nonsense.** `caller_resolves` built its vocabulary from an unfiltered walk,
  so `unknown` and `nothing at all` resolved while a real tracked path did not.
- **The author's repair reported a number it had not measured, and the number was wrong.** The repair
  claimed caller-unnamed went from five to zero. An independent re-review of the repair returned
  REJECT and showed it is seventeen of twenty-three, including one of the six lane units the repair
  was about. The false figure reached this retro and two commit messages before it was checked. It
  was produced by a command-line invocation whose repeated flag silently overwrote rather than
  accumulated - the library call is authoritative and says otherwise. Two of the four repairs were
  confirmed closed with mutations killed; one is correct but pinned by no test at all; this one was
  over-claimed.
- **The author graded ten defects by feel and got two wrong in opposite directions.** BG0368 was
  filed Medium and is Low - `artifact.py` creates a missing index on demand, so no user is blocked.
  BG0370 was filed Medium and is High - it lets a bug reach terminal with zero criteria by default.
  Both corrected only because they were tested rather than asserted.

## Lessons

- **One truth held in two places diverges, and the looser copy is the one that runs.** Two of the
  four serious findings were this shape: `lane_verify` re-derived the shell and provenance rule
  rather than importing it, and `lane_contract` used one parser to decide and another to build. Each
  copy was individually tested and individually correct, which is exactly why a green suite said
  nothing - the defect lives in the gap, and only a differential test looks there. The
  enumerated-list failures this sprint (BG0331, BG0336, BG0341, and the incomplete repairs BG0373
  and BG0374) are the same defect wearing a different hat: a hand-maintained list is a second copy
  of a truth some derivation already holds. Import the rule, derive the list, or write the test that
  asserts the two agree.
- **A guard that cannot fail is not evidence, and its greenness is the tell.** `caller_resolves`
  approved `unknown` and `nothing at all` and no test noticed, because no test ever asked it to
  reject anything. Before trusting a check, feed it something that must fail; a check with no
  recorded refusal has never been shown to be a check.
- **Enforcing a rule is not obeying it.** The batch that built the criteria floor put four bugs into
  Fixed with no criteria, and the batch that built name-your-caller shipped a verb reachable from
  nothing. A rule the machinery does not yet enforce is not in force for the people building the
  machinery either - which is precisely when it fails.
- **In-lane verification changed what review found, not how much.** 20 majors on 33 units last
  sprint, 17 on 31 this sprint: the rate barely moved. The composition changed completely - last
  sprint roughly 17 of 20 were within-unit and mechanically catchable, this sprint essentially none
  were. Thirteen of seventeen were seams between units, which a lane cannot reach because a lane
  reads one unit. Filed as CR0468.
- **Verifying the premise beat trusting it three times in one afternoon**, twice against findings
  this author had filed hours earlier. BG0368 and BG0370 were mis-graded in opposite directions, and
  BG0366's summary overstated its own defect - `_overhead_ratio` labels its bound and names what it
  excludes, which the finding claimed it did not.

## Carried lessons

The set is fixed at five and the displacement rule binds from this retro.

- **One truth held in two places diverges, and the looser copy is the one that runs.** PROMOTED this
  retro: it produced a live trust-boundary breach and would have dispatched 475 units with an empty
  contract, both invisible to a green suite. Import the rule, derive the list, or write the test
  that asserts the two copies agree.
- **A mechanism that reaches no caller is inert.** Re-carried, and violated again this sprint by the
  very units written to enforce it: `sprint lane brief|return` shipped documented nowhere and called
  by nothing.
- **An absence is not an answer.** Re-carried, and violated again: a bug reaches a terminal status
  through an auto-written stated absence carrying zero criteria (BG0370).
- **A repair breaks its neighbours, and a rename is cross-unit coupling.** Re-carried, and violated
  again for the third consecutive sprint - renamed test classes left criteria pointing at nothing.
- **Verify the premise before building on it.** Re-carried on evidence rather than habit. It was a
  candidate for displacement at the start of this close, on the argument that a lane running its own
  criteria makes it mechanical. That argument was falsified within the hour: the lesson earned its
  place three times during the close itself, twice against findings this author had filed hours
  earlier. The mechanisation covers a unit's own criteria and reaches nothing about a claim written
  in a review finding.

**Displaced:** *an enumerated list silently exempts what it forgot* - **merged into the promoted
lesson rather than retired.** A hand-maintained list is a second copy of a truth a derivation
already holds, so the enumerated-list failure is a special case of divergence. Nothing is lost:
BG0331, BG0336, BG0341, BG0373 and BG0374 remain covered by the generalisation, which additionally
reaches the two-parser and re-derived-rule cases the narrower wording could not.

## Estimate vs actual

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US0508 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0509 | 5 | 298,155 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0510 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0511 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0512 | 5 | 298,155 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0513 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0514 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0515 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0516 | 5 | 298,155 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0517 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0518 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0519 | 5 | 298,155 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0520 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0521 | 5 | 298,155 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0522 | 5 | 298,155 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0523 | 5 | 298,155 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0524 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0525 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0526 | 2 | 119,262 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0527 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0528 | 2 | 119,262 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0529 | 2 | 119,262 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0530 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0313 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0319 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0331 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0336 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0341 | 2 | 119,262 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0351 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0352 | 3 | 178,893 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0353 | 2 | 119,262 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 31 unit(s) measured; 31 of 31 forecast at plan time.**

**Sprint tokens/point: 26,411** (2,693,917 tokens over 102 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity: 19.4 points/elapsed-hour** (102 points over 5.258h, run-state, ceremony included). This is the planning number - points per SESSION within the observed single-session envelope; it is NOT a linear per-point rate to extrapolate to a 1-point or 100-point sprint, and it is descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).
Unmeasured: US0508, US0509, US0510, US0511, US0512, US0513, US0514, US0515, US0516, US0517, US0518, US0519, US0520, US0521, US0522, US0523, US0524, US0525, US0526, US0527, US0528, US0529, US0530, BG0313, BG0319, BG0331, BG0336, BG0341, BG0351, BG0352, BG0353. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- The batch was sized at 102 points against an operator estimate of five hours, on the previous
  sprint's measured seven hours for 107. Delivery ran roughly to plan; the overrun is in review and
  repair again. The instrument built this sprint to price that split could not report on the sprint
  that built it until this retro named its units, which is itself the finding: the attribution is
  correct and the paperwork feeds it, so a report run before the retro is written reads UNMEASURED
  rather than wrong. The honest reading is that in-lane verification changed what review found
  without shortening it, and the next sprint is the first that can measure the claim.

## Actions raised

| Finding | Disposition |
| --- | --- |
| `lane_verify` re-derived the shell and provenance rule and executed a verifier `verify_ac` refuses, on a unit carrying externally ingested content | fixed-in: 343da768 - one shared `shell_allowed_for` with a differential test |
| `lane_contract` decided with one parser and built with another, so 475 units would have dispatched with an empty contract | fixed-in: 343da768 |
| `caller_resolves` resolved `unknown` and `nothing at all` while a real tracked path failed | fixed-in: 343da768 |
| `sprint lane brief\|return` was named in no documentation and called by nothing | PARTLY fixed-in: 343da768 - documented in three places, and the documentation is accurate (an independent re-reviewer ran every documented invocation verbatim). The claim that caller-unnamed reached 0 was FALSE and is withdrawn: 17 of 23 stories still report it, including US0513 among the six lane units. BG0377 |
| The lane_contract refusal governing 475 units is asserted by no test - neutering it leaves all 4,860 tests green, violating US0505 from this same batch | BG0375 |
| Five stories' caller criteria are verified by a class that never reads the story, so deleting a Caller declaration leaves the criterion green | BG0376 |
| Four bugs reached Fixed with no acceptance criteria, in the batch that built the rule refusing that | fixed-in: 343da768 |
| A repair renamed test classes and left criteria pointing at nothing, third consecutive sprint | BG0352, filed and fixed in this batch |
| Decomposition creates seams between units and nothing owns them - 13 of 17 majors were seam defects, including four directly contradicting pairs in one batch | CR0468 |
| No sprint-goal verdict exists, so whether a defect can be left is decided informally by the author | CR0469, operator-raised |
| A bug reaches terminal with zero criteria via the auto-written stated absence | BG0370 - **P1, addressed before close** |
| The carried set has three representations and the reader may resolve a different one from the writer | BG0365 |
| `delivery_s` carries no marker that it contains unattributed time, and the remainder is not its own term | BG0366, corrected down to P2 after reading the code |
| The AC-less baseline is not one-way, so a unit can be added to it and self-exempt | BG0367 |
| `init`'s derived tree creates a directory without its index | BG0368, corrected down to P3 - the index is created on demand, no user is blocked |
| The conformance waiver report is blanked when a diff contains no stories | BG0369 |
| The repeated-lesson report rests on a single unpinned call | BG0371 |
| The overhead ratio never reaches the velocity record | BG0372 |
| BG0336's carve-out repair remains story-shaped | BG0373 |
| BG0341's markdownlint widening is an added path rather than a derivation | BG0374 |
| Eight friction findings raised by lanes during delivery | BG0360-BG0364, CR0465-CR0467 |
| The review found 17 majors despite in-lane verification | declined as a defect: the composition changed as intended, and the cause is CR0468 rather than a failure of the in-lane work |

<!-- file one with: scripts/file_finding.py · check with: scripts/retro.py dispose --id RETROxxxx -->

## Close loop (gated)

`gate --require-retro RETRO0081` fails until all four are true:

- [ ] this retro exists AND passes its content check (`retro.py validate --id RETRO0081`)
- [ ] its lessons are in the project store (`retro.py extract --id RETRO0081`)
- [ ] open lessons re-validated (`lessons revalidate`)
- [ ] `retros/LESSONS-SUMMARY.md` regenerated (`lessons summary`)

## Metrics

- Units 31/31, 102 points, 0 blocked · Delivery ~08:00-11:30, review and repair ~11:30-15:00 against
  a 14:00 target · Critic rejects: 1 REJECT on the delivery (17 majors), 4 repaired in-sprint, 1
  addressed at close as P1, 9 carried with recorded priorities

## Deferred at close

Closed with known outstanding work (RUN-01KYKVZM): the operator chose file-and-close over another fix cycle. Nothing here was waived - each blocker is a filed artefact:

- CR-0472: [sign-off] US0508: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0473: [sign-off] US0509: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0474: [sign-off] US0510: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0475: [sign-off] US0511: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0476: [sign-off] US0512: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0477: [sign-off] US0513: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0478: [sign-off] US0514: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0479: [sign-off] US0515: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0480: [sign-off] US0516: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0481: [sign-off] US0517: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0482: [sign-off] US0518: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0483: [sign-off] US0519: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0484: [sign-off] US0520: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0485: [sign-off] US0521: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0486: [sign-off] US0522: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0487: [sign-off] US0523: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0488: [sign-off] US0524: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0489: [sign-off] US0525: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0490: [sign-off] US0526: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0491: [sign-off] US0527: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0492: [sign-off] US0528: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0493: [sign-off] US0529: no critic verdict and no sprint-level review covering it (deferred, not waived)
- CR-0494: [sign-off] US0530: no critic verdict and no sprint-level review covering it (deferred, not waived)

## Handoff

- [HO-0035](../handoffs/HO0035-a-defect-is-caught-by-the-lane-that.md) - 23 remaining item(s): 0 copilot-tail, 23 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.

