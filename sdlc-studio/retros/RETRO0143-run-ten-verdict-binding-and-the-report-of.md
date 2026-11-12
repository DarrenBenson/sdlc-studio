# RETRO-0143: Run ten: verdict binding and the report of record

> **Date:** 2026-11-12
> **Run:** RUN-01M77177
> **Batch:** BG1030, US1011, US1012, US1013, US1014, US1015, US1016, BG1010, US0997, US0998, US1000, US1001, US1147, US1134, BG1300, US1149, BG1334

## Keep

- Regrooming every unit at HEAD before planning, one engineering-seat agent per area: it corrected line references that had moved 400 to 600 lines since October and found three dependencies D0461 had not listed (BG1030, BG1010, US0997).
- Using each feature on the run's own reviews as soon as it landed: from US1011 on, every reviewer wrote the verdict file its brief named, US1016 rebuilt US1000's round-2 brief from the ledger, and US1014 named the agent that wrote each verdict.
- Fixing a regression that turned main red inside the run as a batch unit (BG1334), and holding the push until it was green, rather than waiving the failing test.
- Building BG1300 last, in the main checkout, with every other commit held: every test and mutant ran under a temporary HOME and /home/darren/.gitconfig never existed.

## Stop

- Stop grooming a unit's Affects from its own files only: five units (US1011, US1149, US0997, US1012, US1000) reached a test outside their Affects, two of them tests another unit had landed earlier in the same run.
- Stop resuming a large builder context for a small repair: US1149 and US1012 each cost about 2.3M to 2.4M priced tokens because a 190k-token context was re-read to make a one-test change.
- Stop collapsing a criterion's Verify lines without timing the result: US1134's AC4 became one line of 17 modules that needs a 530 s timeout, and the stacked lines it replaced had already turned main red.

## Try

- At grooming and again at each lane brief, grep the whole tests tree (scripts/tests and tools/tests) for every function, printed string and ledger cell the unit changes, including tests landed earlier in the run, and put each hit in Affects.
- Fast-forward every lane's worktree to main as the brief's first step and again before `lane land` commits, so a lane is judged on main's code (BG1338, BG1337).
- Send a repair to a fresh builder from the REJECT's verdict file; resume a builder only to hand it a ruling while its staged work sits in its worktree.

## Machinery share (D0442)

Delivered 17 units, 56 points: the 55 planned (D0465) and BG1334 (1, added in-run). By theme, machinery 3 points (5%): BG1300 and BG1334; evidence 35 (EP0280 with BG1030, and BG1010, US0997, US0998, US1001); cost 15 (US1000, US1134, US1149); product 3 (US1147). By path, all 56 points touch the loop scripts, .githooks/ or tools/.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG1335 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1336 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1337 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1338 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1339 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1340 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1341 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1342 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1343 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1344 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1345 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1346 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1347 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1348 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1349 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1350 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1351 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1352 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1353 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1354 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1355 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1356 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1357 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1358 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1359 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1360 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1361 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1362 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1363 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1364 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1365 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1366 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1367 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1368 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1369 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1370 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1371 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1372 | not-stop-ship | orchestrator | 2026-11-12 |
| BG1373 | not-stop-ship | orchestrator | 2026-11-12 |
