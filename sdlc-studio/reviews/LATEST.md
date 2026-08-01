
<!-- close-status:begin -->
> **RUN-01KYY52D closed goal-reached.** 9 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **Review of record:** [RV0025](RV0025-run-01kyy52d-the-review-learned-to-discriminate.md) - RUN-01KYY52D closing review, verdict APPROVE.

## Landed: RUN-01KYY52D - the review learned to discriminate, and then failed its own new rule

Nine units, 36 points, two epics, goal ACHIEVED. The sprint's product is that **a review now
carries information**: bounded to each unit's declared `Affects` against the run's base ref and
briefed by `critic.py brief` rather than a hand-written prompt, the passes APPROVED some units
and rejected others with executed reproductions, and one explicitly CLEARED a finding it nearly
filed. Every previous review rejected everything, which says exactly as much as approving
everything.

Four independent passes, none by a context that wrote the code (RV0025 has the table). Every
blocking finding was repaired inside the batch that caused it, and both repair sets were then
confirmed by a fresh pass that found nothing new.

**What shipped.** A verdict records a fingerprint of the brief its seat was given, and
`critic.py record` REFUSES one carrying no provenance - the seat-brief rule stops being
doctrine and becomes a refusal. Every finding declares its origin (`[regression]`, `[new]`,
`[pre-existing]`), decided by execution; an untagged one is refused by name. Only regression
and new hold a gate, so a review whose findings all predate the base ref now COVERS its unit
and reports them apart from what blocked. The shipped doctrine states the scope rule as rule
19, guarded by a runnable `tools/doctrine_review_scope.py`.

**The finding worth carrying.** `US0577` shipped a changelog and a commit message both saying
`critic.py brief` emits a fingerprint. It did not - the function had one caller and it was not
that command. Its acceptance test passed throughout because it called the library in-process,
and a library test cannot see missing wiring: the wiring is the part it does not exercise.
Three of five findings in that batch were the same shape. It cost a second review round, which
is verification handed to the reviewer. `CR0520` makes it mechanically detectable; until it
lands, every claim goes through the shipped CLI in a fixture before a reviewer is asked.

**Owed.** `CR0514` (an amigo panel satisfies the reviewer-of-record half, so a close stops
needing a human to type) is the next build. `CR0522` was filed from this very close: the
repo-wide periodic review blocked a sprint whose own work was fully reviewed and signed off,
and the bounded exit would not file it because the lane is classed a correctness gate. Also
open: `CR0518` (a tool runbook printed at plan time), `CR0519` (a suite verdict read from a
file, never from a pipe that swallows the exit code), and `BG0476`-`BG0478`, `BG0483`.

**Cost.** The gate now measures 444s against a declared 380s ceiling, +17%, and +40% over the
2026-07-26 baseline. That is paid per commit, so it is the sprint's largest single cost.
