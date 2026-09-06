# RETRO-0113: RUN-01M1NS3C: six gates that hold in the command people run

> **Date:** 2026-09-04
> **Batch:** BG0643, BG0603, BG0640, BG0644, BG0647, BG0641, BG0650, BG0642
> **Goal:** Six gates that hold in the command people run, not only on the page: `git push` runs the boundary gate and refuses over a red main until acknowledged; the commit hook holds a selection to the sum of its modules' noise budgets; the verify lint refuses a stacked verifier at every non-terminal status; the filer accepts the not-yet-written test and refuses the typo it can name; the revert-check lane that examined nothing says so. Verdict: achieved (goal-verdict, 2026-09-04)
> **Delivered:** 8 / 8   **Blocked:** 0

## Delivered

- BG0643 (5 pts, ee11bd3b) - `file_finding.py file --verify` accepts a class its test file does not collect and a new method no method in that class is close to, and refuses the same-leaf and in-class near-miss typos; three tests re-authored, BG0570 AC1 and US0667 AC1 re-worded.
- BG0603 (2 pts, d31383b5) - `verify_ac.py lint --ratchet --bugs` refuses a stacked verifier at every non-terminal status, stories and bugs alike.
- BG0640 (2 pts, 77e40b35) - the revert-check lane that examined nothing says so and says why, and a crash still leads.
- BG0644 (5 pts, ba715bd2) - the noise ratchet is a per-module budget file: a selection is held to the sum of its modules' entries, a full run to `_total`, an unrecorded module contributes zero, and `budget-check` refuses a raised entry before the suite.
- BG0647 (2 pts, a77af6de + 652e451b) - the status integration test gathers a fixture, never this repository; added in flight because its 12 ledger warnings refused every docs-only commit on this clone.
- BG0641 (5 pts, 0da43495) - a tracked `.githooks/pre-push` binds `gate.py --boundary push|release`, announces its cost first and records it after, behind the commit hooks' scrub, with the gate's output on stderr; `enable-hooks.sh` names every hook; `tools/boundary_roster.py` refuses a boundary AGENTS.md names with no invocation behind it; D0180 is the cost ruling.
- BG0650 (1 pt, 835c48f9) - the depth-count census reads the deriver's total, not the entry-point denominator; added in flight when BG0641, the first artefact with a manual criterion and a derived field, refused every commit through the tools suite.
- BG0642 (3 pts, 14a9d4d6) - the hook reads the latest push-triggered Lint run on main before the gate and refuses on any non-success until the run id is acknowledged and remembered per clone; unreadable or empty is named, never green; D0181 is the practice ruling.

## Blocked / deferred

- BG0637, BG0638 - on the operator's list, refused by the planner with zero Verify lines; wait on grooming.
- BG0642 AC5 (manual) - the branch-protection edit removing the never-satisfiable `ci` check is the operator's after D0181; read back today it still carries the check.

## What went well

- Plan review before code: three rounds killed four fixtures that could not reach their branch before a line was written, and every delivery-round rejection afterwards was a real gap, not paperwork.
- The seats found what my own checks could not: a budget calibrated on this clone's transient state, a gate whose lane name never reached the stream git shows a pusher, a fixture that reached the real `gh`, a crash test with a one-unit batch, an enable-hooks fixture writing hook config into a foreign repository.
- Every friction became an artefact in the same session: BG0645-BG0650 filed, three Lows into CR0511, two rulings recorded as decisions before code.

## What was hard / what stalled

- Ceremony dominated wall-clock: 12-15 minute commit hooks (14 launches for 9 commits, four refused on paperwork lanes), the mutation ledger dropping registrations on every byte change (LL0053 bit BG0644, BG0647, BG0641 and BG0643 in one day), verdict and closure syntax refusals, and reviewers' pytest caches breaking the rehearsal lane inside a commit hook twice.
- Two units needed three review rounds (BG0643, BG0641) and two needed two; 12 REJECTs across 36 seat verdicts, every one earned by execution.
- The disclosure page and the v5.0.1 count moved with every status change and refused three commits until regenerated last.

## Lessons

