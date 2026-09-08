<!-- close-status:begin -->
> **RUN-01M1WPNV closed goal-reached.** 5 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> **Run of record:** RUN-01M1YK70 - the delivery loop refuses before the seats do (D0183). Six
> units, 27 points, 98 mutants registered killed and none surviving; the rows of ten earlier
> units re-measured after every shared-file edit. Goal **achieved**, every clause measured on
> main. The push stays the operator's.

## THE HEADLINE: THE GATE THIS BATCH BUILT CAUGHT ITS OWN BUILDERS

`verify_ac run --coverage` was run on the two stories that built it before either was briefed.
On US0815 it named thirteen unexecuted added lines and a new file measured as zero statements,
which produced six mutants and a real fix; on US0816 it named one line, an unused branch of the
test's own fixture, removed rather than ruled. That is the instrument doing to its author what
the seats had been doing all run.

The seats still found eight blocking defects across thirty-three delivery verdicts, and every
one was a branch a fixture could not reach rather than wrong code: an unparseable ledger read as
clean, an uncommitted edit to a TRACKED file where the fixture used an untracked one, a stale
coverage data file the fixture wrote as prose that `coverage combine` cannot read, coverage's own
verbs failing read as no data, a printed retraction a shell mangles because 67 of 430 ledger rows
carry a backtick, and a test module red under the plain unittest runner because `unittest.mock`
was used without importing the submodule - the exact failure the `module-alone` boundary lane
exists to catch, hidden by pytest importing it for us.

## WHAT LANDED

- BG0653 - a staged test rename or deletion that orphans a stamped `Verify:` selector is refused
  at pre-commit, resolving index blobs by AST in all four selector shapes.
- BG0652 - `status.py hint` inside one corpus sweep: 57 s to under a second.
- BG0614 - `mutation.py audit` names every duplicated ledger key with its rows, tags stale and
  missing targets, and refuses a ledger it cannot parse.
- US0818 - `register` replaces the identical live row, refuses a disagreeing one, and prints the
  retraction as a command that runs as printed.
- US0815 - `verify_ac run --coverage` names every line a unit itself added that its own verifiers
  never executed, and refuses when the measurement cannot be trusted.
- US0816 - the Fixed and Done gates read that measurement. `report` by default, `block` here from
  2026-09-07, `off` collects nothing, an unknown value is refused by name, and a line ruled
  equivalent is subtracted and counted in the depth field.

## THE SECOND ROUND, AND WHAT IT COST

Round two ran on every unit whose repair was unreviewed, and rejected again: four seats,
four rejections, converging from opposite directions on one defect. `coverage withdraw`
searched by the ruling's REASON text, so a withdrawal retracted whichever row came first
while reporting the row named, and on an escaped pipe it matched nothing, crashed on a
bare assertion, and under `python3 -O` reported success with the waiver still live. Beside
it, a ruling this run wrote claimed its line was reachable only by breaking a tool the
suite needs; two seats reached it with every tool intact. The fixture now spawns a traced
child before the verifier hangs, the ruling is withdrawn on the record rather than
restated, and the withdrawal is keyed on the row's own file, line and hash.

The lesson the run leaves is narrow and repeatable: the mechanism that waives a check is
itself a check, and it needs the same adversarial treatment as the thing it waives.

## WHAT IS OWED

- The push: twelve commits stand unpushed. The pre-push hook pays three boundary lanes, roughly
  fifteen minutes.
- US0817 (CR0565, the self-run gate) was deferred at plan time and opens the next run.
- Fourteen Mediums and the consolidated Low CR are disclosed and ruled not-stop-ship in RETRO0115.
