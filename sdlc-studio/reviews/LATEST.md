<!-- close-status:begin -->
> **RUN-01KZQ03V closed goal-reached.** 19 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **Run of record:** RUN-01KZQ03V - the backlog-clearing run that followed the v5.0.0 release.
> The open bug backlog went from **41 units / 117 points to 2 / 19**. Two adversarial passes
> REJECTED four of seven reviewed units with seven blocking findings; every one is repaired and
> re-mutated.

## THE STATE OF THE BAR

`python3 tools/known_issues.py --bar` is the command, not this sentence. It exits 0 only when no
finding sits open at Critical or High. **It does not exit 0 today**: BG0580 is open at High, and
it is the finding this close raised about itself.

**5 Medium findings ship OPEN**, listed by id in `docs/known-issues.md`, which is GENERATED from
the bug corpus and compared byte for byte. Down from the 40 v5.0.0 disclosed.

## WHAT THIS RUN FOUND ABOUT ITS OWN RELEASE

Three findings were release-blocking and none was in any plan:

* **BG0575** - the verified-install path documented in the README had never worked. v5.0.1 was
  cut for it, and the reproduction was re-run against the real published assets before closing.
* **BG0576** - `tag-check` read a locally recorded green and never asked the forge, so BOTH v5
  tags were cut over a CI that had been red for two days with every shipped guard reporting
  green. The failure class this repository exists to prevent, twice in two days.
* **BG0579** - the per-commit gate had outgrown the tool timeouts that run it, so a commit was
  KILLED rather than refused. A kill records nothing and reads as a hang, whose documented escape
  is `--no-verify`.

## WHAT THE CLOSE FOUND ABOUT THE LEDGER

**BG0580, High and open.** Ten units of this run's batch are `Fixed` AND signed off with planned
mutants that were never executed, and five of them still carry `{{name the production change...}}`
placeholders - 26 rows in total. `transition -> Fixed` already refuses exactly this, and it fired
at the CLOSE rather than at any of the ten transitions. Either the gate does not bind when it
should, or it was bypassed ten times; which of those is true decides whether this is ten author
errors or one inert gate, and it is not yet established.

## THE RECURRING FAILURE, MEASURED

Not weak code. **Verification that could not see what it claimed.**

* Six mutants had to be re-chosen because they did not reach the code they named - one patched a
  message rather than the resolver, one a field map rather than the writer, one a `manual`
  verifier that satisfied the lane exactly as the real one did.
* **Two verdicts were registered without being executed**, and both were retracted on the record
  with the `mutation.py retract` verb built earlier in the same run.
* Two guards were not weak but INVERTED: the opposite statement satisfied them (BG0571).
* Three bugs were overturned by re-measurement rather than repaired - BG0519's 4.5x measured
  0.98x, BG0555's debt list held eight already-fixed names, BG0545's second half no longer
  reproduced.

## WHAT IS CARRIED

* **BG0490, BG0493** - triaged rather than built on the operator's ruling, each claim re-measured.
  BG0490 is half lapsed; BG0493 is fully live.
* **BG0577** - shipped NARROWED. Its own premise check falsified the other two halves: 0 of 31
  open bugs carried an executable `Verify:` line, so the repaired-but-open detector has nothing
  to run until grooming catches up.
* **BG0579's second half** - ~5,300 tests still run single-process on 16 cores. Parallelism needs
  `pytest-xdist`, a dependency change that is the operator's call.
