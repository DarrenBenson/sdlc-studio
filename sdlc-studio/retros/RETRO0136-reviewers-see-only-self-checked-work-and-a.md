# RETRO-0136: Reviewers see only self-checked work, and a run's real cost is measured and held to budget

> **Date:** 2026-10-27
> **Run:** RUN-01M5EM9N
> **Batch:** US1087, US1088, US1089, US1090, BG1111, BG1000, BG1113, US1094, BG1117, BG1095, US1091, US1093, US1096, BG1078, US1097, BG1127, US1092, US1095

## Keep

- Builders worked in worktrees from one written brief, and the orchestrator only landed, recorded and briefed: 19 units landed on main without a tracked write under a running hook.
- The author self-check gate held every brief (US1089 under `block`): no reviewer saw a diff its author had not inventoried and mutated, and US1094's brief cut a review to about 12 to 33 tool calls.
- Landing by fast-forward only, after aa43a89e: every D0386 commit on main is the exact tree devserver1 judged green.
- `verify_ac run --from-run` stamped the whole batch in one pass, every criterion passing and none manual.

## Stop

- Amending an open run with a seven-story epic: the batch grew from 12 units to 19, every landing queued behind the last, and the run cost about 3.0M priced per point, no better than run two.
- Ruling a sentence TRUE without running it: nine units needed a repair round, most for prose in a docstring, help page or fragment that a command would have refuted.
- Paying the full hook again for a commit refused on a timing test BG0963 does not name: each retry cost another ten-minute hook and a host run.
- Leaving a standing REJECT from an earlier run until the close: BG0962's two 2026-10-07 rows could not be superseded (BG1135), so a unit approved in this run was carried.

## Try

- Hold the batch at plan: new work joins the next run unless the operator rules an amendment, and the amendment is priced against COST-BASELINE.md before it is accepted.
- Clear each carried unit's standing review rows at plan time, so the close never meets one.
- Land units whose Affects do not overlap as one proven tree, so one host run covers several landings.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG1109 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1110 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1114 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1115 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1116 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1118 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1119 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1120 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1121 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1122 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1123 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1124 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1125 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1126 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1128 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1129 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1130 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1131 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1132 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1133 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1134 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| BG1135 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| CR0652 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| CR0653 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| CR0654 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
| CR0655 | not-stop-ship | Darren Benson (operator) | 2026-10-27 |
