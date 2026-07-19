# RETRO-0055: The delivery backlog is empty and the close-owed debt is cleared: every writer, gate and test the skill ships is honest about what it covers

> **Date:** 2026-07-19
> **Batch:** BG0202, BG0203, BG0206, BG0207, BG0209, BG0211
> **Goal:** The delivery backlog is empty and the close-owed debt is cleared: every writer, gate and test the skill ships is honest about what it covers.
> **Delivered:** 6 / 6   **Blocked:** 0

## Delivered

Run RUN-01KXX52Z, 11 points over six bugs, plus a debt-clearing phase that preceded them.

**Phase 1 - the close-owed debt (no product change).** `close_owed detect` reported 9 units owed.
Three distinct causes, cleared three ways rather than stamped: RETRO-0053 reconstructs the
persona-layer sprint of 2026-07-16, which shipped in one commit and was never closed; RETRO-0054
reconstructs the CR0322 `refine --into` sprint of 2026-07-17, which ran a full two-role close -
review, repair round, re-verification, operator sign-off - and produced no retro artefact; and
BG0201, fixed in-run during RUN-01KXVYGR and discussed twice in RETRO-0051's prose, was added to
that retro's `Batch` line so the machine can see what the narrative already said. Both new retros
are marked RECONSTRUCTED and contribute nothing to estimator calibration, because no plan-time
forecast was recorded and the harness totals are not retrievable days later.

**Phase 2 - the six bugs.**

- **BG0202** (2 pts) - the confinement roster sweep sees `path.open(mode)`. The mode index now
  follows the call form. Five modules gained a previously invisible append surface, all already
  covered by another route: the detector was blind, the roster was not wrong. The bug named one.
- **BG0206** (1 pt) - a test module importing a sibling helper runs under both forms. 154 tests now
  run under the form that previously produced one `ModuleNotFoundError`. The guard is the point:
  a sweep imports every such module in its own interpreter.
- **BG0209** (2 pts) - the shipped suite passes from an installed copy. Measured both ways from a
  simulated install: 7 errors before, 7 clean skips after, dev repo still running all 144. The
  dev-repo rule now has one definition instead of a copy per module.
- **BG0207** (2 pts) - the RFC accept gate names every open decision. The fail-closed re-scan fired
  only on an empty read, so a fence hiding later rows produced an incomplete list reported as
  complete. Safe by construction: the unstructured read is a strict superset.
- **BG0203** (2 pts) - the audit profile parser's not-found paths are pinned. **The filed premise
  was wrong** and the real defect was better. See below.
- **BG0211** (2 pts) - a dead breakdown id no longer owes a close no close can give, and the cause
  is reported rather than silently forgiven.

Suite **3,208 green** after the review repairs (3,203 at first close, plus five tests added in the
two review rounds), drift 0, every commit through the full gate. Delivery backlog: 1 (BG0212,
filed by this run).

## Blocked / deferred

- None blocked. **BG0212** was filed rather than fixed: 14 mutation survivors elsewhere in
  `audit.py`, outside BG0203's stated scope. Absorbing them would have made a 2-point bug into
  something else.
- Phase 3 (CR0361 and CR0358, both requested) is not started. It needs a refine into epics and
  stories before any code, and the grooming sits on top of the points.

## What went well

- **Two bugs were falsified by running them, not by reading them.** BG0203 claimed two mutation
  survivors in the audit profile parser; hand-mutating both kills them, so the finding does not
  reproduce. BG0211 claimed zero epics were affected on this repo; there are 33 dead ids. In both
  cases the investigation found something more useful than the filed claim.
- **Sequencing paid off.** BG0206 (sibling-module imports) was fixed before BG0209, whose fix wanted
  a new shared helper imported the same way - so BG0209 built on a sound import and BG0206's new
  sweep immediately policed it. Picking that order was luck as much as judgement, but the
  interaction was visible before either was started.
- **Every fix was measured against the real system, not just the fixtures.** BG0202's effect on the
  actual roster (five modules, not one), BG0209 from a simulated install both ways, BG0211's live
  repo answer and runtime. Three of those measurements contradicted what I expected.
- **The gates earned their keep on the author again.** The style guard caught a provenance tag in a
  consuming-facing file; markdownlint caught MD028 and then MD024, the second because I had opened a
  duplicate `### Fixed` under `[Unreleased]` rather than using the one already there; `transition`
  refused two bugs that carried no verification depth. Every refusal was correct.

