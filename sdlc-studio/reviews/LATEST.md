
<!-- close-status:begin -->
> **RUN-01KZ79C1 closed stopped.** 6 unit(s) in the batch. **Sign-off is OWED and is the operator's** - the two-role gate holds Done.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **Run of record:** RUN-01KZ5YXM - the charter queue. 26 of 26 points across 6 units, every
> one approved at the third review round and signed off under D0126. Two earlier rounds returned
> REJECT, and the tooling escalated the second to the operator for non-convergence. That
> escalation stands: both rejected versions passed every automated check in this repository
> while being wrong.

## RUN-01KZ9315 - ceremony is proportional to blast radius, and the fixes were already built

**12 of 12 units, 41 of 41 points, all committed with a green full suite at each commit.** The
sprint's thesis was CR0510's second finding rather than its first: the accelerators were built,
tested, and switched off. Three of the twelve units are wiring, not building.

| Unit | Pts | |
| --- | --- | --- |
| US0638 | 3 | the close pre-flight runs the compulsory checklist - the one chain step it never asked about |
| US0639 | 2 | every gate the close runs is recorded; a pre-flight verdict cannot be reused by the chain's wider gate |
| BG0495 | 5 | the velocity row reports what a sprint WROTE beside what was ACCEPTED |
| BG0520 | 2 | the triage session cap is a per-session budget again, not a lifetime one |
| BG0510 | 3 | a plan-review verdict records WHICH artefact it judged - **this unblocks EP0207** |
| BG0525 | 2 | US0629 AC2 restated in decidable terms, before anything was built against it |
| US0640 | 2 | `plan_review.enabled` decouples the gate from the schema version |
| US0641 | 8 | the review tier is DERIVED from the risk band, RECORDED, and READ by coverage |
| US0642 | 5 | a low-band unit gets a bounded brief; the claim-inventory pass runs only at full tier |
| US0643 | 5 | `sprint plan --write` assigns the sign-off panel, making a built path reachable |
| US0644 | 2 | a sign-off records the capacity it was given in, as a field a filter can read |
| US0645 | 2 | `sprint_report.py operator-summary`, derived wholly from the ledgers |

**`route.py`'s own header said "Advisory only - no gate reads a tier". That is now false.**
Measured through the shipped CLI: a low-band unit's brief is 6,146 characters and omits the
claim-inventory pass; a high-band unit's is 8,415 and carries it. Over this run's own batch the
tiering splits 3 light to 9 full; over the whole corpus of 1,171 units it bands medium 821, low
177, high 167, trivial 6.

**CR0532 turned out to be mostly built.** Panel sign-off ships today with three distinct contexts
enforced, the signer read from the run rather than named at signing time, and a
brief-provenance interlock. What was missing was reachability: nothing but a hand-run command
recorded the assignment, so a run that forgot it could not be signed off at all.

### What the discipline bought, and what it cost

**45 named mutants applied, 45 killed** - against five that survived on the previous run. The
difference is that every mutant here was written from the criterion before the code existed.
Four needed a second attempt and each found something real: a dead guard clause in
`conformance.tier_covers` (the same defect this sprint filed against `gate.py:3170` while
planning it), an explicit `--tier light` that would have silently cleared the gate its derived
twin does not, a reader that would have un-signed every historical sign-off when the table
widened, and the panel's brief-provenance interlock, which no fixture reached.

The gates caught four author defects before any reviewer: two units whose verifiers never
entered the shipped entry point, a `close --dry-run` contract broken by the cost recording, a
test that passed in isolation and failed under the suite, and two test classes appended below a
`__main__` guard.

**The cost, stated plainly.** Six full suites at seven minutes each. The gate's own budget lane
reported OVER on every commit - 383s, 445s, 392s against a 380s ceiling already raised once from
120s. That is CR0510's headline evidence worsening while CR0510's first slice was being built.

### What is owed

Nothing in this sprint was live during this sprint. The measurable claim is the NEXT run's
tokens per point against **RETRO0094's 353,810**, recorded in RETRO0095 as the before figure so
the comparison is against a stated baseline rather than a remembered one.

**No independent review covers any unit, and no reviewer-of-record sign-off exists.** Both are
structurally unavailable to the authoring session - the gate working, not failing. US0643 is
what makes the next run able to answer this without waiting.

## CLOSED: RUN-01KZ79C1 - the instruments are honest; the review found what the gates could not

**Called at 6 delivered, 15 descoped, goal verdict PARTIAL.** Four further units shipped their
code and rest at Review, awaiting the reviewer-of-record sign-off the two-role gate reserves for
the operator: US0468, US0480, US0481, US0637.

