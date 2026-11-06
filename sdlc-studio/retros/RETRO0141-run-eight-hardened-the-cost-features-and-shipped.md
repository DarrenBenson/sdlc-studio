# RETRO-0141: Run eight hardened the cost features and shipped the first consumer savings

> **Date:** 2026-11-06
> **Run:** RUN-01M6RZQZ
> **Batch:** BG1240, BG1244, BG1245, BG1246, BG1242, US1129, US1130 (carried at the cap as BG1258), US1131, BG1252, BG1254, US1132, US1133, US1135, BG1257, BG1258, BG1259 (BG1257, BG1258 and BG1259 added mid-run, D0418-D0420; US1134 dropped to 6.4, D0419)

## Keep

- The lean `sdlc-builder` and `sdlc-reviewer` definitions, used from the moment US1131 landed: a lean agent started at about 16k tokens against about 34k for `general-purpose`, and a lean review cost 60k to 120k tokens against about 140k in run seven.
- The full suite on the gate host after each wave (D0417): wave one's integrated tree was checked green in 636 s, at no token cost, before wave two built on it.
- Normalising each hand-in's vocabulary before `lane land`, and batching related small reviews: no self-check was refused after its commit on a label once `norm.py` accepted every changelog fragment.
- Fresh lean agents for repairs and merges: the US1132 merge cost 37k tokens, its finishing builder 53k and BG1259's pin a few dozen calls.

## Stop

- Writing a repair myself without running every check its unit already carries: US1130's repair restored the rule but left its changelog fragment and the doctrine lead false, and the cap carried it to BG1258.
- Telling a merge agent the semantics rather than letting the reviewer's criterion decide: my instruction to judge a subagent's start inside the run window was the defect US1132's round one found.
- Pushing faster than the forge's CI concludes: the Lint job stayed red on main across three pushes because each left before the previous run finished (BG1259, BG1272).

## Try

- A pre-review sweep that runs, for every unit, the tests and Verify lines that read each file the unit changed, so a cut prose rule or a stale fragment sentence is found before review (US1129, US1130, BG1238).
- Serialise units that edit the same function into one lane or strict sequence at planning, not only the same file (BG1269).
- Wait for the forge's CI on the parent before pushing again, or have the pre-push check name an in-progress run (BG1272).

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG1260 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0423) | 2026-11-06 |
| BG1261 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0423) | 2026-11-06 |
| BG1262 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0423) | 2026-11-06 |
| BG1263 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0423) | 2026-11-06 |
| BG1264 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0423) | 2026-11-06 |
| BG1265 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0423) | 2026-11-06 |
| BG1266 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0423) | 2026-11-06 |
| BG1267 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0423) | 2026-11-06 |
| BG1268 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0423) | 2026-11-06 |
| BG1269 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0423) | 2026-11-06 |
| BG1270 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0423) | 2026-11-06 |
| BG1271 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0423) | 2026-11-06 |
| BG1272 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0423) | 2026-11-06 |
| CR0685 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0423) | 2026-11-06 |
| CR0686 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0423) | 2026-11-06 |
| BG1275 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0424) | 2026-11-06 |
| BG1276 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0424) | 2026-11-06 |
| BG1277 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0425) | 2026-11-06 |
