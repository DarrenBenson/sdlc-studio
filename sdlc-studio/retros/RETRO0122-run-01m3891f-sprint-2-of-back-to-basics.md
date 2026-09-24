# RETRO-0122: RUN-01M3891F: Sprint 2 of back to basics, fast gates and lessons that graduate

> **Date:** 2026-09-24
> **Batch:** US0879, US0880, US0881, US0882, US0883, US0884, US0885, US0886, US0887, US0888, US0889

## Keep

- One independent review per unit with a two-round cap: 11 units, 4 round-1 REJECTs, each a real defect (a double-counted repeat, cap eviction of live evidence, a template-coupled integrity check, a per-clone retirement), and none needed a third round. Two questions went to persona seats (D0260, D0261) rather than to the operator.

## Stop

- Letting parallel agents leave scratch clones and test temp directories behind: /tmp ran out of inodes mid-run and a commit's suites failed on ENOSPC for reasons unrelated to the change (BG0753).

## Try

- [LC-002] US0885's race test generated on a round hour, so an end floored to the minute passed it, and US0880's AC2 fixture passed a docs read-map it was meant to refuse: before review, ask what each criterion's test still passes with the feature removed.
- [LC-005] US0887's round-2 fix to how hits are keyed silently broke US0888's critic hits in a sibling unit on the same store: when two units write one store, rebase and land them as one.
- [new: shared machine resources exhausted | build] A run's agents share one /tmp, one CPU and one clock; exhausting them fails gates for reasons unrelated to the change. Each agent deletes its scratch tree when done, and the orchestrator reads free inodes and load before starting a commit.
