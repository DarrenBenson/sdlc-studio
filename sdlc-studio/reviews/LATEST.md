
<!-- close-status:begin -->
> **RUN-01KZF9AF closed goal-reached.** 8 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **Run of record:** RUN-01KZ5YXM - the charter queue. 26 of 26 points across 6 units, every
> one approved at the third review round and signed off under D0126. Two earlier rounds returned
> REJECT, and the tooling escalated the second to the operator for non-convergence. That
> escalation stands: both rejected versions passed every automated check in this repository
> while being wrong.

## SUPERSEDED by D0133 - the v5 programme is six queued charters, and the blocking number was wrong

**Read this before the section below.** D0132's three-bug gate is superseded. A release-readiness
sweep on 2026-08-09 ran the two paths a consumer actually takes - greenfield `init` to a first
sprint plan, and a v4-era project through `migrate` to `gate` - against throwaway fixtures, and
found three defects that no backlog, test or lane could see. All three are consumer-facing, and
none of D0132's three is:

- **BG0558** - a greenfield project cannot plan its first sprint. Every `Affects` path in a new
  project is legitimately unresolvable, because the story describes code not yet written, and the
  blocking grooming lane calls that a fictional Affects. `sprint.breakdown` defaults to `enforce`
  and `init run` writes no override, so a project created by the shipped initialiser is in the
  refusing state from the moment it exists. The message says `lacks: Affects` about a story that
  declares one. The advisory lane one call away holds the opposite rule and gets it right.
- **BG0559** - `_doc_surface`, new in v5 at 4e0e4a0f, raises `ModuleNotFoundError: No module
  named 'surface'` in every consuming project, reporting count 1 forever. Its sibling
  `doc-coverage` returns `N/A (not the skill repo)` on the same fixture in the same run.
- **BG0560** - README routes every existing user to `docs/existing-users.md`, which is the **v4**
  page, and calls v5 a drop-in. Measured: `gate.py` FAILs on conformance, reconcile and
  index-derived immediately after a clean `migrate --apply`. RFC0040 required this guide before
  the post-freeze release and it was written for v4 and never revised.

**BG0535's number was wrong.** `gate.py --release` re-run on 167e7e38: **53 red of 1876, not 106
of 1824**, in 1663s. And they are stale selectors rather than broken features - `audit_check.py`
and `test_review_generate.py` do not exist; four more name test methods renamed out of files that
do. So the repair is mechanical, and CR0508's write-time guard is the part that has to land with
it. The bug carries the re-measurement; the title was left standing, because a figure that moved
by half is the finding.

**The operator's bar, D0133:** zero open bugs at tag, every red criterion repaired, no KNOWN
ISSUES section, and a project's first run reports the plan-review requirement rather than
refusing it (CR0541). The programme is queued as SC0002 to SC0007 - first-run and upgrade paths,
then the lying gates, then grandfathering, then a grooming run for the 20 units that carry no
criteria, then the bug burn-down, then the cut. SC0001 is deferred to rank 7.

**The transferable result is not any of the three bugs.** It is that twenty minutes of running the
shipped commands against a fixture found what a 6354-test suite, twenty gate lanes and a 253-point
backlog did not. SC0002's load-bearing unit is the rehearsal lane that makes that pass automatic,
and it must fail on the tree as it stands before any of the three repairs land.

## Superseded: v5.0.0 is BLOCKED on three bugs, not frozen - D0132, 2026-08-09

D0130's blanket hold is lifted and superseded. The tag is back in scope and gated on three
named defects rather than on an instruction with no end condition. Clearing these clears v5:

- **BG0535** - `gate.py --release` reports 106 red acceptance criteria of 1824, every one on a
  story already at Done, while `README.md` tells readers acceptance criteria are executable and
  get run. True of the mechanism, false of the corpus. This is the class the release gate exists
  to catch. **The 106 is the figure recorded when the bug was filed and has NOT been
  re-measured** - the lane takes 1667s against a 600s budget and has completed once in its
  history. Re-run it before ruling on it; trusting a remembered number is what put a false
  disclosure figure in RUN-01KZF9AF's own plan.