## What was hard / what stalled

- **I reproduced BG0203's own methodological error before spotting it.** Scoping a mutation run's
  test command below its target's real coverage manufactures survivors: one test file reports 10
  for `audit.py`, that module's actual tests report 4, same code and same mutants. I did this,
  believed the 10, and only caught it by widening the command. That is exactly how BG0203 got
  filed. **A narrow test command does not under-report coverage, it over-reports absence.**
- **My first anti-vacuity sweep was itself vacuous.** BG0206's guard imports every sibling-importing
  module by name. The first version imported all 13 in ONE interpreter and PASSED against the
  unfixed tree, because the first module to run its own `sys.path.insert` fixes the path for every
  module after it. A guard written to enforce "a test that passes for an incidental reason is not
  coverage" passed for an incidental reason.
- **Mutation found a false claim in prose I had just written.** BG0209's shared helper docstring
  called both halves of the dev-repo check load-bearing. Dropping the second half survived the
  entire 197-test gate suite. The docstring was right about the design and wrong about the
  evidence - the same defect class the previous run kept producing, and I produced it again.
- **The first cut of BG0211 regressed the detector 6.3s to 15.8s**, and its first advisory fired 33
  lines on every run to describe records that change no answer - reintroducing the skim-past
  failure BG0210 was filed for, in advisory form. Both were caught by running it on the real repo
  rather than the fixtures.
- **I left dead code behind while fixing dead code.** Inlining BG0211's logic made
  `_derived_from_covered_children` unreferenced, an hour after deleting `PROFILE_DIR` from
  `audit.py` for being exactly that. The review then found `delivery_ids`, dead on arrival in
  the very commit whose message says so.
- **The review REJECTed, and the MAJOR was in the guard written to prevent that class of
  defect.** BG0206's sweep was blind to `test_telemetry`, a module in its own directory, on two
  independent layers: the census matched `ast.Import` only, so `from gitutil import git` was
  invisible; and fixing the census alone would not have closed it, because that import sits
  inside a method and so does not run at import time. The sweep now imports each module AND
  resolves the helpers it references.
- **Round 2 found three more, every one created by the round-1 repair.** The mode-shape gate I
  added was necessary but its `break` lost `open('rt', 'w')` - a write reported as no write
  surface, the same failure class as BG0202 itself. **The helper-resolution line that closed the
  MAJOR was itself unpinned**: deleting it left the whole suite green, silently reopening the
  hole - which is the exact defect I had caught in my own BG0209 work one commit earlier. And my
  correction of an overclaim from "five" to a precise count was off by one; it is six.

## Lessons

- **A narrow test command over-reports absence.** A mutation run scoped below its target's real
  coverage manufactures survivors, which then get filed as bugs. Widen the command to the module's
  actual tests before believing a survivor, and record the test command beside the result.
- **A sweep that checks many things in one process can be satisfied by the first one.** Shared
  interpreter state - `sys.path`, `sys.modules`, caches - makes later cases pass on the back of
  earlier ones. Isolate per case, or the sweep proves nothing about all but the first.
- **A finding is a hypothesis, not a fact.** Two of six bugs in this batch were wrong in their
  specifics and both were worth more once investigated. Reproduce before fixing, and correct the
  record when the premise falls.
- **Forgiving an unsatisfiable demand must surface its cause.** Dropping a dead id silently would
  trade a false debt for a hidden defect; reporting it unconditionally would restore the noise the
  forgiveness existed to remove. Scope the report to the cases where the forgiveness changed the
  answer.
- **A new guard needs a test of its MECHANISM, not just of the case that prompted it.** The line
  that closed this review's MAJOR could be deleted with 3,205 tests still green. A guard is code,
  it rots like code, and "the suite is green" says nothing about a guard nothing exercises. Write
  the fixture that makes it fire.
- **Round 2's findings are made by round 1's repair, and this is now three runs in a row.** Every
  new finding this round was created by the previous round's fix, twice inside the very lines
  written to fix the previous finding. Treat a repair as new code needing its own adversarial
  pass, never as the closing of a loop.

## Estimate vs actual

