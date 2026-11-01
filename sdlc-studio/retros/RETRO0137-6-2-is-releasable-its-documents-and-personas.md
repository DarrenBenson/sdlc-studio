# RETRO-0137: 6.2 is releasable: its documents and personas match the code, every lesson is judged, and gates cost less

> **Date:** 2026-11-01
> **Run:** RUN-01M6A3K2
> **Batch:** BG0963, BG1065, BG1109, BG1135, BG1139, US1080, US1081, US1082, US1083, US1098, US1099, US1100, US1101, US1103, US1104, US1102, US1105, US1106, US1107, US1108, US1109, BG1137, BG1138, BG1140

## Keep

- Clearing the carried units at plan time: US1076 and US1086 were answered by rejoinder reviews before the run opened, so the close met no standing REJECT from an earlier run.
- Builders in worktrees under one written brief, with the author self-check on main before every brief: 24 units landed, and 36 review passes over them rejected 9.
- Letting one devserver1 push judge several landings, after builders stopped running the full suite themselves: the run cost 109.6M priced, about 1.59M per point over 69 points, against 2.84M in run three.
- Sending each refused or incomplete verdict back to its reviewer rather than editing it: every recorded row is the reviewer's own text.

## Stop

- Landing a unit that grows a shared test file without checking the light-tier units already closed on it: US1104 grew test_lean_prd_refresh.py, US1082 and US1103 failed conformance at push, and both needed a second, full-depth review (BG1167).
- Trusting the commit hook for checks that read every test module or the gate host's layout: BG1065's unconfined git call and US1100's check-ignore through a symlinked .local passed every commit and refused the push (BG1166).
- Briefing a reviewer without the BLOCKING-line rules: US1102's round-1 verdict had to be re-emitted twice, once because it was cut off mid-sentence and once because `critic.py record` refused its untagged BLOCKING items.

## Try

- Before landing a unit that adds a test module or a git call, run test_gitutil.py's sweep and the modules that enumerate tests, in a clone whose sdlc-studio/.local is a symlink, as on the gate host.
- Until BG1167 is fixed, re-derive `critic.tier_for` for every closed light-tier unit that declares a file the landing unit changes, and brief a full review then, not at push.
- Start `sprint.py close --dry-run` as soon as the last unit enters review: the first one here was stopped at 20 minutes without printing a line, and its refusals can be cleared while the reviews run.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG1142 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1143 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1144 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1145 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1146 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1147 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1148 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1149 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1150 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1151 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1152 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1153 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1154 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1155 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1156 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1157 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1158 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1159 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1160 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1161 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1162 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1163 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1164 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1165 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1167 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1168 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1169 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1170 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| BG1171 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| CR0656 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
| CR0657 | not-stop-ship | Darren Benson (operator) | 2026-11-01 |
