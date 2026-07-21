# RETRO-0065: This project can plan and judge a sprint on its own recent measured evidence, and every guard reaches the code it claims to cover

> **Date:** 2026-07-21
> **Batch:** BG0244, BG0246, BG0242, BG0245, BG0240, BG0241, BG0243
> **Goal:** This project can plan and judge a sprint on its own recent measured evidence, and every guard reaches the code it claims to cover.
> **Delivered:** 7 / 7   **Blocked:** 0

## Delivered

7 units, 18 points (BG0242 re-sized 3 -> 5 before starting, from a census rather than a summary).

**Evidence the planner and close rely on**

- BG0246 (2) - `batch_history` gated on per-unit telemetry, so every interactive sprint was
  dropped and "what sprints ACTUALLY cost" showed the OLDEST rows while hiding RETRO0060 at
  265,625 tokens/unit. Now included, each row labelled per-unit or sprint-level, with the
  hidden-variance cost printed beside them rather than left in the decision record.
- BG0245 (3) - the mutation ledger could only be written by `mutation.py` while the practice is
  hand-applied mutants, so a policy-following sprint read 0/N. `register` records one, and
  provenance stops a self-report posing as a measurement.
- BG0244 (2) - `Actual (tokens)` was a sum over rated units, publishing an absence as zero. 7 rows
  printed `actual= 0` before; 0 do now, and the reader guard means the correction survives the
  ceremony that previously overwrote it.
- BG0243 (2) - the token delta could be stamped on an unrelated retro. The retro id is now
  required, and the coverage rule was EXTRACTED from the elapsed path rather than copied.

**Guards that did not reach**

- BG0242 (5) - 35 unconfined git call sites confined, proven by victim repo rather than asserted:
  5 of 8 modules damaged the victim at HEAD, three wiping its uncommitted state; none afterwards.
- BG0241 (2) - a spec with no AC Coverage Matrix reported clean; now exits 1, distinct from
  complete (0) and absent (2), with the migration cost measured before the default changed.
- BG0240 (2) - two writers anchored on the cwd, plus a third found in the same file and fixed with
  them, because fixing only the filed two would have made the inconsistency worse.

## Blocked / deferred

- None. No unit was quarantined and the loop guard never fired.
- BG0248 (where the measured rate should be measured FROM) is deliberately not answered here. It
  is the question D0047 did not rule on, and inventing an answer mid-build is what the decisions
  log exists to prevent.

## What went well

- **Asking before building paid for itself three times.** The operator ruled on three design forks
  before any code was written (D0047-D0049). D0048's ruling carried a constraint the author would
  have missed - that a registered mutant is SELF-REPORTED and must never read as a measurement -
  and that constraint drove most of BG0245's implementation.
- **D0049 sent me to count before building, and counting changed the plan.** BG0242 was re-sized
  3 -> 5 on a real census, and the census exposed a trap: `test_sprint` imports `subprocess as
  _sp`, so the obvious grep finds only 24 of 35 sites. An agent sweeping with the natural pattern
  would have reported done with a third of the hole open. That warning went into the bug and the
  implementing agent confirmed it independently.
- **BG0242's evidence is the best this project has produced.** Containment was proven, not
  asserted: a fresh victim repo per module with a deliberately diverging worktree, showing 5 of 8
  modules damaging it at HEAD and none afterwards. The agent's FIRST attempt used a victim whose
  worktree matched its index - a trap that cannot spring - and it said so and rebuilt it.
- **Agents refused to fix things quietly.** The evidence agent found that D0047's rationale was
  wrong about the rate counter, declined to make the counter move to match the prose, measured the
  real cause, and recommended filing it separately. That is the behaviour the decisions log is for.
- **Three surviving mutants were found and each drove a second fix**, two of them the L-0159
  unreachable-guard class again. None was dismissed as equivalent without argument, and the one
  genuinely equivalent mutant was reported as such rather than quietly dropped.