- A hook's stdout never reaches the pusher: git shows a pre-push hook's stderr only, so a refusal that says "see the lane named above" must put the lane on stderr, and a fixture that merges the streams cannot tell (BG0641 engineering r1, proved under a real `git push`).
- A depth field carries two counts, the total after the word and the entry-point denominator before it; a census that takes the first `<n> criteria` reads the wrong one, and the first artefact with a manual criterion exposes it (BG0650).
- Register mutation evidence after the LAST edit to a target, and re-check every earlier unit whose target a later unit touches: BG0641's thirty rows were dropped by BG0642's edit to the same hook, and BG0643's two by BG0603's edit to verify_ac.py, both found only at the close dry-run.
- A test fixture that inherits the caller's environment is a defect even when green: an unscrubbed enable-hooks fixture wrote `core.hooksPath` into a decoy repository, and an unscrubbed PATH reached the live forge (BG0641 qa r1, BG0642 qa/engineering r1).
- The disclosure page is derived from statuses: regenerate it once, after the last transition, or every commit in between is refused by its own paperwork.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- Register mutation evidence after the last edit, and re-check every unit whose target a later unit touched (LL0053, bitten four times in this run).
- Run the Givens, not the words: a fixture that cannot reach its branch is found by executing it, never by re-reading it (plan review r2 of this run).
- A test that inherits the caller's environment or PATH is a defect while green: scrub every fixture the way the shipped script scrubs.
- One stream for the pusher: what a hook wants read must be on stderr, and a test that merges streams pins nothing about which stream carried it.
- Regenerate derived pages once, after the last state change; a derived page refreshed mid-run refuses the commits that follow it.

## Known issues carried

Every finding this sprint leaves OPEN, with the ruling somebody made on it. This is the one
compulsory close item the tree cannot derive: whether an open defect stops the ship is a
judgement, so it is recorded here and the sprint checklist reads it back. An open finding
with no row is reported as UNRULED, because "we carried it" and "nobody looked" must never
read the same.

Ruling is one of `stop-ship`, `not-stop-ship`, `accepted-risk`, `deferred`. A `stop-ship`
ruling HOLDS the close, which is the point of being able to make one.

| Issue | Ruling | Ruled by | Date |
| --- | --- | --- | --- |
| BG0645 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, rejoinder briefs ignore the plan-review phase; workaround in use | 2026-09-04 |
| BG0646 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, status.py takes 113 s on this corpus; BG0647 removed it from the suite's path | 2026-09-04 |
| BG0648 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, a criterion outside its section is executed but not reviewed; the batch's artefacts were checked by hand | 2026-09-04 |
| BG0649 | not-stop-ship | delivery session (Claude), for the operator's confirmation at sign-off - Medium, test_critic red alone; discovery order hides it and the selected-run lanes now expose it | 2026-09-04 |
| BG0651 | not-stop-ship | operator, delegated in session on 2026-09-06 - Medium, the evidence-drift gate filed at this close and groomed into the D0182 batch; the drop it guards was caught by the close dry-run this run and re-measured | 2026-09-06 |
| BG0567 | not-stop-ship | delivery session (Claude) under D0136-D0139 (Medium ships disclosed against v5.1), for the operator's confirmation at sign-off - the upgrading-project baseline compares against this tree minus one branch, not against th | 2026-09-04 |
| BG0591 | not-stop-ship | delivery session (Claude) under D0136-D0139 (Medium ships disclosed against v5.1), for the operator's confirmation at sign-off - status and close_owed give opposite answers about the same units | 2026-09-04 |
| BG0601 | not-stop-ship | delivery session (Claude) under D0136-D0139 (Medium ships disclosed against v5.1), for the operator's confirmation at sign-off - The dry-run class sweep compares only the first two probes of each pair | 2026-09-04 |
| BG0608 | not-stop-ship | delivery session (Claude) under D0136-D0139 (Medium ships disclosed against v5.1), for the operator's confirmation at sign-off - The budget line still LEADS with the seconds comparison BG0594 proved uninformative, so th | 2026-09-04 |
| BG0612 | not-stop-ship | delivery session (Claude) under D0136-D0139 (Medium ships disclosed against v5.1), for the operator's confirmation at sign-off - Three limbs that survived the closure of BG0599 and BG0602: an edit-verb gap, an unpinned | 2026-09-04 |
| BG0614 | not-stop-ship | delivery session (Claude) under D0136-D0139 (Medium ships disclosed against v5.1), for the operator's confirmation at sign-off - the mutation ledger keeps several LIVE rows on one (unit, criterion, row) key, and the joi | 2026-09-04 |
| BG0627 | not-stop-ship | delivery session (Claude) under D0136-D0139 (Medium ships disclosed against v5.1), for the operator's confirmation at sign-off - eleven other fields-file consumers carry the same `or ""` guard, so a falsey value is repo | 2026-09-04 |
| BG0630 | not-stop-ship | delivery session (Claude) under D0136-D0139 (Medium ships disclosed against v5.1), for the operator's confirmation at sign-off - the test-plan gate is skipped on In Progress to Done, so a unit that entered before its re | 2026-09-04 |
| BG0633 | not-stop-ship | delivery session (Claude) under D0136-D0139 (Medium ships disclosed against v5.1), for the operator's confirmation at sign-off - transition.py annotate is a THIRD writer of Severity and carries no vocabulary, so the cla | 2026-09-04 |
| BG0637 | not-stop-ship | delivery session (Claude) under D0136-D0139 (Medium ships disclosed against v5.1), for the operator's confirmation at sign-off - critic._clean escapes underscores INSIDE code spans, corrupting 655 identifiers across the | 2026-09-04 |
| BG0638 | not-stop-ship | delivery session (Claude) under D0136-D0139 (Medium ships disclosed against v5.1), for the operator's confirmation at sign-off - five sprint-checklist rows state a conclusion they never established, and _ck_known_issues | 2026-09-04 |
| CR0509 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0528 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0529 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0530 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0531 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0533 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0534 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0535 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0536 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0539 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0546 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0547 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0548 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0550 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0551 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0552 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0553 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0554 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0555 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0556 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0557 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0558 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0559 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0560 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0561 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0562 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |
| CR0563 | deferred | delivery session (Claude), for the operator's confirmation at sign-off - a request, not a defect; not decomposed into this run - | 2026-09-04 |

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

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BG0643 | 3 | 113,661 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0603 | 2 | 75,774 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0640 | 2 | 75,774 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0644 | 3 | 113,661 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0647 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0641 | 3 | 113,661 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0650 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0642 | 2 | 75,774 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 8 unit(s) measured; 6 of 8 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes, by phase - read from the two verdict ledgers:

  test-plan review: 58 pass(es) over 7 unit(s), 26 rejected

  code review: 36 pass(es) over 8 unit(s), 12 rejected

  ratio: 0.62 code-review pass(es) per test-plan pass - the claim EP0207 is judged on, as a number
