# RETRO-0105: four close-ceremony defects, three of them found by reviews that rejected the first cut

> **Date:** 2026-08-18
> **Batch:** BG0585, BG0584, BG0589, BG0590
> **Goal:** four groomed bugs from SC0006 delivered under a build rung, with BG0592's outstanding review rounds carried alongside
> **Delivered:** 4 / 4   **Blocked:** 0

## Delivered

- BG0585 - the `derived-only` grooming limb could not see its own writer, so it had been reachable by nothing for twelve days. `criteria_block` gained the `**ACn**` marker two days after the detector shipped and nothing re-ran the detector against it, so every criterion the tool itself emits read as authored - the placeholder that reads like content passed every gate in the repository.
- BG0584 - the sprint checklist's tick-verification row asked every run the build rung's question, which a `design` rung cannot answer, only waive. It asks what a design rung actually owes now, and D0145 retracts the waiver so the repair is observable.
- BG0589 - one fact had two answers: the pre-flight headline counted the blocker LIST in one renderer and the HELD rows in its sibling, so an operator was told the close was twice as far away as it was.
- BG0590 - `sprint close` wrote a hardcoded dash bullet into the retro, so it exited 0 and then left the tree refused by the repo's own markdown lane. Both bullet appenders now follow the document.

## Blocked / deferred

- BG0592 - not in this batch, carried from the previous run and repaired alongside it. REJECTED four times and ESCALATED twice. Every rejection after the first was a defect in the repair, not in the original diagnosis.
- Reviewer-of-record sign-off is OWED for all four units. `critic signoff` refuses a principal the authoring session controls, which is the gate working.

## What went well

- The review model earned its cost outright. Five seats over six rounds; the code was found correct almost every time and the EVIDENCE was not. A reviewer made the detector return True unconditionally - census 17 bugs to 364, 0 stories to 669 - and the criterion pinning it still passed.
- Driving every claim through the shipped entry point kept finding wiring nothing else could see. A criterion naming `sprint.py plan` was verified by a test running `breakdown`, which is read-only and exits 0, so no refusal was ever asserted.
- The gates refused correctly and repeatedly: `suite-claim` caught a verdict taken before edits twice, the release selection guard refused deselecting a bound lane, the duplicate-burndown guard refused two criteria sharing one verifier, and `critic record` escalated both non-converging repairs without being asked.

## What was hard / what stalled

- Repairs kept breaking their neighbours. BG0592's round-2 repair reintroduced the false green it indicts; BG0590's round-1 repair regressed a case its own docstring claimed to handle. Two of the four rejections were of repairs, not of original work.
- Numbers I wrote down were wrong more often than the code was. The gate baseline, the census, the mutant counts, the retro bullet style - each was stated, reviewed, corrected, and in two cases the CORRECTION was wrong too.
- The mutation record was prose until late in the run. Hand-rolling the runs and writing the outcome into `Verification depth` produced a claim no reader could check, and two reviewers found it false where they re-ran it.

## Lessons

