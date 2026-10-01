# RETRO-0128: Maya signs, without a re-close, a report that checks VALID and names every operator ruling and carry

> **Date:** 2026-10-01
> **Run:** RUN-01M3T8N1
> **Batch:** BG0826, BG0859, BG0848, BG0829, BG0850, BG0851, BG0849, BG0862, BG0865

## Keep

- Reviews on a detached worktree at the unit's commit while the next unit builds in the main tree: nine units, nine round-1 APPROVEs, no tree contention once paperwork waited for the build.
- BG0862's end-to-end test, run before the sprint was declared done, found the gap nine unit reviews could not: the signed page never stated a non-STOP-SHIP ruling, so the goal was false until BG0865.

## Stop

- Handing a reviewer a base ref computed by hand: BG0849's brief named the unit's own commit, an empty diff; derive it as the unit commit's parent.

## Try

- [LC-002] A goal's end-to-end criterion is the only one that can fail on what no unit owns. Write and run it red at plan time, before the units, so a gap like BG0865 enters the plan rather than arriving mid-run.
- [new: paperwork during a build] An uncommitted verdict or finding in the main tree trips the building worker's commit gate. Commit orchestrator paperwork only between builds, and never write the main tree while a worker builds there.
- [LC-006] Two corpus guards this run (BG0851 AC4, BG0865 AC3) skip when the signed report is absent, so outside this repository they pass with nothing checked. A corpus test fails on a missing file, never skips.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG0863 | not-stop-ship | Claude (orchestrator) | 2026-10-01 |
| BG0864 | not-stop-ship | Claude (orchestrator) | 2026-10-01 |
| CR0592 | deferred | Claude (orchestrator) | 2026-10-01 |
