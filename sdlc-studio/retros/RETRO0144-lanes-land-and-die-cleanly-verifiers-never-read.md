# RETRO-0144: Lanes land and die cleanly, verifiers never read green wrongly, and every unit's cost is priced

> **Date:** 2026-11-13
> **Run:** RUN-01M78TKD
> **Batch:** BG1190, BG1228, BG1112, BG1005, BG1009, BG0991, BG1336, BG1337, BG1339, BG1344, BG1330, BG1279, BG1331, BG1305, BG1371, BG0965, BG1340, BG1341, BG0990, BG1343, BG1333, BG1261, BG1262, BG1372, BG1420

## Keep

- One builder and one reviewer per file-cluster lane: 24 units went through nine lanes and two repair lanes, so each agent's fixed reading of a file was paid once for several points (D0469, D0471).
- An at-HEAD triage by cheap read-only agents before planning: three agents checked 74 bugs in under 300k tokens, closed one that was not real, cut one to its missing test and sent two Affects corrections into the plan.
- Joining a reached test to a unit's Affects by a recorded ruling, changed only as far as the criterion requires (BG1330, BG1005, BG1331), rather than deleting or skipping it.
- Building the package upgrade (BG1372) last, in the main checkout, with npm confined to a temporary HOME and cache and install scripts off: nothing was written under the real home directory.

## Stop

- Stop running six builders at once on this eight-core host: the load average reached 18, one land timed out at 900 s and commit hooks took 857 s against a 90 s budget.
- Stop accepting a carried unit's re-review under a new reviewer id: BG1190's APPROVE had to be written again under the seat that rejected it, and the stray row stays in the ledger (BG1400).
- Stop leaving the full suite to the run's first push: it came after 24 units and found five red tests that no lane's selected run had reached (BG1420).

## Try

- Push, or run `tools/run-suite.sh all`, after each wave lands, so a regression the selected runs miss is found while its lane's context is fresh.
- Check a lane's self-check surfaces before `lane land` commits, while the builder can still be resumed (BG1399), and price a multi-unit lane by splitting its builder's total by points (BG1397).
- Cap a wave at four builders on this host, and put every agent's temporary files under ~/.cache/sdlc-tmp from the start: /tmp is a 6.8G tmpfs that reached its quota mid-run.

## Machinery share (D0442)

Delivered 25 units, 52 points: the 49 planned (D0471) and BG1420 (3, added in-run). By theme, cost 10 points (BG1279, BG1305, BG1330, BG1331), product 3 (BG1333), machinery 39 (75%), over the one-third cap and declared as a maintenance run (D0469, D0471). By path every unit but BG1372 touches the loop scripts.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG1382 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1383 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1384 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1385 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1386 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1387 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1388 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1389 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1390 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1391 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1392 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1393 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1394 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1395 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1396 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1397 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1398 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1399 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1400 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1401 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1402 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1403 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1404 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1405 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1406 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1407 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1408 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1409 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1410 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1411 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1412 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1413 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1414 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1415 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1416 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1417 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1421 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1422 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1423 | not-stop-ship | orchestrator | 2026-11-13 |
| BG1424 | not-stop-ship | orchestrator | 2026-11-13 |