**Were the estimates any good?** The plan forecast a token cost per unit; telemetry recorded
what each one actually cost. This section holds the comparison, so the question is asked every
sprint instead of only when someone remembers to ask it.

Generate it: `scripts/retro.py accuracy --id RETROxxxx --write` - it fills the block below from
the batch's telemetry and appends this sprint's row to `retros/VELOCITY.md`.

A unit with no per-unit telemetry record has its PER-UNIT ratio reported as **UNMEASURED** and
excluded from that ratio - it is never counted as accurate. But the token count itself is NOT
unmeasurable: the harness tracks it deterministically. An INTERACTIVE sprint (no runner) records no
per-unit actual, so supply the harness-tracked sprint total with `accuracy --tokens N` to get a
real sprint tokens-per-point over the delivered points - report it as **not-yet-captured** until you
do, never as if the number were unknowable. That figure is DESCRIPTIVE, never a target (see CR0273).

The forecast is a hypothesis, not a settled calibration. Read the ratio, write down what it
implies, and change the constants only on evidence a human has looked at - a fit to a couple of
sprints fits noise.

<!-- accuracy:begin (generated by retro.py accuracy --write) -->
<!-- accuracy:end -->

- The plan forecast ~275,000 tokens for 11 points at the seed rate of 25,000 per point. The sprint
  total is harness-tracked and **not-yet-captured** here: run `accuracy --tokens N` with the figure
  to close the loop (CR0278 is the standing gap). What can be said without it: the two falsified
  bugs, BG0203 and BG0211, cost multiples of their 2 points, because investigating a wrong premise
  and then correcting the record is work the points do not model. **Points size the diff, not the
  discovery** (L-0111), and this batch is a clean example - the smallest-sounding bugs were the
  expensive ones.

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
| 14 mutation survivors in `audit.py` outside the profile parser | BG0212 - filed, deliberately not absorbed into a 2-point bug |
| A mutation run scoped below its target's coverage manufactures survivors, and nothing warns | **CR0363** - filed. This produced BG0203 and I repeated it; the gate should report the coverage its test command actually reaches |
| BG0203's filed premise was wrong; both named survivors were already pinned | declined: no NEW work is owed - it was fixed in-run, and BG0203 carries a Resolution section stating the falsification. See the CR0362 row below: "declined" is the wrong word for this and the vocabulary is the reason |
| BG0211's "zero epics are in this state" was wrong; there are 33 | declined: no new work owed - established in-run and used to scope the advisory. Same vocabulary problem as the row above |
| A finding FIXED during the sprint has no honest disposition: `retro validate` accepts only an id or `declined:`, so in-run repairs must be recorded as declined | CR0362 - already open, and hit live twice in this retro. The two rows above are not declined in any ordinary sense; they were fixed. Confirms the CR from a second run |
| The closing review took two rounds and every round-2 finding was created by the round-1 repair - the third consecutive run with that shape, and nothing in the process detects it | CR0358 - already open and unbuilt; this run is its third piece of evidence. The repair-regression detector it specifies would have flagged two of the three round-2 findings, both of which landed inside the lines written to fix a round-1 finding |
| A new guard can ship with its mechanism untested: the line closing the review's MAJOR was deletable with 3,205 tests green | declined: fixed in-run by `ProbeMechanismTests`, which exercises the probe against real fixtures. The general habit is now a lesson rather than a ticket |
| Two bugs still lacked a `Verification depth` field and were refused by `transition` | declined: the gate caught both and the cost was one field each. The refusal is the feature working |
| A retro reconstructed days later cannot supply estimate-versus-actual | declined: correctly excluded rather than guessed. The general gap is CR0278, already open |
| Interactive sprint tokens are still not captured, so this retro's own accuracy block is empty | declined: CR0278 covers it and is unchanged by this run |

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

- Tokens: not-yet-captured (harness-tracked; supply with `accuracy --tokens N`). The two review
  rounds cost ~113k and ~141k subagent tokens, which the point-based forecast does not model at
  all · Duration: one interactive session · Critic rejects: 1 (REJECT at round 1 on a MAJOR, APPROVE
  at round 2 with three new MINORs, all repaired)

## Handoff

- [HO-0011](../handoffs/HO0011-the-delivery-backlog-is-empty-and-every-writer.md) - 0 remaining item(s): 0 copilot-tail, 0 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
