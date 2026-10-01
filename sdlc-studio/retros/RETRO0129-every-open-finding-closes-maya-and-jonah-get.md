# RETRO-0129: Every open finding closes: Maya and Jonah get honest commands, safe installs and upgrades, and leaner sprint machinery

> **Date:** 2026-10-01
> **Run:** RUN-01M3VF2J
> **Batch:** BG0726, BG0737, BG0817, BG0827, BG0832, BG0833, BG0834, BG0835, BG0866, US0804, US0966, BG0867, BG0868, BG0869, BG0855, BG0860, US0759, US0784, US0968, US0973, BG0825, BG0831, BG0837, BG0861, US0805, US0969, US0970, US0972, BG0858, US0975, US0976, US0967, BG0876, BG0877

## Keep

- Two file-disjoint build lanes, one in the main tree and one in a worktree landed by rebase or cherry-pick, built 40 units unattended; reviews ran in detached worktrees in parallel, and paperwork was committed with `git commit --only` so a worker's tree was never swept in.
- One independent QA seat per unit found a real blocking defect in 17 of 40 units in round 1; no blocking finding was refuted. Discharge by the rejecting reviewer (BG0850) cleared all six carries inside the run.
- Execute the premise before grooming: the groomer re-ran all nine new bugs at the current code before writing a criterion.

## Stop

- Asking a builder to "fold in cheap extras" with a repair. BG0839's round-1 extras (a writable-parent preflight and a transcript variable) were both round-2 blockers, and US0974's generic step guard shipped a false "nothing was written".
- Hand-listing the shapes a repair must cover. US0974's readability probe moved its defect between rounds (too broad, then the wrong list) until the licence was narrowed to what the criterion names.
- Reaching the 20-finding triage cap with real findings unfiled: the run filed 20 and one (`.py` optional in the retired-surface scan) waits for the next run.

## Try

- [new: a retirement outruns the deletion | build, review] Before retiring a criterion or deleting a test with a removed feature, name the deleted symbol it pins; a test or criterion that pins surviving code is re-pointed, never retired. US0967 left four Done criteria contradicted and US0978 deleted three tests of surviving code under false retirement notes.
- [LC-005] BG0839, US0974 and BG0824 each shipped a round-1 repair that broke a neighbouring path (a missing parent refused, a write-then-read step misreported, a decode crash on the onboarding path). A repair brief carries only the blocking fix and its pins.
- [LC-010] US0977's tests passed under pytest and failed only in CI's one discovery run: `mock.patch.object` hit a loader-held `critic` while the code imported it at call time through a `sys.modules` other modules replace. Patch by name when the code imports at call time.
- A builder that adds a widened env scrub to satisfy a guard test should reuse the pinned list it already has: US0971's `GIT_*` scrub broke fixture isolation until it imported `verify_ac._REPO_LOCATING_GIT_VARS`.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG0870 | not-stop-ship | Claude (orchestrator) | 2026-10-01 |
| BG0871 | not-stop-ship | Claude (orchestrator) | 2026-10-01 |
| BG0872 | not-stop-ship | Claude (orchestrator) | 2026-10-01 |
| BG0873 | not-stop-ship | Claude (orchestrator) | 2026-10-01 |
| BG0878 | not-stop-ship | Claude (orchestrator) | 2026-10-01 |
| BG0882 | not-stop-ship | Claude (orchestrator) | 2026-10-01 |
| BG0885 | not-stop-ship | Claude (orchestrator) | 2026-10-01 |
| BG0886 | not-stop-ship | Claude (orchestrator) | 2026-10-01 |
| BG0887 | not-stop-ship | Claude (orchestrator) | 2026-10-01 |
| BG0888 | not-stop-ship | Claude (orchestrator) | 2026-10-01 |
| BG0889 | not-stop-ship | Claude (orchestrator) | 2026-10-01 |