- **BG0542** - `sprint plan` under `sprint.affects_check: block` prints REFUSED, exits 0, and
  writes the offending unit into the batch. A consuming project's gate announcing a refusal it
  does not perform is worse than the honest advisory it replaced.
- **BG0536** - a test fixture takes a caller-supplied root; one call passed `.` and wrote into
  the real repository, destroying 23 mutation registrations that `.local/` being gitignored made
  unrecoverable.

The other ten open High bugs are internal-consistency defects - inert detectors, verifiers that
cannot fail on what they claim. Real, and not reasons to hold a release.

RETRO0099 ruled 47 findings `not-stop-ship` on the basis that D0130 meant nothing reached a
consumer. That basis is gone; the retro carries a superseding note rather than a quiet rewrite,
and the three above are re-ruled there.

## RUN-01KZF9AF - the skill documents what the tooling ships, and the coverage number cannot be self-satisfied

**8 of 8 units, 31 points, goal ACHIEVED under panel sign-off.** 49 of 211 verbs appeared in no
hand-written doc as something a reader could type. The obvious fix - generate a page listing
every verb - would have driven a coverage query to 100% with nothing improved, which this repo
has already filed once as BG0457: a document compared against a projection of itself. So the
corpus the number is measured against EXCLUDES every generated target and every fenced generated
region, and the criterion asserts it in both directions: 132 of 257 with the exclusions on, 257
of 257 with both off.

| Unit | Pts | |
| --- | --- | --- |
| US0652 | 5 | one enumeration of the surface, NAMING what it cannot read rather than skipping it |
| US0653 | 5 | the verb catalogue is generated between markers; an unmarked file is refused |
| US0654 | 5 | the gap is measured against hand-written docs only - the load-bearing criterion |
| US0655 | 3 | the number reaches the gate lane, the lint aggregate and the close report |
| US0656 | 3 | the reference index is walked from the filesystem, each row reading its own file |
| US0657 | 3 | budgets record what shipped and report the files inside the tolerance |
| US0658 | 5 | 26 generated Reading Guides with LINE SPANS, replacing the 3 hand-written ones |
| US0659 | 2 | SKILL.md carries its own checklist's sections; the nesting depth is measured |

**Read this before the next review round.** The delivery review returned 4 APPROVE and 4 REJECT,
and three of the four rejections were one failure: **a test asserting a weaker claim than the
criterion above it.** US0658 asserted a guide was PRESENT where the criterion said REPLACES -
three references shipped carrying two guides, the generated table listing its rival as a section
row. US0656's description test ran on a two-file synthetic fixture where the criterion said the
corpus - seven real rows shipped markup as prose. US0652's delegation test compared against an
empty list, which an empty sweep also satisfies. All three were green from the day they were
written, so no run could have surfaced them. Only reading each test back against its own
criterion did.

**The second thing worth carrying: drive the claim through the COMMAND.** `verify_ac lane-check`
reported five of these eight units as verified only in-process. Paying that advisory - adding one
CLI-driving verifier per unit - found two defects a 6354-test green suite held: `docgen.py
references` and `surface` threaded `--root` to the file they WROTE but not to the content they
READ, so the flag chose a target and the real installed tree supplied its contents; and
`nesting_depth` had zero non-test callers, the same shape RUN-01KZEF9M spent itself repairing.
`test_cli_grammar.py` checks a `--root`'s grammar exhaustively and its EFFECT not at all.

Filed and open: **CR0539** (lane-check names 181 units corpus-wide and blocks none, so the rule
AGENTS.md states has a checker nobody acts on - ratchet it rather than block on 181) and
**BG0556** (no guard catches a decorative `--root`). Both are `not-stop-ship`; D0130 still holds
the tag, so nothing here reaches a consumer until a release is cut, and that judgement is owed
again then.

## RUN-01KZEF9M - the doctrine's claim and the command's behaviour are the same claim now