- **The noise ratchet went DOWN**, 132 -> 129, because leaks were captured rather than tolerated.

## What was hard / what stalled

- **The author wrote a false claim into a bug about numeric honesty, and then into a decision of
  record.** BG0246's summary and D0047's rationale both asserted that `batch_history`'s filter was
  what stalled the measured-rate counter. It is not: they read different sources. The claim was
  never checked before being written twice. Caught independently by the implementing agent and by
  the author before review, corrected in D0050 and filed as BG0248 - but it is the fifth
  consecutive sprint in which prose asserted something the code does not do.
- **A gate passed a commit that was non-compliant the instant it existed.** The engagement floor
  derives "shipped" from `git log --grep`, so a unit no commit has mentioned is invisible. The
  floor read 0 violations, the pre-commit gate passed, the commit landed, and the same check
  immediately reported 2 new violations in files nothing had touched. Filed as BG0251.
- **Fixing one column revealed its twin, unfixed.** BG0244 taught `Actual (tokens)` to render an
  absence honestly; the `Estimate` column beside it has the identical defect in 12 of 17 rows.
  Found by the agent doing BG0244, reported rather than swept in, filed as BG0249.
- **The sibling sweep keeps growing.** BG0240's two root-anchoring fixes triggered a sweep that
  found 20 more scripts with the same shape, 10 of them driving writes - including `next_id.py`,
  where the consequence is not a stray file but a MINTED COLLIDING ID. CR0383 now carries that
  census. Three sprints have each fixed two or three instances of one missing convention.

## Lessons

- **Two numbers that look related can come from different sources, and "obviously connected" is
  not evidence.** The measured-rate counter and the plan's cost history both describe what sprints
  cost, so it was assumed fixing one moved the other. They read different logs. The assumption was
  written into a bug and a decision before anyone ran it.
- **A gate whose input is derived from history cannot judge the commit that creates the history.**
  The engagement floor reads `git log --grep`, so a pre-commit run is blind to the units the
  pending commit will ship. A PASS meant "nothing already shipped violates", while everyone read it
  as "this commit is compliant".
- **Count before sizing, and count with a pattern that survives an alias.** A naive
  `subprocess.run(["git"` grep found 24 of 35 sites because one module aliases the import. The
  sweep would have reported done with a third of the hole open.
- **Prove containment against a fixture that can actually fail.** The first victim repo had a
  worktree matching its index, so `git add -A` was a no-op and the hash survived the damage. A
  containment proof needs a victim with something to lose.
- **Fixing a column obliges you to look at the one beside it.** `Actual` and `Estimate` are written
  by the same code in the same row from the same wrong source; fixing one and shipping without
  reporting the other would have left a defect the fix had just proved exists.
- **A self-report is not a measurement, and a ledger that cannot tell them apart is worse than one
  that holds neither.** Recording provenance was the constraint that made BG0245 safe rather than a
  quiet downgrade of every entry in the ledger.
- **A fix that rescues the value can leave the reason with the original defect.** BG0244 taught
  the velocity row to preserve a measured `actual_tokens` across a re-record, and left the Note
  column - created specifically to explain a blank - regenerated unconditionally. The bug it was
  filed to end was "the correction was overwritten by the ceremony that rewrote the row", and that
  is still true of the reason. Fixing half a row is not fixing the row.
- **Check the incentive a new reporting path creates, not just its correctness.** Registering a
  SURVIVED mutant moves a file from "no evidence" to "covered" while the survivor itself is never
  displayed, so reporting bad news makes the gate quieter than reporting nothing. A mechanism that
  rewards silence will get silence.
- **Do not diagnose from a diff taken while another process is mid-edit.** A transient mutation
  window looked exactly like a reviewer failing to restore two units' work, and was announced as
  such before being checked. The file was identical to HEAD moments later. Verify the current
  state, then describe it - the same order this project keeps failing to use.
