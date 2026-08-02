
<!-- close-status:begin -->
> **RUN-01KYY52D closed goal-reached.** 9 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **Run of record:** RUN-01KYZKY5 - **STOPPED, not closed.** 152 of 152 points delivered;
> 27 REJECT / 11 APPROVE over 38 units in five independent passes. Closing it would have
> recorded an approval the review withheld.

## Landed: RUN-01KYZKY5 - the batch delivered in full and did not pass review

Every planned unit shipped: 45 units, 152 points, 24 commits, two dropped with recorded reasons.
Then five independent adversarial passes returned **27 REJECT and 11 APPROVE**, and the run was
stopped rather than closed.

The rejections are not one batch being bad at everything. They split cleanly:

| | Count | What was wrong |
| --- | ---: | --- |
| Feature broken or unreachable | ~13 | zero-caller functions, a bypassable gate, a guard aimed at the wrong tree, `Fixed` with the title still true of the tree |
| Feature correct, evidence cannot fail | ~14 | the command works through the front door; the verifier greps source text |

**The defect worth carrying forward is the second one.** A verifier that asserts the SHAPE of a
change - is the symbol present, does the string appear - stays green when the feature is
deleted. Reviewers demonstrated it by mutation ten-plus times; twice by removing the whole
feature. `BG0401` shipped this defect inside the bug whose own title is "a grep over source
text is not a test of what the source does".

### What is owed

`BG0488`-`BG0494` carry every unrepaired finding with the pass's executed reproduction.
`CR0523`, `CR0524`, `CR0525` carry the process repairs. 23 delivered units sit in `Review`,
held by findings rather than by unfinished work - they return cheaply, because most need a
verifier that can fail rather than a feature.

### Repaired in-run (307ce91d, baec2b42)

The `BG0448` terminal oracle was BYPASSABLE - its regexes scanned the whole artefact while the
refusal said "every acceptance criterion is unticked", so a tick in Steps to Reproduce cleared
it. EP0198's panel sign-off was hollow at the lane and is now reachable end to end. `BG0420`'s
guard scanned the one directory with nothing to find. `BG0483` had exempted every review
document from claim-drift. Eight verifiers now exercise what they claim, each proven to kill
the mutant its predecessor survived. Three false measured claims corrected, one WITHDRAWN
rather than replaced because three measurements disagreed.

### Decisions taken

1. **Stop, do not close.** The units stay in `Review` as real backlog with their evidence.
2. **`lane-check` becomes blocking**, once `BG0491` widens its corpus to bug units. It flagged
   all nine of the units later confirmed hollow, before any reviewer looked, and shipped
   advisory - so it changed nothing.
3. **Test plans move before the code** (`CR0525`, Critical). Reviewing the test is cheaper than
   reviewing the code: this run spent five passes to learn that ~14 verifiers could not fail.
   The `test-spec` type and the name-the-mutant-first rule already ship; the repo holds two
   test specs and this run wrote none.

### Backlog after the run

**296 points across 72 units** (`status.py points`): 226 story, 70 bug. 90 of those points are
this run's units held in `Review`.