**8 of 8 units, 42 points, goal ACHIEVED under panel sign-off.** The doctrine told consuming
projects that `transition.py` refuses a repair whose changed surface carries no surviving-mutant
evidence. `repair_mutation_gate` had zero non-test callers; `mutants_over_changed_lines` had none
anywhere. The wave that built them verified every criterion through the library function each
one's own When named the command for, so nothing in it could see the missing lane.

| Unit | Pts | |
| --- | --- | --- |
| BG0541 | 8 | the lane is wired, OUTSIDE the unrelated cutoff the repair branch sat in |
| US0660 | 8 | a survivor becomes a severity-rated bug and the transition proceeds - the operator's mode |
| US0661 | 8 | a MEASURED run is evidence the gate can read, not just a hand-typed claim |
| US0564 | 5 | changed-line scope, re-verified through the command its criteria always named |
| US0565 | 5 | the survivor gate, likewise, with a `line` the shipped verb can now write |
| US0566 | 3 | repair scope and the exemption, re-derived from the diff rather than the declaration |
| US0573 | 3 | the uncommitted-surface reason - **found FALSE at the entry point while re-verifying it** |
| US0567 | 2 | rule 21 enumerates its mechanisms, and a guard checks each is REACHED |

**`review.mutation_evidence` is the operator's decision, and `report` is the default.** A survivor
becomes a severity-rated bug and the close proceeds; `block` restores the hard bar; `off` stands
the lane down. Two things ignore the setting, and both are stated in the doctrine: a claimed
exemption re-derived and found FALSE refuses under `report` too, because that is a written claim
shown untrue rather than a bar being applied; and a ledger recording one mutant as both killed and
survived refuses even under `off`, because `off` says evidence must not hold your transitions, not
that the instrument may lie.

### The gate could not be satisfied by measurement at all

`append_ledger` reduced a measured run to a counter block and discarded its per-mutant records,
while `register` - the hand-typed claim - wrote the list both gates select on. **The strongest
evidence in the system read as no evidence and the weakest read as proof**, which is the exact
inverse of what the doctrine claimed. That is now fixed, and `ledger_entries` exists at all: it
was called behind a `hasattr` that was False for its whole life.

### What the reviews cost, and what they bought

Three plan-review rounds (24 findings, 21 closed before a line existed) and three delivery rounds
plus a closing pass. Ten REJECTs in all, every blocking finding established by EXECUTION.

**Twice, a repair MOVED its defect rather than closing it.** The terminality rule learned If, Try,
With and `while True` in one round and was still wrong about `for`/`else`, `match`, `async with`,
an inner loop's `break`, and a `break` that jumps past the `else`. Widening a rule is not the same
as making it right, and the test for the difference is a fixture on the OTHER side.

**One proposed repair was implemented and REVERTED.** Round three asked that a corrected mutation
verdict supersede the earlier row. Building it reddened the test that pins the opposite rule
deliberately: a genuine correction and an author registering their way out of a survivor are
byte-identical to the tool. BG0553 carries it with an answer that does not open that door.

### The sprint's own thesis caught the sprint

61 mutants had been registered across the eight units for edits that were never applied - the
ledger held claims, which is the exact state this work exists to stop counting as proof. Clearing
all 61 and applying them for real took under ten minutes and **turned up two survivors the
paperwork had recorded as kills**. LL0053 records it: a registered mutant is a claim; clear the
ledger and apply them before believing the count. 65 mutants were measured in the end.

### Filed and NOT fixed, each ruled

BG0545 to BG0554. Two carry `accepted-risk` because they limit something this increment claims:
**BG0551** - `repair_mutation_gate` still derives its surface from the artefact's own `Affects`,
so a unit declaring a surface it did not change is not held to one, and rule 21 now names that gap
rather than promising a bar it does not fully have. **BG0553** - a mistyped verdict cannot be
corrected, and the contradiction check turns that from a wrong number into a refusal.

**BG0552 is the one to read next**: a registered mutant names the author's prose and a measured one
names the generator's fault class, so the cross-provenance contradiction - a hand-typed claim caught
disagreeing with a measurement, the case this whole rule turns on - is undetectable. US0661 AC4 was
narrowed to what the ledger can decide rather than left asserting a premise no fixture could meet.

## RUN-01KZ9315 - ceremony is proportional to blast radius, and the fixes were already built

