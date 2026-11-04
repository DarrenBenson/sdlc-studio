<!-- close-status:begin -->
> **RUN-01M6F74P closed running.** 23 unit(s) in the batch. **The run signature is OWED and is the operator's** - `sprint sign` seals the batch in one signature.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **RUN-01M5EM9N, the third 6.2 run.** Goal, amended once under US1096: "Reviewers see only
> self-checked work, a run's real cost is measured and held to budget, and 6.2's blockers are
> fixed." Nineteen units (55 points), one QA seat per unit, all Done or Fixed. The efficiency
> epic EP0292 joined the run under D0389. Judged partial: the first two clauses hold on main,
> and 6.2's blockers moved to run four. The run cost 156.4M priced, about 2.84M per point,
> against 2.76M in run two (RPT0022).
> Signed on 2026-10-31 over RPT0022 by the operator; the agent entered the command at the
> operator's instruction ("I sign it off").

## What landed

- **The author's self-check is a gate.** `critic.py self-check record` stores the author's claim
  inventory and mutation run (US1088), the brief shows the author what to run first (US1087),
  and under `review.author_self_check: block` the brief is refused without a current record
  (US1089). A record survives another unit's later commit (BG1117). AGENTS.md names the push
  gate as the full-suite check (US1090).
- **A run's cost is measured, priced and compared.** The meter reads the main thread and every
  subagent transcript, once per message (BG1111, US1091), and never reads a run's opening
  readings as a spend of 0 (BG1127) or mixes counting bases (US1097). The retro and VELOCITY
  carry the priced cost per point under a named basis (US1092). The close flags a run over 1.5x
  its baseline as a known issue (US1095), against `sdlc-studio/retros/COST-BASELINE.md`
  (RETRO0134 and RETRO0135 seeded).
- **Delivery is cheaper to brief.** `sprint.py lane brief` hands a fresh builder its unit
  (US1093). The review brief carries the unit's diff, a verify command and tier budgets
  (US1094). A goal review is one round, and the operator can amend an open run's goal (US1096).
- **Run two's carried units are fixed:** BG1078 (US1076) and BG1095 (US1086). So are BG1000
  (per-commit test selection), BG1113 (the neutrality guard) and BG0962 (closing-review reads
  each unit's latest verdict). BG0962 was approved at round 2 by a rejoinder review under its
  round-one seat id, because its two 2026-10-07 REJECT rows could not be superseded (BG1135).
- **The lessons log is in this clone** (D0371): `sdlc-studio/retros/LESSONS.md`, 447 lessons.
  The 257 past their horizon were extended one window on the operator's ruling (D0391).

## What is owed

- **Known issues carried, all not-stop-ship** (RETRO0136): BG1109, BG1110, BG1114-BG1116,
  BG1118-BG1126, BG1128-BG1135 and CR0652-CR0655. RPT0022 lists each with its severity.
- **Run four (D0389):** CR0645-CR0647 and CR0649, BG0963 (High), US1080-US1083, BG1109 and
  BG1065, with BG1135 and CR0655 to plan. The operator approves the plan before delivery
  starts, and 6.2.0 is tagged once run four is signed.
- **The lessons re-validation** (CR0655): D0391 extended 257 lessons without judging them.
- **The repo-wide unified review** is overdue: LATEST.md predates 292 changed artefacts. The
  close reported it as cadence debt, because every unit in the run was independently reviewed.

## Learned the hard way

- Amending an open run with a seven-story epic cost more than it saved. Landings are serial,
  each needs a host run, and the cost per point did not fall.
- Most repair rounds came from prose ruled TRUE without running it. Execute every sentence in a
  docstring, help page or fragment before the self-check records it.
- A standing REJECT from an earlier run belongs at plan time, not at the close. Its exit is a
  rejoinder review under the round-one seat id.
