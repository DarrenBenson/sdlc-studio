# RETRO-0138: Run five delivered the release path and the Cursor meters, at a cost the operator ruled too high

> **Date:** 2026-11-04
> **Run:** RUN-01M6F74P
> **Batch:** BG0958, BG1090, BG1114, BG1116, BG1122, BG1147, BG1160, BG1163, BG1167, US1112, US1113, US1114, US1115, US1116, BG1183, BG1187, US0989, US0990, US0991, BG1197, BG1210, BG1212, BG1216

## Keep

- Building in parallel waves of units with no shared files, with small units sharing one lane and one reviewer (D0404): 19 points landed in about four hours after it, against 14 in the 35 hours before, and agent tokens per point fell from about 200K to about 140K.
- Resuming the original builder for a repair, in a worktree recreated at the same path, and briefing it on the blocking findings only: BG1116, BG1163, US0990 and BG1183 each closed at round 2 that way.
- Letting the review cap carry a unit that did not converge: US0986 went to BG1205 rather than a third round, and the blocking part of it shipped in the run as BG1197.
- Pushing to the gate host mid-run: the full suite there caught four regressions no commit hook selected (the PRD and TSD rows for the Cursor call, the wall-clock census, a shell-hazard false positive), each fixed in the run as BG1210, BG1212, BG1216 and a re-spaced quote.

## Stop

- Asking the operator mid-run: four questions in one day stopped the run before D0404 ruled that sprints decide, record and list their rulings at the sign.
- Running four or five agents at once on a four-core laptop: load reached 15 to 35, commit hooks took 15 to 40 minutes, two commits hit their ceiling, and BG1183's primer tests and every timing-bound criterion flaked under it.
- Briefing a repair on every finding: US1112's repair was asked for all seven, against the lane brief's rule that a repair carries only the blocking ones and files the rest.
- Grooming a timing bound this laptop meets only when idle: BG1183 AC2 (120 s) and BG1187 (120 s) each passed only at load below about 10.

## Try

- Run builders' test passes and commit hooks on the gate host (CR0661), so parallel lanes stop competing for four local cores.
- Before landing any change to a PRD or TSD NFR, run tools/tests/test_lean_prd_refresh.py and test_lean_tsd_refresh.py together: a one-paragraph PRD fix (BG1210) broke the TSD test (BG1216).
- Measure the run's priced cost at each wave, not only at the close: the operator's 1M-per-point norm was missed by three times before anyone measured it.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG1185 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1186 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1188 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1189 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1190 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1191 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1192 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1193 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1194 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1195 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1196 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1198 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1199 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1200 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1201 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1202 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1203 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1204 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1205 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1206 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1207 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1208 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1209 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1211 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1213 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1214 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1215 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1217 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1218 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| BG1219 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| CR0661 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
| CR0662 | not-stop-ship | Claude Opus 5.5 (orchestrator, D0404) | 2026-11-04 |