**12 of 12 units, 41 of 41 points, delivered with a green full suite at each commit and reviewed
by two independent seats over two rounds.** The sprint's thesis was CR0510's second finding
rather than its first: the accelerators were already built, tested, and switched off.

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
claim-inventory pass; a high-band unit's is 8,415 and carries it. Over the whole corpus of 1,171
units the bands split medium 821, low 177, high 167, trivial 6 - so the tiering buys a bounded
brief on about 16% of units, and every unit of the NEXT sprint's own batch bands medium. That
number is the case for CR0510's next slice, and it is stated here rather than discovered later.

**Panel sign-off is in force.** Adversarial seats qa and engineering, signing seat product, under
D0130. The panel was assigned by `persona_resolve.py panel`, read from the run rather than named
at signing time, and the product seat signed work it neither authored nor adversarially reviewed.

### What the two review rounds actually found

Round 1 (both seats, pre-repair): 71 mutants, 12 survivors, 6 blocking findings. Round 2 (both
seats, over the repaired tree): 103 further mutants, and **the sharpest finding of the sprint was
a regression created BY a repair.**

That repair replaced four open-coded `"UNMEASURED"` literals with one constant and rewrote the
assertions to compare against it. Both sides of every assertion then moved together: mutating the
constant to `"0"` survived all 134 tests while the shipped CLI printed `Cost: 0 tokens over 8
points` - verbatim the mutant the criterion names. The literal assertions the repair deleted were
the only thing pinning the word. A self-referential assertion cannot fail, however many there are.

The same round found the first repair of BG0495 had moved its defect rather than removed it: the
`seconds` rule was inverted from an allow-list to an exclusion, with a comment citing LL0043
written directly above three surviving enumerations of the same rule. A preflight-only ledger
rendered `0 full run(s), 0 selected - 623s of test time`. The counts now derive from the ledger.

Twice, a repair relocated its own defect one clause over. That is the transferable finding, and
it is why `critic.py brief --rejoinder` exists.

Also found and fixed: a completeness claim true of the dict and false of the page (the renderer
hand-enumerated four field names, so a fifth component was derived correctly and never printed);
a deferred import justified by an import cycle that does not exist; and two units whose declared
`Affects` omitted the files their own repairs landed in, so a seat honouring the bounded scope
could not see the work it was reviewing.

Reported and NOT fixed, each proven pre-existing at the base ref by execution: the reuse
annotation in the execution sentence is unpinned in both directions, the sum-to-runs invariant is
reuse-blind on its fixture, the overhead `exact` bound has no positive control, `critic.py:1236`'s
role normalisation is unpinned since 307ce91d, and `retro.py:2255`'s "absent rather than a repeat"
rule for the Written cell can be deleted with the suite green.

**The panel split on BG0495** - engineering rejected, qa approved - and the tooling escalated it
to the operator rather than resolving it by majority. The disagreement is the finding.

### Filed this run

BG0526, BG0527, CR0533, CR0534. **BG0527** is the one to read: the premise "the previous run must
close before the next can open" was tested rather than assumed and is false - `_is_spent` reads a
recorded goal verdict as proof a run is history, though the verdict is written before the close
chain rather than by it, so every run passes through a window in which the slot guard is off.
**CR0534** is the operator's: 64 documented config keys, no command that shows what is in force,
and nothing that revisits a setting against the evidence the run itself produced.

### What this cost, stated plainly

Six full suites at roughly seven minutes each, and the gate's own budget lane reported OVER on
most commits - 383s, 392s, 405s, 406s, 445s against a 380s ceiling already raised once from 120s.
That is CR0510's headline evidence worsening while CR0510's first slice was being built.

The run stayed open for over 24 hours, and the cause is worth recording because no gate reported
it: **eight of the twelve units never left `Ready`.** Delivery committed their code and green
suites and never transitioned them. Every downstream gate then reported a symptom - no review
coverage, no sign-off, a blocked Done gate - and none of the twenty pre-flight blockers said the
units had not been moved. `sprint close` also does not name it. Filed as **BG0528**.

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
