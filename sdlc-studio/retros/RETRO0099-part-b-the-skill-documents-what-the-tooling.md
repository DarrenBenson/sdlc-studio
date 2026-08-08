# RETRO-0099: Part B: the skill documents what the tooling ships

> **Date:** 2026-08-08
> **Batch:** US0652, US0653, US0654, US0655, US0656, US0657, US0658, US0659
> **Goal:** the skill documents what the tooling ships - CR0538 / EP0211, Part B of RUN-01KZF9AF
> **Delivered:** 8 / 8   **Blocked:** 0

## Delivered

- US0652 - `scripts/lib/surface.py`: one enumeration of the shipped command surface, walking
  subparsers AND positional `choices`, NAMING what it cannot read rather than skipping it. The
  bare `continue` it replaced made `_all_parsers()` report a count of whatever happened to load.
- US0653 - `scripts/docgen.py surface`: the verb catalogue is generated between markers, and a
  file without them is refused. Flags stay off the page by design; `--format json` carries them.
- US0654 - `command_audit.py --coverage`: 132 of 257 verbs carry an invocable form. Measured
  against HAND-WRITTEN markdown only - the generated targets and every fenced generated block
  are excluded, or the page lists all 257 and the gap vanishes with nothing improved.
- US0655 - the number reaches the three places people already look: an advisory `doc-surface`
  lane in `gate.py`, `npm run lint` (which `lint:disclosure` joined at the same time), and a
  FIGURE row in the close report.
- US0656 - `help/references.md` is walked from the filesystem, each row carrying the
  reference's own first descriptive paragraph.
- US0657 - `check_budgets.py --record` and `--drift`. The hard threshold is unchanged; the three
  unbudgeted trees get a reported total rather than a ceiling that fails on day one.
- US0658 - a generated Reading Guide with LINE SPANS on all 26 references over 400 lines, so an
  agent can `Read(offset, limit)` instead of grepping. It REPLACES the three hand-written ones.
- US0659 - SKILL.md carries `## See Also`, trigger phrases and four loading rows, at 293 of 500
  lines; `disclosure.py` reports the measured nesting depth - 3 hops, 99 reachable files.

## Blocked / deferred

- Nothing was blocked. The plan predicted `disclosure.py` would fall 28 -> 24 findings; it reads
  54 both before and after, because the plan-time figure was taken over a different root. No
  criterion depended on it, and saying so costs less than quietly dropping the claim.

## What went well

- The load-bearing risk held. `--coverage` reads 132/257 with the exclusions on and 257/257
  with both off, asserted in both directions through the command - so the projection trap the
  plan named as the one finding that would make this CR a lie is shut, and provably.
- Every generator is idempotent to a fixed point. The Reading Guide reports line spans and
  occupies lines, so a single pass emits spans true of the file before the guide existed; the
  iteration is what makes the second run report zero drift instead of 26.
- The adversarial delivery review earned its place: 4 APPROVE, 4 REJECT, and each rejection was
  a real defect this session had already satisfied itself was fine.

## What was hard / what stalled

- Three of the four rejections were one failure wearing three faces: a criterion whose test
  could not fail on what the criterion claimed. US0658 asserted a guide was PRESENT while three
  files carried TWO; US0656's description test ran on a two-file fixture while seven real rows
  shipped markup; US0652's delegation test passed on an empty sweep. All green from the day they
  were written, so no run could have surfaced them.
- `--record` rewriting its own source line-wise over the WHOLE file was found by a reviewer
  putting a ceiling-shaped line in a docstring and watching the tool corrupt it. The sibling
  function twenty lines below already scoped correctly, so it was an oversight, not a decision.

## Lessons

- A criterion is only as good as the mutant its test can fail on. Three of this sprint's four
  rejections were tests asserting a WEAKER claim than the criterion above them - present rather
  than exactly-one, a synthetic fixture rather than the corpus, an equality an empty result also
  satisfies. All were green from the day they were written, so no run could have surfaced them;
  only reading each test back against its criterion did.
- Drive the claim through the COMMAND and it finds wiring the suite cannot see. Adding one
  CLI-driving verifier per unit, to satisfy an advisory lane check, found that `docgen.py
  references` and `surface` threaded `--root` to the file they wrote but not to the content they
  read, and that `nesting_depth` had zero callers. A 6348-test green suite held both.
- A tool whose blast radius is its own source must be scoped to the literal it rewrites. The
  demonstration cost nothing - a ceiling-shaped line in a docstring - and the failure mode is
  silent corruption of the file that decides what every budget is.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- A mechanism that reaches no caller is inert, however well it is tested. Carried from
  RETRO0098 and paid again here: `nesting_depth` had zero non-test callers.
- Name the mutant before writing the test, and check the mutant is one the criterion cares
  about. This sprint's dearest lesson.
- A repair breaks its neighbours. Bounding the hand-guide stripper by the next heading deleted
  the document when the guide was the last section - found only because a new test looked.
