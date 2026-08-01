# Latest review anchor

<!-- close-status:begin -->
> **RUN-01KYX375 closed stopped.** 9 unit(s) in the batch. This was a `plan` rung, not a build - its units end at their own terminal and no Done sign-off is owed.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> **Goal verdict:** PARTIAL - the run object is measurably more honest at its close and the
> gate around it now blocks a collapsed suite and prices itself; the charter-queue clause was
> never started
> · **Delivered:** 9 units / 27 points of a 37-unit 150-point plan (re-cut from 46/150 at plan)
> · **Carried:** 28 units dropped from the batch, each with a recorded reason

## Landed: RUN-01KYX375 - nine units, three review rounds, and what the reviews found

Nine bugs Fixed across eight commits, every one TDD-red-first and mutation-checked. One theme:
**a guard reporting green over something it never checked.** A collapsed suite now BLOCKS the
commit instead of declining to record a timing (BG0413). The planner and the budget lane can no
longer disagree about what the same gate costs (BG0415). The close reports the retro validator's
unreplaced-scaffold warning instead of discarding it, and refuses a retro nobody wrote (BG0418,
BG0459). The dry run accounts for every chain step (BG0460). `stop` no longer counts a unit
awaiting an independent signature as work it threw away (BG0455). The overhead ratio survives to
`VELOCITY.md` (BG0372). A v3 ULID is no longer exempted from the provenance check by an ordinal
cutoff (BG0466). The evidence lessons from five consecutive REJECTs ship as LL0050 (BG0422).

**The reviews are the result, and they are not comfortable reading.** Three independent
adversarial seats, fresh contexts in isolated worktrees, ~60 mutants. They rejected seven of the
nine units on round 1-2, and three of the repairs on round 3.

## What the next session should know

- **The full suite is not optional, and this run proved it the hard way.** BG0413's first
  delivery left `test_precommit_window_guard` RED on main for six commits. Every one of those
  commits passed the gate, because the gate runs a SELECTED subset that never included it. The
  rule against exactly this shipped one commit later, in BG0422, and was not applied to the work
  beside it.
- **Round 3's finding is the transferable one:** *a repair is behaviourally right on the path it
  was written for, and silently wrong on the path where its helper is absent, broken, or never
  ran.* All three round-3 rejections were that shape - an untested shell half, a preflight that
  never reached the gate, and an `except` that fell through to the fail-open direction.
- **An assertion over the set of every possible value holds nothing.** One shipped test asserted
  `status in {"ok", "refuse", "unevaluated"}` and survived mutation against 5,658 tests.
- **Two criteria read `Verified: yes` over tests that passed while the defect was present.** Both
  re-pointed. Check a verifier can FAIL before ticking the criterion it holds.
- **A ROUND-4 confirmation pass is owed** over the round-3 repairs. The authoring session cannot
  approve its own corrections, and no unit here is signed off.
- **BG0415 AC4 is deliberately unticked.** D0089 records the 380s ceiling as CARRIED, not
  resolved: the gate runs ~450s, and raising the number to meet the measurement is the pattern
  CR0510 was filed about. Carrying is not resolving.
- **The batch was re-cut from 37 units to 9.** 28 were dropped with recorded reasons, never
  started rather than half-built. BG0448 is the deliberate one: gating `Fixed` on an oracle
  rewrites fixtures repo-wide, and ticking 31 criteria across eight terminal bugs without
  re-verifying each fix is the unevidenced claim that bug exists to condemn.
- **The plan was 1.4x measured velocity and delivered 18% of it.** That was flagged at plan time
  and not acted on. Plan to the record, not the appetite.
