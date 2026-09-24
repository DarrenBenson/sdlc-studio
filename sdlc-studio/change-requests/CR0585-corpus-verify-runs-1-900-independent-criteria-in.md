# CR-0585: corpus-verify runs 1,900 independent criteria in one serial job, so a weekly signal costs 85 minutes and sits under its own cap

> **Status:** Rejected
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), RETIRE
> **Decomposed-into:** EP0254
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .github/workflows/lint.yml, tools/verify-corpus.sh, tools/verify-corpus-baseline.txt
> **Evidence:** Measured in RUN-01M2JA6J, 2026-09-16. corpus-verify on Lint run 35072360410: job 85.6 min, of which the red-criteria pass is 84 min and the dead-stamps pass 73 s, against a 90-minute job cap (raised to 150 in that run's repair). Run 35063993893 measured 75.9 min for the same pass. The pre-push boundary gate measured 749 s, of which module-alone is 551 s. Selector census over every story and bug: 3,439 Verify lines - 2,491 pytest node selectors, 386 WHOLE-MODULE pytest selectors, 366 shell, 126 grep, 58 manual.
> **Date:** 2026-09-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The red-criteria pass executes every executable acceptance criterion across every story already at Done, one after another, in a single job: 84 minutes of the run's 85.6, against a cap that was 90 until this run raised it. The criteria are independent of one another, which is what makes the lane shardable and what makes running it serially a choice rather than a constraint. A lane this long is also a lane that cannot be dispatched to answer a question mid-run: BG0676 needed three dispatches over a morning, and each cost an hour of wall clock nobody could use. The cap is the sharper edge: a job killed at its ceiling is marked failure, which reads exactly like a corpus regression, and BG0676 AC5 reads that conclusion.

## Impact

Anyone waiting on a corpus answer, and anyone reading a red corpus job. A sharded lane turns an 85-minute wait into roughly ten minutes and removes the class of failure where the clock, not the corpus, is what went red.

## Acceptance Criteria

- [ ] The red pass runs as N shards over a deterministic partition, and every criterion lands in exactly one shard - proven by a run whose shard identities union to the unsharded set
- [ ] A single collector judges the union against tools/verify-corpus-baseline.txt and names NEW, went-green and VANISHED ids exactly as the serial lane does today
- [ ] A shard that dies (cap, runner loss) fails the lane by NAME rather than shrinking the union, so a lost shard can never read as a corpus that got smaller
- [ ] The lane's wall clock per shard is recorded, and the job cap is set from the measured figure rather than an estimate

## Recommendation

Shard the red pass across a matrix of runners by a deterministic partition of the criterion set, each shard reporting its own identities, with one collector that unions them and judges the union against the baseline - the baseline stays one file and one number, because a per-shard baseline would hide a criterion moving between shards. Keep the whole-corpus dead-stamps pass where it is at 73 s. Record the wall clock per shard so the partition can be rebalanced on measurement.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Raised |
| 2026-09-21 | audit ruling | still wanted, never started - returned to Proposed, and BOTH of its headline figures are stale. The last successful corpus-verify job measured 57.2 minutes, not the 85.6 filed, and the cap is already 150 minutes - raised in the very run that raised this request - so the `sits under its own cap` half of its title is no longer true. The serial structure is unchanged and the case now rests on wall-clock and dispatch latency alone, not on cap kills. Re-measure before re-proposing. |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): RETIRE - shard the weekly corpus lane (EP0254) |
