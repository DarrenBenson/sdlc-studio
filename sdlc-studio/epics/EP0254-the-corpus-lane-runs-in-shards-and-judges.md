# EP0254: The corpus lane runs in shards and judges one union

> **Status:** Draft
> **Derived Point Total:** 15
> **Parent:** CR0585
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0585. Delivers the work CR0585 requested.

## Story Breakdown

- [ ] [US0828: the red-criteria pass runs as N shards over a deterministic partition, every criterion in exactly one](../stories/US0828-the-red-criteria-pass-runs-as-n-shards.md)
- [ ] [US0829: one collector unions the shard identities and judges them against the single baseline, naming NEW, went-green and VANISHED as the serial lane does](../stories/US0829-one-collector-unions-the-shard-identities-and-judges.md)
- [ ] [US0830: a shard that dies fails the lane by name, so a lost shard can never read as a corpus that got smaller](../stories/US0830-a-shard-that-dies-fails-the-lane-by.md)
- [ ] [US0831: per-shard wall clock is recorded and the job cap is set from the measured figure](../stories/US0831-per-shard-wall-clock-is-recorded-and-the.md)

## Acceptance Criteria (Epic Level)

- [ ] The red pass runs as N shards over a deterministic partition, and every criterion lands in exactly one shard - proven by a run whose shard identities union to the unsharded set
- [ ] A single collector judges the union against tools/verify-corpus-baseline.txt and names NEW, went-green and VANISHED ids exactly as the serial lane does today
- [ ] A shard that dies (cap, runner loss) fails the lane by NAME rather than shrinking the union, so a lost shard can never read as a corpus that got smaller
- [ ] The lane's wall clock per shard is recorded, and the job cap is set from the measured figure rather than an estimate

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