Unmeasured: BG0643, BG0603, BG0640, BG0644, BG0641, BG0642. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: BG0647, BG0650. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- The forecast was 2,748,068 tokens for 25 points at plan time (~110k per point); the harness delta is captured at close. Read against RUN-01M0CT8P's 525k per point, the ratio will say whether three-round reviews on two units moved this run to the same order; the estimate missed BG0647 and BG0650 entirely because neither existed at plan time.

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?**

This is the question that turns a retro into work. Every finding gets a disposition:
**file it** (a BG/CR id), **record it fixed in-sprint** (`fixed-in: <sha or unit>`), or
**decline it with a reason**. All three are green. What does not pass is silence - a
finding written down and left to rot. The three are counted separately at close: a sprint
that repaired eleven findings reads as eleven fixed, not eleven declined.

To say "nothing worth raising", say so in a row and give the reason. An empty table is
not an answer.

All three accepted dispositions are shown below, filled in rather than described - the
vocabulary is exact and a refusal is a poor place to meet it for the first time. Replace
every EXAMPLE row; a row left in place is reported at the close, and a retro still carrying EVERY demonstration line this template ships is REFUSED by it.

| Finding | Disposition |
| --- | --- |
| test_config gathered the real repository and printed this clone's ledger state into the noise count | BG0647 |
| the depth-count census read the entry-point denominator and refused BG0641's commits | BG0650 |
| test_critic uses unittest.mock without importing it and is red when run alone | BG0649 |
| rejoinder briefs ignore --phase plan-review | BG0645 |
| status.py takes 113 s on this corpus | BG0646 |
| a criterion appended outside the Acceptance Criteria section is executed but never reviewed | BG0648 |
| the pre-push hook records a refused run's duration and seeds the estimate towards zero | CR0511 (Low) |
| five depth fields carry a hand-written count after the derived span the census cannot see | CR0511 (Low) |
| the hook's gh read has no time bound and coreutils timeout is not on the four-tool PATH | CR0511 (Low) |
| shellcheck SC2086 on tools/skill-tests.sh:83, no gate runs shellcheck | declined: pre-existing at the base ref, nothing runs shellcheck and the variable is a word list by design |
| test_repo_hygiene reported red when run alone by a seat | declined: does not reproduce at ba715bd2, the module passes alone |
| the BG0644 engineering r1 seat's claim that import-time leaks explain the 120-versus-106 gap | fixed-in: ba715bd2 |
| AC3 of BG0647 asserted one of two warning sites | fixed-in: 652e451b |
| the gate's stdout never reached the pusher's stream | fixed-in: 0da43495 |
| a fixture reached the real gh through an inherited PATH | fixed-in: 14a9d4d6 |

<!-- file one with: scripts/file_finding.py · check with: scripts/retro.py dispose --id RETRO0113 -->

## Close loop (gated)

`gate --require-retro RETRO0113` (this retro's id, file form) fails until all four are true:

- [ ] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETRO0113`)
- [ ] its lessons are in the project store, not just in this file (`retro.py extract --id RETRO0113`)
- [ ] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [ ] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: captured at close from the harness delta (baseline 2,175,154 at 08:51:57Z) · Duration: 08:51Z to close, one session · Critic rejects: 12 of 36 seat verdicts (BG0643 3, BG0641 3, BG0642 2, BG0644 2, BG0603 1, BG0647 1)