- **Check what a measurement EXCLUDES before drawing a conclusion from it.** The first
  attributable token figure this project ever produced was 2.2% from the seed rate, which reads as
  a textbook validation. It excluded every delegated agent, and the true rate is about 2.7x the
  seed. The conclusion was drawn first and the exclusion checked second.
- **A number that looks like a successful measurement is more dangerous than an obvious absence.**
  Three closes reported not-attributable and everyone knew where they stood. The first close to
  report a figure was the first at risk of being believed.
- **An operator ruling before the build is cheaper than a review rejection after it.** Three forks
  were ruled in advance; one of the rulings carried a constraint the author had not seen, and it
  shaped the implementation rather than being discovered as a defect.

## Estimate vs actual

**Were the estimates any good?** The plan forecast a token cost per unit; telemetry recorded
what each one actually cost. This section holds the comparison, so the question is asked every
sprint instead of only when someone remembers to ask it.

Generate it: `scripts/retro.py accuracy --id RETROxxxx --write` - it fills the block below from
the batch's telemetry and appends this sprint's row to `retros/VELOCITY.md`.

A unit with no per-unit telemetry record has its PER-UNIT ratio reported as **UNMEASURED** and
excluded from that ratio - it is never counted as accurate. But the token count itself is NOT
unmeasurable: the harness tracks it deterministically. An INTERACTIVE sprint (no runner) records no
per-unit actual, so the close captures this RUN's share of the harness-tracked total itself
(`accuracy --tokens-from-harness`, run by `sprint close --apply-signoff`) and the velocity row
records it. The meter is per-SESSION and cumulative, so what is captured is the delta from the
baseline stamped when the run opened - not the session total, which in a session holding more than
one sprint counts the earlier ones again. A run with no baseline (opened before the baseline
existed, or closed from a different session) reports **not-attributable** rather than a number:
there is no fallback to the raw total, because a plausible-looking figure that is not this sprint's
cost is worse than an absent one. When the capture cannot attribute, the close states why and
`accuracy --tokens N` remains the manual override.
Report it as **not-yet-captured** only while neither has happened, never as if the number were
unknowable. That figure is DESCRIPTIVE, never a target (see CR0273).

The forecast is a hypothesis, not a settled calibration. Read the ratio, write down what it
implies, and change the constants only on evidence a human has looked at - a fit to a couple of
sprints fits noise.

<!-- accuracy:begin (generated by retro.py accuracy --write) -->
<!-- accuracy:end -->

- **This is the first sprint opened WITH a session-token baseline**, and it did produce an
  attributable delta: 439,982 tokens. That is the previous sprint's work paying off, and it is
  also where this sprint found its sharpest defect.
- **The number is wrong by a factor of nearly three, and it looks right.** The capture sums the
  session transcript, which carries ZERO sidechain records, so every delegated agent is invisible.
  The four cluster agents spent 787,834 between them and the closing review is uncounted, so the
  known true cost is at least 1,227,816 - a 64% understatement, published under a label reading
  "the run's own spend". Filed as BG0252.
- **The false reading was nearly reported as a success.** At 18 points, 439,982 gives 24,443
  tokens per point against a 25,000 seed: 2.2% under, which reads as a textbook validation of the
  estimator. The true rate is at least 68,212 per point, about 2.7x the seed. The calibration was
  computed and only then checked against the transcript's sidechain records, which is the wrong
  order and is recorded here as such.
- The forecast recorded at plan time was ~400,000 tokens for 16 points. BG0242 was then re-sized
  3 -> 5, and the forecast was deliberately NOT re-priced: first-record-wins, so the retro judges
  the number the plan actually made. The estimate should therefore read low by roughly 2 points'
  worth, and that is the honest result rather than a tidied one.
- Per-unit ratios stay UNMEASURED: no unit carries per-unit telemetry, which is BG0248's subject.

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?**

This is the question that turns a retro into work. Every finding gets a disposition:
**file it**, or **decline it with a reason**. Both are green. What does not pass is
silence - a finding written down and left to rot.

