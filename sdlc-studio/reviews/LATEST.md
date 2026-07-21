# Reviews - LATEST (anchor)

> Derived from **RUN-01KY321Q** (the follow-up batch, 2026-07-21, RETRO-0065).
> Supersedes the RETRO-0064 picture. Full detail lives in RETRO-0065; this is the anchor.

## Where the pipeline is (2026-07-21)

**RUN-01KY321Q delivered 7/7 units, 18 points.** The batch was the follow-up backlog the previous
sprint filed. Goal: *this project can plan and judge a sprint on its own recent measured evidence,
and every guard reaches the code it claims to cover.*
It is the **first run opened with a session-token baseline**, and it did publish an attributable
cost - 439,982 tokens. It is also where the sprint found its sharpest defect: that figure counts
only the main thread. See below.

## What shipped

**Evidence the planner and close rely on**

- **BG0246** - `batch_history` gated on per-unit telemetry, dropping every interactive sprint, so
  "what sprints ACTUALLY cost" showed the OLDEST rows while hiding RETRO0060 at 265,625/unit. Now
  included, labelled `per-unit` or `sprint-level`.
- **BG0245** - the mutation ledger could only be written by `mutation.py` while the practice is
  hand-applied mutants, so a policy-following sprint read 0/N. `register` records one, with
  **provenance**, and a self-reported SURVIVOR is now named rather than quietly improving the lane.
- **BG0244 / BG0243** - `Actual (tokens)` published an absence as zero (7 rows before, 0 now); the
  token delta could land on an unrelated retro, so the retro id is now required.

**Guards that did not reach**

- **BG0242** - 35 unconfined git call sites confined, proven not asserted: a victim repo per module
  showed **5 of 8 damaging it at HEAD**, three wiping uncommitted state; none after.
- **BG0241 / BG0240** - a matrix-less spec reported clean, now exits 1 (migration cost measured
  first: 30 of 178 specs); three cwd-anchored writers fixed.

## What this sprint got wrong about itself

**The closing review REJECTED, then APPROVED at round 2.** Three MAJORs: two in BG0244's new Note
column reproducing the defect it was filed to end, one where registering a SURVIVED mutant made the
gate quieter than registering nothing. Repaired; the same reviewer re-ran its reproductions and
mutation-tested the repair. **Goal: PARTIAL** - guards done, measurement not: the close still
cannot state its own cost within 3x.

**A false claim went into a bug about numeric honesty, then into a decision of record.** BG0246's
summary and D0047's rationale said `batch_history`'s filter stalled the measured-rate counter. It
does not. Corrected in **D0050**, filed as **BG0248**.

**The first token figure this project ever measured is wrong by nearly 3x and looks right.** The
capture sums the session transcript, which carries ZERO sidechain records, so delegated agents are
invisible. Published 439,982; the four cluster agents alone spent 787,834, so the true cost is at
least 1,227,816 - a **64% understatement** labelled "the run's own spend". At 18 points it reads
24,443/pt against a 25,000 seed, a 2.2% miss inviting the conclusion the estimator is validated;
the true rate is at least 68,212/pt. The calibration was computed BEFORE the exclusion was
checked. Filed as **BG0252**.

**A gate passed a commit that was non-compliant the instant it existed.** The engagement floor
derives "shipped" from `git log --grep`, so a unit no commit has mentioned is invisible. It read 0
violations, the gate passed, the commit landed, and the check then reported 2 new violations in
files nothing had touched. Filed as **BG0251**.

## Evidence

~62 mutants hand-applied. **Three survived first time**, two the L-0159 unreachable-guard class
again. Noise ratchet **DOWN, 132 to 129**. Suites 3,598 + 273 green, gate PASS, drift 0.

## Next steps

- **BG0248** the rate cannot advance under interactive sprints; **BG0249** the `Estimate` column
  has BG0244's defect in 12 of 17 rows; **BG0251** the floor's blind spot; **BG0250** a dead key.
- **CR0383** census: 20 scripts resolve `--root` without discovery, 10 driving writes, worst
  `next_id.py` minting **colliding ids** from a subdirectory.
- **CR0388** / **LL0039** - `git add -A` during a review stages whatever a concurrent process
  left; a symlink farm plus a redirect writes into the source tree, as the reviewer discovered.
- **BG0254** (High) - measured at sign-off: the forecast said 400,000 and the sprint cost at
  least 4,119,916, over 10x, because the forecast prices only the BUILD (787,834 of it) and this
  project spends most of its budget proving the build correct. The seed is 5.9x to 9.2x low.
- **BG0247, BG0253, CR0384, CR0386-0388** open. **CR0319** is the release cut.

## Lessons

Check what a measurement EXCLUDES before concluding from it. A gate deriving its input from history cannot judge its own commit. See RETRO-0065.
