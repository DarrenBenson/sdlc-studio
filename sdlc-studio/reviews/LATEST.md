# Reviews - LATEST (anchor)

> Derived from **RUN-01KY321Q** (the follow-up batch, 2026-07-21, RETRO-0065).
> Supersedes the RETRO-0064 picture. Full detail lives in RETRO-0065; this is the anchor.

## Where the pipeline is (2026-07-21)

**RUN-01KY321Q delivered 7/7 units, 18 points.** The batch was the follow-up backlog the previous
sprint filed. Goal: *this project can plan and judge a sprint on its own recent measured evidence,
and every guard reaches the code it claims to cover.*
It is the **first run opened with a session-token baseline**, stamped at plan time by BG0236's
fix from the previous sprint, so it should be the first close in this project's history to publish
a real attributable token cost rather than not-attributable.

## What shipped

**Evidence the planner and close rely on**

- **BG0246** - `batch_history` gated on per-unit telemetry, so every interactive sprint was
  dropped: "what sprints ACTUALLY cost" showed the OLDEST rows (128k-188k/unit) while hiding
  RETRO0060 at 265,625/unit. Now included, each row labelled `per-unit` or `sprint-level`, with
  the hidden-variance cost printed beside them.
- **BG0245** - the mutation ledger could only be written by `mutation.py` while the practice is
  hand-applied mutants, so a policy-following sprint read 0/N. `register` records one, and
  **provenance** stops a self-report posing as a measurement.
- **BG0244** - `Actual (tokens)` was a sum over rated units, publishing an absence as zero. 7 rows
  printed `actual= 0` before; 0 do now, and a reader guard means the correction survives the
  ceremony that previously overwrote it.
- **BG0243** - the token delta could land on an unrelated retro. The retro id is now required, and
  the coverage rule was EXTRACTED from the elapsed path rather than copied.

**Guards that did not reach**

- **BG0242** - 35 unconfined git call sites confined, proven rather than asserted: a victim repo
  per module showed **5 of 8 damaging it at HEAD**, three wiping uncommitted state, none after.
- **BG0241** - a spec with no AC Coverage Matrix reported clean; now exits 1, distinct from
  complete (0) and absent (2), with the migration cost measured first (30 of 178 specs).
- **BG0240** - two writers anchored on the cwd, plus a third found in the same file and fixed with
  them, since fixing only the filed two would have made the inconsistency worse.

## What this sprint got wrong about itself

**The author wrote a false claim into a bug about numeric honesty, then into a decision of
record.** BG0246's summary and D0047's rationale both said `batch_history`'s filter was what
stalled the measured-rate counter. It is not - they read different sources, and fixing BG0246
correctly left the counter at 3, as it should have. Caught independently by the implementing agent
and by the author before review, corrected in **D0050**, filed as **BG0248**. Fifth consecutive
sprint in which prose asserted something the code does not do.

**A gate passed a commit that was non-compliant the instant it existed.** The engagement floor
derives "shipped" from `git log --grep`, so a unit no commit has mentioned is invisible. It read 0
violations, the pre-commit gate passed, the commit landed, and the same check immediately reported
2 new violations in files nothing had touched. Filed as **BG0251**.

## Evidence

~62 mutants hand-applied. **Three survived first time** and each drove a second fix, two of them
the L-0159 unreachable-guard class again. One genuinely equivalent mutant was reported as
equivalent rather than quietly dropped. The noise ratchet went **DOWN, 132 to 129**, because leaks
were captured rather than tolerated. Suites 3,598 skill + 273 tool green, gate PASS, drift 0.

Three design forks were ruled by the operator BEFORE the build (**D0047-D0049**). One ruling
carried a constraint the author had not seen - that a registered mutant is self-reported and must
never read as a measurement - and it shaped BG0245 rather than surfacing later as a defect.

## Next steps

- **BG0248** (High) - the measured rate cannot advance under interactive sprints; where it should
  be measured from is unruled. **BG0249** (High) - the `Estimate` column has BG0244's defect in 12
  of 17 rows. **BG0251** the floor's blind spot, **BG0250** a config key no code reads.
- **CR0383** now carries a measured census: 20 scripts resolve `--root` without discovery, 10
  driving writes, worst being `next_id.py` minting **colliding ids** from a subdirectory.
- **BG0247, CR0384, CR0386, CR0387** open. **CR0319** is the release cut and the freeze expired.
- **RFC0050** unbuilt; its risk lens subsumes RFC0049 option B - do not build both.

## Lessons

Two numbers that look related can come from different logs. A gate whose input is derived from
history cannot judge the commit that creates it. Prove containment against a fixture that can
actually fail. Full set: RETRO-0065.
