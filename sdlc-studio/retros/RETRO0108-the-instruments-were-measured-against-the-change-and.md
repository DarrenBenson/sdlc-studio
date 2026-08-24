# RETRO-0108: The instruments were measured against the change, and wave 2 shipped unreviewed

> **Date:** 2026-08-24
> **Batch:** US0671, US0672, US0673, US0674, US0675, US0676
> **Goal:** A unit's own evidence is made honest: a test that never reaches the change it claims to cover is reported rather than counted as proof, and a `Verification depth` field states only what the mutation ledger supports.
> **Delivered:** 6 / 6   **Blocked:** 0

## Delivered

- US0671 - `verify_ac revert-check` reverts a unit's declared production files to the run's base ref, re-runs that unit's own `Verify:` selectors, and REFUSES when no counted criterion goes red. Green after the revert means the test never reached the change.
- US0672 - the tree is restored byte-exact, including content, file MODE and symlink targets, and including when the check is interrupted: SIGTERM, SIGINT and SIGHUP all restore before re-raising.
- US0673 - a unit whose `Affects` names no production file is REPORTED, not passed. Exemptions are declared per criterion and granted only when EVERY row on it is `unnameable`.
- US0674 - `revert-check` binds as an ADVISORY lane at the push and release boundaries and accumulates its yield in `sdlc-studio/.local/revert-check-yield.json`, so the decision to make it blocking will be taken on a measured number.
- US0675 - every COUNT in `Verification depth` is read from the mutation ledger through `mutation.plan_execution`, and an unexecuted row is named rather than absorbed into a total.
- US0676 - the derived half of the field is delimited and fingerprinted, and the blocking `derived-depth` gate lane refuses a hand-edit inside the delimiters.

## Blocked / deferred

- Nothing in the batch was blocked. All six units delivered.
- US0677-US0683 (24 points) remain HELD at Draft. They are the CR0549 and CR0550 grooming, and a goal review found both CRs mis-specified before a line was written. They are annotated with the specific defects and were deliberately not re-groomed inside this run.

## What went well

- The forecast was accurate for the first time: 2,710,181 tokens forecast against 2,691,843 actual, 0.7% out. The points-times-rate model held.
- 128,183 tokens per point against 525,434 on the previous run, a 4.1x reduction, with ONE delivery round rather than six. D0146's round cap did what it was adopted to do.
- The narrowing held. The run was opened deliberately small after a second goal review caught two fabricated regression cases in the original plan, and the batch that resulted delivered 6 of 6.
- The gates caught what the author did not: `repo-writes` refused a commit whose suites had modified a tracked file, `suite-claim` refused a verdict recorded at the wrong HEAD, and the release-notes claim guard refused a known-issues paragraph that turned out to be wrong in BOTH directions - naming three fixed bugs as open and missing one that was open.

## What was hard / what stalled

- The new lane corrupted the suite that was testing it. `RevertCheckLaneTests` drove `gate.py --boundary push` against the REAL repository, so the lane reverted `verify_ac.py` while a parallel xdist worker was reading it, and an unrelated test failed intermittently on a docstring fragment. Fixed in two stages: the new tests moved to throwaway workspaces, then the pre-existing boundary runs were scoped with `--only`.
- An adversarial reviewer, following the D0149 oracle procedure, ran a manual revert against the MAIN working tree and destroyed roughly 400 uncommitted lines of `verify_ac.py`. The file came back byte-identical to the base ref. Recovered by re-applying the wave-2 edits. Filed as BG0604.
- Two declared mutants SURVIVED for reasons that had nothing to do with the code. One test pointed at the wrong function; in another, a sibling guard masked the guard under test, so a test asserting only the exit code passed with the repair removed. Both were found by executing the mutant, neither by reading.
- `testplan derive` refused several mutant cells for carrying no edit verb and for restating their own criterion above the 60% ceiling, so plan rows had to be reworded before they could be recorded.

## Lessons

