
<!-- close-status:begin -->
> **RUN-01KZ3V4D closed goal-reached.** 13 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **Run of record:** RUN-01KZ3V4D - the close-convergence sprint.
> 39 of 39 points delivered across 13 units. Every unit is terminal, independently reviewed at
> the lane boundary, and signed off by the operator. Six review passes returned five REJECTs
> and 22 blocking findings; every one was repaired in the batch that raised it.

## Landed: RUN-01KZ3V4D - the close converges, and its findings count

The sprint goal was that a close converges in one pass and its findings count: nothing is
repaired inside the close, a repaired REJECT has a route back to covered, and no close gate
reports a green it did not earn. All three clauses shipped.

**The close now has a fixed point.** `sprint close` and `sprint stop` refuse while the working
tree carries an uncommitted change to a file one of their own batch units declares, because a
repair made inside the ceremony reaches terminal after the retro accounted for the batch and
re-opens the ledger the close just satisfied. One run hit that twice in a single close and it
read, from outside, as a sprint that was never being closed. The ledger now tells a close-time
repair from an unaccounted unit, an unavoidable one can be recorded as a reasoned per-unit
override, and re-running a finished close over an unchanged tree is a no-op that says so.

**A REJECT can be answered.** `critic repair` records what was done about a rejection beside the
verdict rather than over it, naming each finding it closes and the evidence closing it. Coverage
distinguishes approved, repaired and unreviewed - the figure that motivated this was wrong by 18
out of 19 because one number cannot carry three states - and the preflight now states the counts
separately and NAMES the units nobody reviewed.

**The suite verdict is earned.** It is written below both suite lanes, proven by executing the
hook rather than grepping it, and bound to the working tree rather than the commit, so it no
longer authorises every edit made after the suite ran.

### What the reviews found, and why it matters

Five of six independent passes returned REJECT. The findings were not cosmetic:

| Finding | Shape |
| --- | --- |
| A one-character closure marked a REJECT COMPLETE | a review bypass through the shipped CLI, in the mechanism built to make rejections answerable |
| `US0624` was false through the command it named | the fix landed in a checklist row while the operator-facing preflight ran a different path |
| `US0619`'s recording lane was wholly inert | replacing all three call sites with `pass` changed no test result |
| A pre-gate APPROVE read as rejected | two authorities answering one question, over 75 rows |
| `BG0492`'s digest was empty on this repo | the exclude form fails when the path is gitignored; every fixture passed |

Two of those were found by the author only because the work was driven against the real tree;
the rest needed a reviewer who had not written the code.

### What is owed

| Item | Where |
| --- | --- |
| The suite-collapse lane writes its green above the collapse check | `BG0507`, open |
| The close report's imports sit outside its own advisory try | `BG0508`, open |
| Day-granularity in the close-time-repair split, and an override that never expires | `BG0509`, open |
| Review at the boundary is still not PROMPTED by anything | `CR0523`, undecomposed |
| A verdict vocabulary separating broken from unproven | `CR0524`, undecomposed |
| A unit's test plan written and reviewed before its code | `CR0525` / `EP0207`, 26 points, unbuilt |

The last three are the natural next sprint: this run made a rejection answerable, but nothing
yet prompts the review that produces one, and half of the previous run's rejections were correct
features whose verifiers could not fail.
