# RETRO-0147: Run fourteen: the front door, the evidence page and the effort each seat ran at

> **Date:** 2026-11-16
> **Run:** RUN-01M7GEHM
> **Batch:** BG0947, BG0998, BG1260, BG1395, BG1396, US1160, US1161, US1162, US1163, US1165, US1166, US1167, US1169, BG1177, US1164, BG1474, BG1478, BG1479, BG1480, BG1484, BG1489

## Keep

- Landing the push-blocking fix first and pushing as soon as it was accepted: BG1474 restored the build-trap classes the run thirteen close had retired, and run thirteen's signed seal went up with run fourteen's first wave rather than waiting for this close.
- Folding a reviewer's or the push gate's finding into the lane already holding the files: BG1479 (two overclaiming fragments), BG1480 (three page sentences) and BG1484 (the quiet-success regression) rode in one fixes lane with BG1478, 7 points for one builder.
- Letting the land's hooks find a regression before main does: the report lane's first land was refused on two reds (a filed report citing an uncommitted plan path), and the builder fixed them in place without a review round.
- Resuming the rejecting seat for round 2: US1160's repair was approved by the seat that rejected it, on a rejoinder brief that quoted its finding.

## Stop

- Stop accepting a lane's per-commit test selection as proof a change is safe for main: BG1395's new total line passed its lane and turned test_quiet_success red at the push boundary, refusing the push a second time.
- Stop writing a criterion with no Verify line: BG1479's AC3 had none, so its accept moved the bug to Fixed and then reported it blocked until a manual line was added.
- Stop committing records with a sweeping add while a reviewer is still writing its verdict: US1161's verdict was committed half-corrected (BG1492).
- Stop leaving a builder unwatched for hours: the sweep lane's first builder stalled for 2 h 10 min with nothing written, and was found only by hand (CR0711).
- Stop grooming a unit that adds a commit lane without its registries: US1168 needed a new script and a ruled change to the 31-lane cap, so it was dropped mid-run (D0495).
- Stop handing back a fragment or page sentence unread against its code: three wave-one units claimed more than their code did (US1162's page, BG1395's and BG1396's fragments), each caught by review (lesson class LC-018).
- Stop letting a test read the harness's environment: two critic tests fail only inside an agent session, because the session id reaches the recorded verdict's source field (BG1490, lesson class LC-020).

## Try

- [LC-019] BG1395's total line broke test_quiet_success, which no lane selected, and the push boundary refused 46db0430 (BG1484); before handing back, a builder greps the whole tests tree for every output string it changes and runs those files.
- [LC-021] The evidence lane's generated table wrote empty cells as two spaces and its land was refused under MD060, and a reviewer's verdict was refused under MD038; builders and reviewers now run the main tree's markdownlint binary on every Markdown file they write, generated ones included.
- [LC-010] The push gate passed 7c64bf26 and GitHub's Lint failed it on the green-run noise gate (112 lines against 104), because run thirteen's new author-form warning leaked from passing tests; BG1489 captured the leaks, and BG1493 makes the push gate run the noise gate so the two cannot disagree again.

## Machinery share (D0442)

Delivered 21 units, 50 points: fifteen of the sixteen planned (40 of 42 points; US1168 was dropped under D0495 because its commit lane needs a new script and a ruled change to the 31-lane cap) and six added in-run (BG1474 2, BG1478 1, BG1479 3, BG1480 1, BG1484 1, BG1489 2; D0490, D0491, D0492, D0493, D0494). By theme, the front door is 18 points (US1160, US1161, US1162, US1163, US1164, BG1177, BG1478, BG1480), evidence and cost 6 (US1165, US1166), consumer-visible correctness 13 (BG0947, BG0998, BG1260, BG1395, BG1396, BG1479), and process machinery 13, about 26% (US1167, US1169, BG1474, BG1484, BG1489), within the one-third cap. Three of the machinery units (BG1474, BG1484, BG1489) repaired reds the push gate or CI found, which no plan foresaw. By path, the front door lives in README.md, SUPPORT.md, SECURITY.md and docs/, and the machinery in gate.py, retro.py, verify_ac.py, sprint.py and the test tree.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG1475 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1476 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1477 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1481 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1482 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1483 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1485 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1486 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1487 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1488 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1490 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1491 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1492 | not-stop-ship | orchestrator | 2026-11-16 |
| BG1493 | not-stop-ship | orchestrator | 2026-11-16 |
| CR0709 | not-stop-ship | orchestrator | 2026-11-16 |
| CR0710 | not-stop-ship | orchestrator | 2026-11-16 |
| CR0711 | not-stop-ship | orchestrator | 2026-11-16 |
| LC-010 | not-stop-ship | orchestrator | 2026-11-16 |