Terminal: BG0513, BG0507, BG0518, BG0514, BG0515, BG0500. BG0463 delivered narrowed, stays Open.

**The finding that matters is not any defect.** Ten units passed every automated gate - full
suite, `verify_ac`, lane-check, mutation as the author ran it - and two independent seats,
briefed with `critic.py brief`, both REJECTed on 11 blocking findings and produced IDENTICAL
unit-level splits. Five AC-named mutants did not kill their tests, on units committed claiming
they had. The generative defect: each mutant was written after the code, from the code, so it
was the mutant the test was already built to catch. The criterion stated the real mutant in
every case.

**Carried under D0129 (`review.policy: carry-forward`), all filed, none waived:**

| Finding | Filed |
| --- | --- |
| `affects_check` inert at plan time; `batch add` writes before it refuses; JSON path skips it | BG0521 |
| BG0515's fix reproduces BG0515 through the terminal Open-Questions gate | BG0522 |
| Five criteria pinned by verifiers that cannot fail | BG0523 |
| Stale baseline reports clean; US0480 AC2 contradicts AC4 | BG0524 |
| US0629 AC2 is not mechanically decidable | BG0525 |
| Low-severity test debt | CR0511 |

**Two numbers for planning.** Ten units delivered produced eight filed findings - at that ratio
a blocking policy cannot converge, which is why D0129 exists and why CR0510 (ceremony by blast
radius) is the next thing to build. And reviewing a TEST PLAN cost 55k tokens against roughly
400k for the same class of finding after the code shipped - measured here on the first hand-run
use of EP0207's mechanism, which rejected all three rows of US0629's plan.

**Next run leads with EP0207**, descoped intact from this one: build test-plan-before-code, then
turn it on the carried findings so the repairs are held by evidence that can fail.

## Superseded in-flight note: RUN-01KZ79C1 - the instruments are honest, and the baselined debt is paid

**This run is OPEN. 10 of 15 units delivered, 31 of 52 points.** The close-status block above
still describes RUN-01KZ5YXM; it is stamped by `sprint close` and this run has not closed.

Delivered and committed, each with a green full suite at its own commit, `verify_ac` passing
where it applies, and every named mutant applied and killed:

| Unit | Pts | |
| --- | --- | --- |
| BG0513 | 3 | a red suite leg names its failing test and keeps a per-run log (NARROWED - BG0519 carries the residue) |
| BG0507 | 2 | a collapsed suite leaves no reusable green - third door into one fail-open, now pinned as a property |
| BG0518 | 2 | `close_owed`'s headline and its exit code come from one predicate |
| BG0514 | 2 | `queue show` is readable during a run, which is when it is used |
| BG0515 | 3 | the charter queue has an exit - `plan --write --charter` spends it |
| BG0500 | 2 | the runbook guard runs in a lane, not only in the tools suite |
| US0468 | 5 | `help/sprint.md` bound to the shipped parser - **EP0170 has no work left** |
| US0480 | 5 | the Affects/Verify family ratcheted by instance, 371 recorded |
| US0481 | 5 | `sprint plan` validates its batch's units - **EP0173 has no work left** |
| US0637 | 2 | unanswerable duplicate groups derived and named one by one |

**Owed, and why.** `sprint preflight` reports 17 unmet prerequisites. One is cleared: the
installed copy is back in sync (14 files). The other 16 reduce to two facts - no independent
review covers any unit, and no reviewer-of-record sign-off exists. Both are structurally
unavailable to the authoring session, which is the gate working rather than failing.

**Still open in the batch:** US0635, US0636 (8 pts, and all-or-nothing on AC1 - 20 new
discriminating tests, not a tidy-up), BG0406, BG0421, BG0463 (15 pts, each a bundle of ~20
findings behind one id).

**Do not start BG0406 casually.** Its smallest coherent slice is AC4+AC5 and they cannot be
separated: fixing the header re-pin makes the detector active, and an active detector without
AC5 reports 16 TRUE cells as drift and tells the operator to blank them. AC5 means teaching
`children_of` the `RFC:` link spelling - core machinery that `close_owed`, `transition` and
epic derivation all read to decide status across the corpus.

**Carry into any re-forecast of Run B.** A new gate lane costs two roster updates plus npm
parity, not five - the five on US0480 fired because `validate.py` also became a writer and a
new test file appeared. Mutation caught defects in freshly written work three times in this
run that the passing tests could not, twice on the same unit; budget for the second and third
attempt at a test, because the first version is often the one that does not discriminate.