- An enumerated exemption list silently covers what nobody re-read. `ROOT_GRAMMAR_DEBT` was
  silencing two conformance families those twelve scripts already passed.
- Verify the premise before building on it. The plan's 28 -> 24 disclosure figure was measured
  over a root the sprint never used.

## Known issues carried

Every finding this sprint leaves OPEN, with the ruling somebody made on it. This is the one
compulsory close item the tree cannot derive: whether an open defect stops the ship is a
judgement, so it is recorded here and the sprint checklist reads it back. An open finding
with no row is reported as UNRULED, because "we carried it" and "nobody looked" must never
read the same.

Ruling is one of `stop-ship`, `not-stop-ship`, `accepted-risk`, `deferred`. A `stop-ship`
ruling HOLDS the close, which is the point of being able to make one.

**The basis for these rulings, stated once rather than repeated 47 times.** Nothing ships out
of this run: D0130 holds the tag, so no release carries any of these to a consumer. Every one
is a finding this repo raised about its own tooling, none is in EP0211's declared `Affects`,
and none was touched by the eight units. A `stop-ship` ruling exists to hold a release; with no
release to hold, `not-stop-ship` is the true answer rather than the convenient one - and the
next run that DOES cut a tag has to make this judgement again, against the release it is cutting.

Three of these were raised BY this sprint and are the ones worth reading first: CR0539
(lane-check names 181 units and blocks none), BG0556 (no guard catches a decorative `--root`)
and BG0555 (the twelve scripts carrying root-grammar debt).

| Issue | Ruling | Ruled by | Date |
| --- | --- | --- | --- |
| BG0457 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0463 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0469 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0486 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0508 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0509 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0512 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0519 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0522 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0523 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0526 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0528 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0529 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0531 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0532 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0534 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0535 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0536 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0537 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0538 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0539 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0540 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0542 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0543 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0544 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0545 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0546 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0547 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0548 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0549 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0550 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0551 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0552 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0553 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0554 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0555 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| BG0556 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| CR0509 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| CR0528 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| CR0529 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| CR0530 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| CR0531 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| CR0533 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| CR0534 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| CR0535 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| CR0536 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |
| CR0539 | not-stop-ship | sdlc-studio-authoring-session | 2026-08-08 |

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
| US0652 | 5 | 222,135 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0653 | 5 | 222,135 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0654 | 5 | 222,135 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0655 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0656 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0657 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0658 | 5 | 222,135 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0659 | 2 | 88,854 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 8 unit(s) measured; 8 of 8 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes, by phase - read from the two verdict ledgers:

  test-plan review: 16 pass(es) over 8 unit(s), 7 rejected

  code review: 12 pass(es) over 8 unit(s), 4 rejected

  ratio: 0.75 code-review pass(es) per test-plan pass - the claim EP0207 is judged on, as a number
Unmeasured: US0652, US0653, US0654, US0655, US0656, US0657, US0658, US0659. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- 31 points planned across 8 units, 8 delivered. The estimate missed the repair round entirely:
  the four rejections and six majors cost roughly a third of the build again, and none of it was
  in the forecast. A points figure that prices only the first pass is not pricing the unit.

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
| lane-check names 181 units whose criteria never enter their own command, and blocks none | CR0539 |
| No guard catches a `--root` that selects the file written but not the content read | BG0556 |
| `--record` rewrote a ceiling-shaped line inside a docstring | fixed-in: US0657, scoped to the ALLOWLIST literal |
| Three references carried TWO Reading Guides, the generated table listing its rival as a row | fixed-in: US0658 |
| Seven reference rows shipped markup as their description | fixed-in: US0656 |
| `disclosure.py` carried a verbatim duplicate of four helpers and a shadowing `_skill_dir` | fixed-in: US0659 |
| `docgen.py --root` was decorative for two verbs | fixed-in: US0656 |
| The surface cache keyed on a path STRING, so a relative dir re-executed 71 modules | fixed-in: US0652 |
| `ROOT_GRAMMAR_DEBT` silenced two conformance families those scripts already passed | fixed-in: US0652 |
| Coverage matched a bare substring, so `autosprint.py plan` satisfied `sprint.py plan` | fixed-in: US0654 |
| A `doc-surface` lane that could not measure reported count 0, which renders as perfect | fixed-in: US0655 |
| The plan's predicted 28 -> 24 disclosure drop did not occur | declined: the plan-time figure was taken over a different root, and no criterion depended on it |

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

- Tokens: captured at close by `accuracy --tokens-from-harness` · Duration: one interactive
  session · Critic rejects: 4 of 8 at delivery (US0656, US0657, US0658, US0659), all repaired
  and re-verified; 35 of 35 criteria pass and the full suite is green.

## Handoff

- [HO-0056](../handoffs/HO0056-the-skill-can-measure-what-it-fails-to.md) - 0 remaining item(s): 0 copilot-tail, 0 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