- A detector's SILENCE is evidence only once it has been shown able to speak. The markdownlint helper caught a missing binary and not a missing package, so it handed `npm ERR! 404` to an `assertNotIn` and four criteria's lint half was inert in any clone without `npm ci` - while both its docstring and the depth field said "skipped, never faked". Prove the tool detects the thing on a known-bad input before trusting a clean result.
- A fixture that makes the mutant equivalent is the commonest way a test measures nothing here. Three instances this run: a census test whose repo root resolved to `.claude/` so its glob matched nothing; a thematic-break test whose fixture put the real list ahead of the break; and a green-figure test whose every story had `manual=0`, hiding a numerator that counted manual criteria as green.
- A false premise RESTATED is worse than the original, because each restatement reads as verification. "Every retro carries asterisks" was corrected once to blame the generator - also false - before measurement gave 102 dash and 3 asterisk of 105.
- Scope a rung fix to the rung it is about, never to "not `done`". Done twice now: BG0582's siblings were rejected for it at their round two, the correct ruling was written into `sprint.py` twice, and BG0584 made the same mistake again with those comments in the file.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- A repair is judged more harshly than the code it repairs: two of four rejections this run were of repairs.
- An enumerated list silently exempts what it forgot - three markers where CommonMark has three, two of four return paths, one appender of two.
- Register mutants AFTER the last edit, or the ledger drops them when the file changes under it.
- Verify the premise before building on it, and re-measure before restating it.
- A test whose fixture makes the mutant equivalent proves nothing, however green it reads.

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
| BG0592 | not-stop-ship | authoring session | 2026-08-19 |
| BG0593 | not-stop-ship | authoring session | 2026-08-19 |
| BG0594 | not-stop-ship | authoring session | 2026-08-19 |
| BG0595 | not-stop-ship | authoring session | 2026-08-19 |
| BG0596 | not-stop-ship | authoring session | 2026-08-19 |
| CR0511 | not-stop-ship | authoring session | 2026-08-19 |
| CR0535 | not-stop-ship | authoring session | 2026-08-19 |
| BG0463 | not-stop-ship | authoring session | 2026-08-19 |
| BG0490 | not-stop-ship | authoring session | 2026-08-19 |
| BG0493 | not-stop-ship | authoring session | 2026-08-19 |
| BG0567 | not-stop-ship | authoring session | 2026-08-19 |
| BG0578 | not-stop-ship | authoring session | 2026-08-19 |
| BG0581 | not-stop-ship | authoring session | 2026-08-19 |
| BG0586 | not-stop-ship | authoring session | 2026-08-19 |
| BG0587 | not-stop-ship | authoring session | 2026-08-19 |
| BG0588 | not-stop-ship | authoring session | 2026-08-19 |
| BG0591 | not-stop-ship | authoring session | 2026-08-19 |
| CR0496 | not-stop-ship | authoring session | 2026-08-19 |
| CR0497 | not-stop-ship | authoring session | 2026-08-19 |
| CR0499 | not-stop-ship | authoring session | 2026-08-19 |
| CR0503 | not-stop-ship | authoring session | 2026-08-19 |
| CR0504 | not-stop-ship | authoring session | 2026-08-19 |
| CR0507 | not-stop-ship | authoring session | 2026-08-19 |
| CR0509 | not-stop-ship | authoring session | 2026-08-19 |
| CR0523 | not-stop-ship | authoring session | 2026-08-19 |
| CR0524 | not-stop-ship | authoring session | 2026-08-19 |
| CR0528 | not-stop-ship | authoring session | 2026-08-19 |
| CR0529 | not-stop-ship | authoring session | 2026-08-19 |
| CR0530 | not-stop-ship | authoring session | 2026-08-19 |
| CR0531 | not-stop-ship | authoring session | 2026-08-19 |
| CR0533 | not-stop-ship | authoring session | 2026-08-19 |
| CR0534 | not-stop-ship | authoring session | 2026-08-19 |
| CR0536 | not-stop-ship | authoring session | 2026-08-19 |
| CR0539 | not-stop-ship | authoring session | 2026-08-19 |
| CR0540 | not-stop-ship | authoring session | 2026-08-19 |
| CR0543 | not-stop-ship | authoring session | 2026-08-19 |
| CR0544 | not-stop-ship | authoring session | 2026-08-19 |
| CR0545 | not-stop-ship | authoring session | 2026-08-19 |
| CR0546 | not-stop-ship | authoring session | 2026-08-19 |

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

- The four units were sized 1-2 points each and the FIXING matched that. The ceremony did not: six review rounds, four repair cycles and 39 mutants across five units. The points measured the diff and missed the review loop, which is where the run's cost actually went - the same conclusion the plan for this programme reached before it started, now measured rather than forecast.

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
| `verify_ac._testplan_rows` keys by criterion, so a second mutant on the same AC is silently dropped and `--from-plan` reports every one killed over rows it never joined | BG0596 |
| The commit-msg hook test runs the real hook against the real repository, so the full suite goes red whenever work is in flight | BG0595 |
| `artifact._wire_story_to_epic` locates its insertion point with a hardcoded dash, so an asterisk epic takes the rebuild path the adjacent comment exists to avoid | CR0511 |
| The gate budget is a scalar against a bimodal population - narrow commits ~212s, wide ~540s, ceiling 380s between them, so it is wrong about both | BG0594 |
| `_close_recorded_transition` canonicalises against the extended vocab then tests module-constant terminals, the same recognised-then-excluded shape as BG0592's defect | declined: it fails CLOSED, so the carve-out is refused rather than granted, and it predates this diff |
| The corpus red-criteria baseline did not reproduce for an independent reviewer - 27 measured against 20, six from a missing devDependency and one unexplained | fixed-in: 369d217f - recorded in BG0592's own history as owed re-measurement in a clone with `npm ci` |

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

- Tokens: captured by the close · Duration: captured by the close · Critic rejects: 6 across 5 units (BG0592 ×4, BG0590 ×2, BG0584 ×1, BG0585 ×1), 2 escalations