## Landed: RUN-01KZ5YXM - more, smaller runs becomes a command

The goal was that the programme's own re-plan stops being an intention. A charter is now a
first-class artefact (`SC`, `sdlc-studio/charters/`) whose prefix, create status and terminal set
are **derived** from the shared registry rather than restated beside the charter code.

**`sprint next` resolves the head charter against the backlog as it stands at that moment.** The
load-bearing test moves the backlog underneath a charter - one unit created since, one delivered
since - and asserts the second pass returns the new unit and not the delivered one. A cached
batch passes every other assertion in that class and fails only this.

**The queue is inspectable and editable.** `queue show`, `reorder`, `cancel`, `clear`. Cancel
withdraws rather than deletes and keeps its reason, because a cancelled plan is a decision
somebody made and deleting it loses the only trace of why the queue looks as it does. An
unranked charter sorts after every ranked one: absence is not rank zero.

**A charter carries its own goal review**, under `## Seat review` on the charter rather than in
`.local/`. The test proves it travels by deleting `sdlc-studio/.local` entirely and reading the
verdicts back from the file alone. The runner is recorded beside the reviewer and a match is
stated plainly - separation is recorded, never enforced, because a queue is usually planned and
run by one person and refusing that would make it unusable.

**`sprint call` finishes a run rather than abandoning it**: the unstarted remainder is descoped
to the **backlog**, never forward to the next charter, and the close chain then runs.

### What the reviews found, and why it matters

| Round | Finding | Why no gate caught it |
| --- | --- | --- |
| 1 | `call` printed "now close it against the goal" and did not close | AC1's verifier had been repointed to clear the lane-check |
| 2 | `call` could not execute at all - uncaught `AttributeError` on every path | the verifier stubbed the collaborator under test |
| 3 | APPROVE, judged by typing the command in nine argument shapes | - |

Both failures were the same error: **satisfying a gate rather than the criterion.** Both shipped
green through the full suite, `verify_ac`, the lane-check and `gate.py`. Round 2's version passed
every automated check in the repository while being a verb that could not run.

That is the clearest evidence this programme has produced for the independent pass. Eleven gate
refusals across the run were all correct and all useful - but no gate caught either of these,
because in both cases the thing being measured had quietly moved.

### What is owed

| Item | Where |
| --- | --- |
| `queue show` is blind during a run, reusing the materialiser's open-run refusal | `BG0514`, open |
| The queue has no exit - nothing sets `Spent`, so a charter re-materialises forever | `BG0515`, open |
| A scope query cannot express a decomposition; `SC0001`'s two scope fields disagree | `CR0531`, open |
| `run-suite.sh` intermittently red, and the failing test cannot be named | `BG0513`, open |
| The close reports "could not be attributed" where the gate named its lane plainly | `BG0516`, open |
| The close-loop cap stopped a converged loop | `BG0517`, **fixed in this run** |

### The close ceremony refused this run, twice, on its own defects

Run 2's close is worth recording because the ceremony blocked a run that had done everything
asked of it. The attempt series read `1, 1, 1, 1, 0, 0` - converged - and the loop guard stopped
it anyway.

Two defects, both filed by this run and one of them fixed by it:

- **`BG0516`** - the close reported `the refusal could not be attributed` while the gate named
  its failing lane in terms (`review-current`, `LATEST.md` stale). `gate --require-retro` alone
  exits 0; only the `--require-review` form the close passes fails, so the message sends a reader
  to the wrong place. Four rounds were unactionable, and the loop guard - reading exactly those
  four identical rounds - correctly saw no convergence in rounds that were never attempts.
- **`BG0517`, fixed** - `loop_termination` tested the attempt COUNT before it looked at what the
  attempts contained, so a loop reporting zero outstanding was refused at whatever the cap
  happened to be. The cap was raised twice under `D0128` before this was seen for what it is;
  both raises are now reverted, because a guard whose number keeps moving is one nobody trusts.

`EP0176` is Done and `RFC0057` derived resolved - the whole chain from request to epic to
stories is terminal.

### The programme

`D0125` freezes the target at the 66 units open on 2026-08-03. Two runs are closed: 22 points and
26 points. Roughly 183 points remain, and at this rate that is several more runs - which is the
shape the operator chose when they re-planned it as more, smaller runs.

`SC0001` sits at the head of the queue: **the close costs less than it returns**, the complaint
raised three times and still unanswered. `CR0531` must land first or its scope query resolves 15
CRs against an 8-unit appetite.
