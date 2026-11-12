<!-- close-status:begin -->
> **RUN-01M77177 closed goal-reached.** 18 unit(s) in the batch. **The run is SIGNED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

Signed on 2026-11-12 over RPT0029 (fingerprint 92ed4ae3b01b2bf2). During the run the operator
answered "Authorise you to sign" when asked how the run should be signed, so the orchestrator
entered `sprint sign --principal "Darren Benson"` on that authorisation, for this run only (D0467).

> **RUN-01M77177, run ten.** Goal: "A signed report's verdicts are provably the reviewers' own,
> and the report is reviewable from the committed tree." Planned at 16 units and 55 points (D0465,
> D0466); delivered 18 units, 57 points, each on an independent APPROVE, with BG1334 and BG1374
> added in-run. Machinery share by theme 3 points (5%), by path all 57. Cost 45.1M priced tokens,
> 791k per point, $126.37 ($2.22 per point) against run nine's 904k and $2.48; the re-close reused
> the first meter reading, so BG1374's fix is not counted. Wall-clock 9.6 h.

## What landed

- **Verdict binding (EP0280, with BG1030).** A review brief names the verdict file its reviewer
  writes (US1011); a recorded verdict is bound to that file's bytes (US1012), drift or a replay is
  named (US1013), the agent that wrote it is read from the harness transcript (US1014), and a
  verdict from the context that edited the unit records as a self-review (US1015). `--rejoinder`
  with no file quotes the seat's standing REJECT from the ledger (US1016). Prose after
  `BLOCKING: none` and a `RULINGS:` line now record as rulings (BG1030).
- **The report of record (EP0276, with BG1010).** The close cites the committed run record
  (US0997), names the plan by digest (US0998), states each priced model's frozen prices and prices
  delegated totals (US1000), and freezes the lane-yield tally (US1001); `build --run` renders the
  named run (BG1010). US0999 is deferred to run eleven (D0465).
- **Run nine's carries.** US1134 (one line on a passing commit), US1149 (the fresh-session check),
  US1147 (Done on its rejecting seat's APPROVE) and BG1300 (the test identity is seeded under the
  private directory; built in the main checkout because Claude Code's worktree check refuses a
  temporary HOME and cannot be turned off).
- **In-run fixes.** BG1334 (US1011's verdict files broke the markdown-evidence lint and turned main
  red) and BG1374 (the report twin printed a bare price-source URL, so the run was reopened once).

## What is owed

- **Known issues carried, all not-stop-ship** (RETRO0143): BG1335-BG1373 and BG1375-BG1381, every
  finding of the run filed as its own bug at the operator's ruling. The triage cap is now 50
  (D0468). One close gap is handed over: the tick-verification item reads US1147, a
  re-review-only carried unit, as unsupported (filed).
- **Run eleven** per D0461: EP0275, the cost pair CR0694 and BG1330, US0999, and BG1333 first;
  CR0699 (effort setting), CR0700 (instruction audit) and CR0701 (ownership trial) are filed (D0464).

## Learned the hard way

- Grep the whole tests tree for every function, string and ledger cell a unit changes, including
  tests landed earlier in the same run: five units reached a test outside their Affects.
- Fast-forward each lane's worktree to main first and again before `lane land` commits: harness
  worktrees start at origin's commit, and a lane committed at its old base is judged on old code.
- Send a repair to a fresh builder; resuming a 190k-token builder for a one-test change cost about
  2.4M priced tokens twice.