To say "nothing worth raising", say so in a row and give the reason. An empty table is
not an answer.

| Finding | Disposition |
| --- | --- |
| BG0244's Note column is destroyed by the next `accuracy --write` on its OWN row, reproducing the defect BG0244 was filed to end (review MAJOR 1) | BG0244 - repaired in round 2, in the unit it was raised against |
| After the documented `--tokens 0` retraction the Note asserts "no sprint total was supplied" (review MAJOR 2) | BG0244 - repaired in round 2 |
| A self-reported `survived` verdict is write-only, so registering bad news makes the gate QUIETER than registering nothing (review MAJOR 3) | BG0245 - repaired in round 2 |
| `_store_ledger`'s docstring claims a bound it does not provide for `register` (review MINOR 4) | BG0245 - repaired in round 2 |
| `batch_history` admits hand-typed `--tokens N` totals with no provenance mark (review MINOR 5) | BG0246 - repaired in round 2 |
| The reviewer overwrote live source via a symlink farm plus a shell redirect, reverting two delivered units before restoring them | LL0039 (global lesson) |
| `git add -A` during the closing review staged a file the reviewer had a mutant applied to; the gate refused it only because that mutant broke tests, so a SURVIVING mutant would have been committed silently | CR0388 |
| The token capture counts only the main thread, so this sprint published 439,982 against a known true cost of at least 1,227,816 - a 64% understatement labelled as the run's own spend | BG0252 |
| The measured rate can never advance under interactive sprints, and BG0246's summary plus D0047's rationale were WRONG about why | BG0248, and the rationale corrected in D0050 |
| The velocity `Estimate` column has BG0244's defect exactly, in 12 of 17 live rows | BG0249 |
| `quality.epic_requires_test_spec` is documented as an opt-out but is read by no code | BG0250 |
| The engagement floor cannot see a violation the gating commit itself creates | BG0251 |
| `batch_history` showed the oldest measured sprints as the current cost picture | BG0246, fixed in this sprint |
| The WSJF advisory reported the AGE of scores covering none of the batch, so `--order wsjf` had silently been priority ordering | BG0247 |
| The run-opened line prints `goal=unset` on the command that just set the Sprint Goal | CR0387 |
| The handoff line tells you to plan a worklist containing zero items | CR0386 |
| 20 further scripts resolve `--root` without discovery, 10 driving writes, worst being `next_id.py` minting COLLIDING ids from a subdirectory | CR0383, census added this sprint |
| `reference-sprint.md` and the scripts catalogue do not document the new `register` subcommand | CR0385 covers the mutation docs; the `register` gap is added to its scope |
| Pre-existing stdout noise in `test_sprint` and `test_gate` from `main(--format json)` calls that do not redirect | declined: pre-existing, unrelated to this batch, and the ratchet already bounds it. Filing it would not change what anyone does before the ratchet next rises |
| Modules still fail under a polluted environment because the redirection lands in the script under test, not the fixture | declined: already declared debt in `SCRUB_SITES` as PARTIAL scrubs in `gate.py` and `lessons.py`; BG0242 measured the improvement (test_sprint 48 to 8 failures) rather than claiming the class closed |
| 215 units are grandfathered under the engagement floor's `adopt_after` | declined: pre-existing, forward-only by design, and unchanged by this sprint |
| One genuinely equivalent mutant in BG0243 (deleting one of three mentions of the retro id) | declined: the asserted property still holds with two mentions, so it is equivalent rather than a coverage gap. Deleting every mention IS killed |

<!-- file one with: scripts/file_finding.py · check with: scripts/retro.py dispose --id RETROxxxx -->

## Close loop (gated)

`gate --require-retro RETROxxxx` (this retro's id, file form) fails until all four are true:

- [ ] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETROxxxx`)
- [ ] its lessons are in the project store, not just in this file (`retro.py extract --id RETROxxxx`)
- [ ] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [ ] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: {{tokens}} · Duration: {{duration}} · Critic rejects: {{rejects}}