- A staging decision that puts a unit LAST also puts it outside the review that already ran. D0149 required wave 2 to land last in its own commit so the oracle stayed honest; the effect was that US0674 and US0676 - the two gate lanes, the highest-blast-radius units in the batch - were never in front of delivery round 1. Round-1 briefs exist for US0671, US0672, US0673 and US0675 and for no others. The review hole was created by the ordering, not by an omission anybody noticed.
- Absent and could-not-ask must be different answers, and this run needed the lesson TWICE. `_base_blob` read any git failure as "absent at base" and deleted the production file, manufacturing the red it was looking for. Separately, a verifier that never RAN was counted as green evidence that the tests reached the change. Both are the same error: an unmeasured state collapsed into a measured one.
- A fixture whose counts are EQUAL cannot detect a swap, and the REPAIR for it moved the defect rather than closing it. The derived-depth fixture used 2 criteria, 2 rows and 2 executions, so four of five counts survived being exchanged. It was rebuilt as 3 criteria, 4 rows, 3 executed - and the round-2 QA seat proved that still degenerate: criteria(3) EQUALS executed(3), and killed, survived, equivalent and not-run are ALL 1. The test docstring asserting "every count is a different number" was false, and so was the same claim in the commit message and in the first draft of this retro. Two mutants survive against the final file - swapping the killed and survived counts, and sourcing the criteria count from the ledger's executed rows instead of the artefact's ACs. The lesson is not the original defect but the repair: a fix aimed at ONE equality restored one number and left four, and nobody re-checked the property, only the number that had been complained about.
- A gate lane that mutates the shared working tree corrupts whatever else is reading it. `revert-check` reverted this repository's own `verify_ac.py` underneath a parallel test worker. The same shape destroyed a reviewer's uncommitted work through the manual oracle. One defect, two victims, filed as CR0552 and BG0604.
- A partial disposition recorded twice reads as two partial dispositions forever. `critic.py repair` computes the outstanding set from the closures in that invocation alone, so four units whose findings were fully closed across two calls each left two rows stamped PARTIAL, each naming as outstanding what the other row closed. Filed as BG0605.

- A plan row can be killed by a test the criterion does not name, and the toolchain will call that covered. `plan_execution` joins rows to the ledger on (criterion, row) and never asks WHICH node did the killing, though the ledger records it and the `Verify:` line states which node was supposed to. An independent plan review found SIX such rows in this six-unit batch - in the batch whose whole subject was that a unit's own evidence must be honest - and found them by reading the ledger against the Verify: lines by hand. Filed as BG0606, with CR0554 to make the comparison the tooling already has the data for.

- A repair whose test can be satisfied by EITHER of two guards pins neither, and I shipped that shape while repairing this very defect. The widened path pattern grew two arms - any extension once a `/` is present, and an allowlist for bare filenames - and my first test used one fixture, `config/settings.yaml`, which BOTH arms match. Deleting either arm left the test green. Two mutants survived my own repair, and I found them only because I executed them rather than trusting the green. The fix was two tests, each with a fixture only one arm can see: a bare `settings.yaml` and a `config/values.jsonnet`. Name the mutant first is not enough - name one mutant PER GUARD.

- The derived field caught its own run's stale evidence, which is the first time an instrument this project built reported against the session that built it. Registering the newly-executed mutants invalidated every earlier registration for the same targets - registration is keyed on the target's content hash, and the close had edited `verify_ac.py` and `gate.py` - so `depth` went from "executed 5" to "executed 3" and named the rows that no longer had support. Nothing else in the toolchain would have said a word: the suite was green, the criteria all passed, and the old counts sat in the fields looking exactly as they had. Twenty-two rows were re-executed against the current tree as a result, and every unit now reads `not-run 0`. LL0053 says register AFTER the last edit; what this adds is that the FIELD is what tells you when you did not.

- The plan review took FOUR rounds, and the biggest single cause was a rule already written down: I hand-edited test-plan tables that `verify_ac.py testplan derive` owns. That produced a FUSED table row inside US0674's AC4 Title cell - a row a human reads and `testplan_rows_by_criterion` cannot see, so the unit's own derived field said "plan rows 8; executed 8; not-run 0" and every one of those numbers was computed over a table missing a row - and Title cells on two US0676 criteria stating a different criterion's claim. Running the tool repaired all of it in one command and then reported "unchanged". AGENTS.md's rule is "always look for a tool before doing anything by hand", the runbook names this exact command, and the failure mode it prevents is not sloppiness but a table that parses differently from how it reads.

