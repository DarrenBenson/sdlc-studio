<!-- close-status:begin -->
> **RUN-01M7SS62 closed goal-reached.** 15 unit(s) in the batch. **The run is SIGNED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

**RUN-01M7SS62, run eighteen, is SIGNED (2026-11-19).** It is the first of D0537's cost-per-point
runs: 15 units, 48 points, all on independent APPROVEs, for $126.81 ($2.64 per point) against a
$146.44 forecast, metered across every subagent transcript for the first time (BG1605). Six units
took a repair round. The engineering second seat on the nine high-risk units (D0540) rejected
five, and six of its blocking defects were ones the qa seat had passed; D0541 and D0542 set how
the two seats' verdicts are recorded. The operator delegated the signature (D0539), and the
orchestrator signed over RPT0037 after a rehearsal in a throwaway copy; RETRO0001 was untouched.

> Goal: "Toward cost per unit: one drive step per hand-back, replayed machine-run mutants,
> configurable CI red-run rules, cost measured or flagged." Judged **achieved**.

## What landed

- **The wave driver and one-step hand-back** (US1196, US1197, US1198): `sprint.py drive` runs a
  wave from build to paperwork and `drive step --after <agent>` turns each hand-back into the
  next prompt; it resumes a landing stopped after its commit and holds at an unanswered stop.
- **Landing and repair** (US1192, US1193, US1195): `lane land` takes several worktrees as one
  commit, `--resume` restarts a stopped landing, and `lane brief --repair` quotes the REJECT
  verbatim; lane land now prices each unit's return from the agent transcript.
- **Machine-run mutants** (US1200, US1201, US1202): `mutation.py run --edits` runs a builder's
  edit list, the self-check records the runner's report whole with any hand-run rows, and the
  QA brief replays the author's mutants, marking a disagreement, within lane land's bound.
- **CI red-run rules** (US1236, US1237, US1238): a red main is read before the next push,
  `ci.rerun_limit` and the wait timeout are configurable, and `gate.py --red-run` answers rerun,
  stop or regression across every flaky bug's record.
- **Cost measured or flagged** (BG1605, BG1607): a run opened where no transcript store is found
  warns at plan, and sign writes the accuracy block to the run's own retro.
- **BG1622**, taken in-run (D0544): the plan's new warning leaked into test output and held every
  push above the green-run noise budget until two tests captured it.

## What is owed

- **Runs nineteen to twenty-one** follow D0537's order; US1194 and US1199 open run nineteen.
- **Filed in the run, not taken:** BG1609 to BG1621, BG1623 to BG1629, CR0746 and CR0747, ruled
  not-stop-ship in RETRO0151. BG1610 (a timed-out land orphans its hooks) and BG1614 (lane accept
  records a second seat against the qa brief) shaped how this run was driven. BG1608 (the goal's
  word limit is checked late) was filed at grooming.
- **Release blockers named at the close:** BG1516 and BG1517, the TRD's high-severity gaps on
  the headless lane runner and Verify-line shell execution, which a release cannot carry.
- **Carried from run seventeen and the website run:** BG1591 to BG1598, BG1600, BG1602 to BG1604,
  BG1606, CR0743, CR0745 and RFC0068.
- **Carried from run sixteen:** BG1570 to BG1578, BG1581 to BG1585, BG1587 to BG1589, BG1590,
  CR0740 and CR0741.
- **Carried from run fifteen:** BG1495 to BG1497, BG1499, BG1500, BG1502, BG1504, BG1505,
  CR0713, CR0673, CR0710, US1168, and the after-tag bugs BG1508, BG1510 to BG1514 and BG1301.

## Learned the hard way

- Give a landing the machine to itself: a suite-sized job beside `lane land` pushed its hooks
  past the 1800s limit and orphaned them (BG1610).
- Change nothing between the close and the sign: four files committed after the close made sign
  refuse RPT0037, and the close had to run again.
- A new stderr line from a command the tests run in-process is test noise until captured: run
  the noise gate on its callers before hand-in (BG1622).