- A repair for unpinned behaviour can itself ship unpinned, and did. `_first_three` was added to fix a finding that the lane truncated its output silently - and it shipped with no test and no plan row, so the fix for "this is not pinned" was not pinned. An independent review found it one round later. The check is mechanical: after writing a repair, ask what test fails if the repair is removed, and if the answer is none, the repair is a claim.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- Mutate only in an isolated checkout of your own. Never `git stash` or `git checkout --` against a tree somebody else is reading - both are tree-wide, and over uncommitted work the damage is indistinguishable from the work itself.
- Register mutants AFTER the last edit to their target. Registration is keyed on the target's content hash, so an edit invalidates every prior registration and leaves survivors reported as kills.
- An absence and an unanswerable question are different facts. A code path that cannot tell them apart will report the more convenient one.
- A row that reads `killed` is the strongest evidence this toolchain produces (displaces "no two counts in a fixture may be equal", which the next batch's units do not turn on), and it can be produced by a test the criterion never named. Check the kill node against the criterion's own `Verify:` line before believing it.
- Exercise every claim through the shipped ENTRY POINT before asking for review. A library call that passes in-process proves nothing about the CLI that nobody wired.

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
| BG0463 | not-stop-ship | authoring session | 2026-08-24 |
| BG0490 | not-stop-ship | authoring session | 2026-08-24 |
| BG0493 | not-stop-ship | authoring session | 2026-08-24 |
| BG0567 | not-stop-ship | authoring session | 2026-08-24 |
| BG0578 | not-stop-ship | authoring session | 2026-08-24 |
| BG0581 | not-stop-ship | authoring session | 2026-08-24 |
| BG0586 | not-stop-ship | authoring session | 2026-08-24 |
| BG0587 | not-stop-ship | authoring session | 2026-08-24 |
| BG0588 | not-stop-ship | authoring session | 2026-08-24 |
| BG0591 | not-stop-ship | authoring session | 2026-08-24 |
| BG0592 | not-stop-ship | authoring session | 2026-08-24 |
| BG0599 | not-stop-ship | authoring session | 2026-08-24 |
| BG0600 | not-stop-ship | authoring session | 2026-08-24 |
| BG0601 | not-stop-ship | authoring session | 2026-08-24 |
| BG0602 | not-stop-ship | authoring session | 2026-08-24 |
| BG0603 | not-stop-ship | authoring session | 2026-08-24 |
| BG0604 | not-stop-ship | authoring session | 2026-08-24 |
| BG0605 | not-stop-ship | authoring session | 2026-08-24 |
| BG0606 | not-stop-ship | authoring session | 2026-08-24 |
| BG0607 | not-stop-ship | authoring session | 2026-08-24 |
| BG0608 | not-stop-ship | authoring session | 2026-08-24 |
| BG0609 | not-stop-ship | authoring session | 2026-08-24 |
| CR0549 | deferred | authoring session | 2026-08-24 |
| CR0550 | deferred | authoring session | 2026-08-24 |
| CR0551 | deferred | authoring session | 2026-08-24 |
| CR0552 | deferred | authoring session | 2026-08-24 |
| CR0553 | deferred | authoring session | 2026-08-24 |
| CR0554 | deferred | authoring session | 2026-08-24 |
| CR0424 | deferred | authoring session | 2026-08-24 |
| CR0441 | deferred | authoring session | 2026-08-24 |
| CR0496 | deferred | authoring session | 2026-08-24 |
| CR0497 | deferred | authoring session | 2026-08-24 |
| CR0499 | deferred | authoring session | 2026-08-24 |
| CR0503 | deferred | authoring session | 2026-08-24 |
| CR0504 | deferred | authoring session | 2026-08-24 |
| CR0507 | deferred | authoring session | 2026-08-24 |
| CR0509 | deferred | authoring session | 2026-08-24 |
| CR0511 | deferred | authoring session | 2026-08-24 |
| CR0512 | deferred | authoring session | 2026-08-24 |
| CR0515 | deferred | authoring session | 2026-08-24 |
| CR0523 | deferred | authoring session | 2026-08-24 |
| CR0524 | deferred | authoring session | 2026-08-24 |
| CR0526 | deferred | authoring session | 2026-08-24 |
| CR0528 | deferred | authoring session | 2026-08-24 |
| CR0529 | deferred | authoring session | 2026-08-24 |
| CR0530 | deferred | authoring session | 2026-08-24 |
| CR0531 | deferred | authoring session | 2026-08-24 |
| CR0533 | deferred | authoring session | 2026-08-24 |
| CR0534 | deferred | authoring session | 2026-08-24 |
| CR0535 | deferred | authoring session | 2026-08-24 |
| CR0536 | deferred | authoring session | 2026-08-24 |
| CR0539 | deferred | authoring session | 2026-08-24 |
| CR0540 | deferred | authoring session | 2026-08-24 |
| CR0543 | deferred | authoring session | 2026-08-24 |
| CR0544 | deferred | authoring session | 2026-08-24 |
| CR0545 | deferred | authoring session | 2026-08-24 |
| CR0546 | deferred | authoring session | 2026-08-24 |
| CR0547 | deferred | authoring session | 2026-08-24 |
| CR0548 | deferred | authoring session | 2026-08-24 |

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
<!-- accuracy:end -->

- The forecast landed within 0.7%, the first accurate one on record, and the reason is legible: this batch ran ONE delivery round where the previous ran six. The points-times-rate model is not wrong about the work - it was wrong about the ceremony, and D0146 removed the variance rather than the cost. Do not re-fit the constants on a single accurate row.

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
| `revert-check` mutates the live working tree, so a boundary gate rewrites files underneath concurrent readers | CR0552 |
| The exemption reason floor counts characters, so twelve junk characters buy a blanket exemption | CR0553 |
| The D0149 oracle procedure tells a reviewer to revert by hand and imposes no restore obligation | BG0604 |
| The repair ledger computes outstanding findings per record, so two partial repairs both read as PARTIAL | BG0605 |
| Six test-plan rows across US0671, US0674 and US0676 declare mutants their own criterion's verifier cannot die on | fixed-in: the close - the rows were re-filed onto criteria whose tests reach them, nine criteria were added binding behaviours that had a test and no criterion, and BG0606 is closed by that work rather than carried |
| A row killed by a test no criterion names reads as `killed`, though the ledger records both the kill node and the criterion's asked-for node | CR0554 |
| A unit's verdict is the last row written, so one seat's APPROVE after another seat's REJECT makes a rejected unit read approved | BG0607 |
| Round 2: the exemption pattern still could not see a production file whose extension was not a source-code one, live on BG0560 AC1 | fixed-in: the close commit, pinned by two tests isolating each arm of the pattern |
| Round 2: the boundary lane's own call to the yield recorder was unpinned - deleting it left the whole suite green | fixed-in: the close commit, pinned by a test that drives `gate.py` at a real boundary and reads the file back |
| Round 2: the derived-depth seal judged only the FIRST span, so a second span carrying false counts passed the blocking lane | fixed-in: the close commit, pinned at both span positions |
| Round 2: the fixture's counts were still not pairwise distinct, so four swap mutants survived | fixed-in: the close commit, fixture rebuilt to 3/12/7/1/2/4/5 and all four mutants re-executed and killed |
| Round 2: this commit made a true sentence false in the release notes' own disclosure paragraph | fixed-in: the close commit, both paragraphs re-derived from the corpus |
| Round 1 never saw US0674 or US0676, because the wave ordering put them after it | fixed-in: the close, which ran a full round-2 pass over all six units before any transition |
| Every round-1 finding, 18 blocking across four units | fixed-in: f4db0a84 |
| The gate is 738s against a 380s budget, +133% since the 2026-07-26 baseline | declined: the per-test rate is 0.124s against a 0.152s ceiling, so this is suite VOLUME rather than slowness, and it is not this run's work to re-baseline |

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

- Delivery review rounds: 2. Test-plan plan review rounds: 4 - it rejected all three units three times, and every round's blocking findings were closed by the next. Round 2 ran three seats over all six units and REJECTED four of them on five blocking findings, every one proved by execution rather than by reading; all five were repaired at the close and each is pinned by a mutant that was applied and killed. Round 1 never saw US0674 or US0676.
- Tokens: captured by `accuracy --tokens-from-harness` at close · Duration: captured at close · Critic rejects: 4 recorded at round 1 (US0671, US0672, US0673, US0675), all repaired; US0674 and US0676 had no round-1 pass
