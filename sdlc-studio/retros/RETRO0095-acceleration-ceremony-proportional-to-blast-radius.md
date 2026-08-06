# RETRO-0095: Acceleration: ceremony proportional to blast radius

> **Date:** 2026-08-05
> **Batch:** US0638, US0639, BG0495, BG0520, BG0510, BG0525, US0640, US0641, US0642, US0643, US0644, US0645
> **Goal:** The close converges in two rounds, the review costs what the unit's risk deserves, and a run can be signed off without waiting for a human
> **Delivered:** 12 / 12   **Blocked:** 0

## Delivered

- US0638 - the close pre-flight runs the compulsory checklist, the one chain step it never asked about
- US0639 - every gate the close runs is recorded, and a pre-flight verdict cannot be reused by the chain's wider gate
- BG0495 - the velocity row reports what a sprint WROTE beside what was ACCEPTED, and stops calling a zero-idle span working time
- BG0520 - the triage session cap is a per-session budget again rather than a lifetime one
- BG0510 - a plan-review verdict records WHICH pre-code artefact it judged; the gate asks for its own
- BG0525 - US0629 AC2 restated in mechanically decidable terms, before anything was built against it
- US0640 - `plan_review.enabled` decouples the gate from the schema version, through one shared predicate
- US0641 - the review tier is DERIVED from the risk band, RECORDED on the verdict, and READ by the coverage predicate
- US0642 - a low-band unit gets a bounded brief; the claim-inventory pass runs only at full tier
- US0643 - `sprint plan --write` assigns the sign-off panel, making a fully-built path reachable
- US0644 - a sign-off records the capacity it was given in, as a field a filter can read
- US0645 - `sprint_report.py operator-summary`, derived wholly from the ledgers

## Blocked / deferred

- CR0532's reversal window and its tiering of WHO signs by blast radius - stated as deferred in the plan and not attempted. Both compose with CR0510 now that bands are live.
- CR0510's full scope, which supersedes three earlier CRs and would have swamped this batch. What shipped is the slice the plan named.

## What went well

**Naming the mutant before the code changed the outcome, measurably.** RUN-01KZ79C1 shipped five criteria whose AC-named mutants did not kill their tests, because each mutant was written after the code and from the code - so it was the mutant the test was already built to catch. This sprint authored every criterion with its mutant first: 45 mutants applied, 45 killed. Four needed a second attempt, and all four found something real rather than cosmetic.

**The gates caught the author's defects before any reviewer did.** The lane-check named two units whose verifiers never entered the shipped entry point. The full suite caught a `close --dry-run` contract broken by the cost recording, and a test that passed in isolation and failed under the suite because it patched `import config` rather than the module `plan_review` actually imported. The repo-hygiene lane caught two test classes appended below a `__main__` guard. Each of those would have been a review finding on the last run.

**Reading the code before building on a premise stopped three units being wasted.** Slice 2 was planned as a schema v3 migration across 900+ artefacts and turned out to need a config key, because `triage_noise` already had one. CR0532's core turned out to be fully built and merely unreachable. BG0495's filed AC4 asked for a figure to be refused that was already qualified. All three were corrected on the artefact with the reason, rather than delivered against a stale premise.

## What was hard / what stalled

**The full suite is a seven-minute investment and this sprint paid it six times.** The operator raised it mid-sprint and was right: the last five units were batched into one commit for that reason. The gate's own budget lane reported OVER on every commit - 383s, 445s, 392s against a 380s ceiling that has already been raised once from 120s. That is CR0510's headline evidence worsening while CR0510's first slice was being built, and it is the strongest argument for the next slice.

**Nothing built in this sprint was live during this sprint.** The bounded brief, the tier-driven coverage and the panel sign-off all land for the NEXT run. This sprint bought the next one's speed and paid full price itself, which is the honest shape of a wiring sprint and should be said plainly rather than dressed as acceleration already achieved.

**Mutation found four defects that four passing test suites did not.** Every one was a first attempt that looked complete. That is the cost of the discipline and it is worth paying, but it means a unit's first green is not evidence and should not be budgeted as though it were.

## Lessons

- A guard whose deletion changes no behaviour is dead code, however reasonable it reads. This sprint filed exactly that defect against `gate.py:3170` while planning, and then wrote one into `conformance.tier_covers` six hours later; only mutation caught it. Apply the deletion, not the reasoning.
- An absent value and a defaulted one must be distinguishable in the record, or a rule applied later reinterprets history. The tier column reads `-` for absent rather than `full`, and the capacity column never reads `seat` for a row that predates it - in both cases the unsafe direction is a claim nobody made being attributed to somebody.
- Widening a table by INSERTING a column shifts every historical row; appending one does not. Adding `Written` to VELOCITY.md's header alone made the estimate column read back the actual, because the schema is written out three times - header, row writer, reader - with nothing making them agree.
- A sample drawn from the head of a sorted corpus is not a sample of the corpus. Sixty bugs taken by id banded 60 of 60 the same way and reported a working gate as degenerate; the same estimator over a strided sample of the whole corpus returned four distinct bands.
- A fixture that always supplies the thing under test hides the refusal that depends on its absence. Every panel test supplied a brief fingerprint, so the brief-provenance interlock went unpinned until a mutant deleted it and nothing reddened.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro.

- A mechanism that reaches no caller is inert, however well it is tested. This sprint's whole thesis, and it held three times: the risk band, the panel assignment, and `loop_guard budget` which is still uncalled.
- Verify the premise before building on it. Three of this sprint's planned units were re-scoped by reading the code first, one of them from a 900-artefact migration to a config key.
- Name the mutant before the test, and APPLY it. 45 of 45 killed here against 5 survivors on the previous run, and the difference was writing the mutant from the criterion rather than from the code.
- An absence is not an answer: an empty result and an unanswerable question are different facts. UNMEASURED, `-`, and an unrecorded capacity all say so explicitly in the work this sprint shipped.
- A repair breaks its neighbours. Recording the pre-flight's gate cost broke `close --dry-run`'s promise to write nothing, and only the full suite saw it.

## Known issues carried

| Issue | Ruling | Ruled by | Date |
| --- | --- | --- | --- |
| BG0528 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0527 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| CR0533 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| CR0534 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0526 | deferred | Claude Opus 5 (author) | 2026-08-05 |
| CR0511 | not-stop-ship | Claude Opus 5 (author) | 2026-08-05 |
| BG0521 | deferred | Claude Opus 5 (author) | 2026-08-05 |
| BG0522 | deferred | Claude Opus 5 (author) | 2026-08-05 |
| BG0523 | deferred | Claude Opus 5 (author) | 2026-08-05 |
| BG0524 | deferred | Claude Opus 5 (author) | 2026-08-05 |
| BG0457 | deferred | Claude Opus 5 (author) | 2026-08-05 |
| BG0463 | deferred | Claude Opus 5 (author) | 2026-08-05 |
| BG0469 | not-stop-ship | Claude Opus 5 (author) | 2026-08-05 |
| BG0486 | deferred | Claude Opus 5 (author) | 2026-08-05 |
| BG0508 | not-stop-ship | Claude Opus 5 (author) | 2026-08-05 |
| BG0509 | not-stop-ship | Claude Opus 5 (author) | 2026-08-05 |
| BG0512 | deferred | Claude Opus 5 (author) | 2026-08-05 |
| BG0516 | not-stop-ship | Claude Opus 5 (author) | 2026-08-05 |
| BG0519 | deferred | Claude Opus 5 (author) | 2026-08-05 |
| CR0509 | deferred | Claude Opus 5 (author) | 2026-08-05 |
| CR0510 | not-stop-ship | Claude Opus 5 (author) | 2026-08-05 |
| CR0528 | not-stop-ship | Claude Opus 5 (author) | 2026-08-05 |
| CR0529 | deferred | Claude Opus 5 (author) | 2026-08-05 |
| CR0530 | deferred | Claude Opus 5 (author) | 2026-08-05 |
| CR0531 | deferred | Claude Opus 5 (author) | 2026-08-05 |
| CR0532 | not-stop-ship | Claude Opus 5 (author) | 2026-08-05 |

**How these were ruled, since a table of one-word verdicts explains nothing.** `not-stop-ship`
is for a defect whose failure mode is a MISLEADING REPORT rather than wrong behaviour: BG0469
(a close reported as already happened), BG0508 (an import escaping an advisory block), BG0509
(a same-day repair split at day granularity), BG0516 (a refusal reported as unattributable
where the gate named its lane). Each misleads a reader and none of them ships a wrong artefact.

`deferred` is for a defect that is real, understood, and larger than a ruling: BG0457 (four
guards pinning prose to prose), BG0463 (twenty findings behind one id), BG0486 (duplicate
verifiers grouped on a normalised string), BG0512 (batch mutation without the census), BG0519
(unattributed slowdown in the tools leg), BG0526 (`loop_guard budget` has no caller). None is a
judgement that they do not matter; each needs its own unit.

BG0510, BG0520, BG0525 and BG0495 were on this list at the first pre-flight and are not carried:
they were DELIVERED by this sprint and moved to Fixed.

CR0510 and CR0532 are ruled `not-stop-ship` because this sprint delivered their FIRST SLICE and
each stays In Progress by derivation until its remaining children are done - an open parent
whose children shipped is not an unaddressed defect. CR0528 (the installed copy is reconciled
only at a close) is `not-stop-ship` for the same reason it is uncomfortable: this close
forward-ported 15 files, which is the manual act CR0528 exists to remove, and doing it by hand
means the risk it names did not materialise here.

## Estimate vs actual

**Were the estimates any good?** The plan forecast ~3,164,819 tokens for 41 points - a fixed
per-sprint term of 1,377,055 plus 43,604 per point, fitted on 21 whole sprints.

**The before figure this sprint is judged against, stated now rather than remembered later:
RETRO0094 recorded 353,810 tokens per point**, against a recent median near 80,000 and a
planner constant of 25,000 that no row in the last ten came in under. The acceleration claim
is not that this run was cheaper - a wiring sprint pays full price - but that the NEXT run
should be, and that comparison needs a baseline written down before the next run opens.

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US0638 | 3 | 130,812 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0639 | 2 | 87,208 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0495 | 5 | 218,020 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0520 | 2 | 87,208 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0510 | 3 | 130,812 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0525 | 2 | 87,208 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0640 | 2 | 87,208 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0641 | 8 | 348,832 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0642 | 5 | 218,020 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0643 | 5 | 218,020 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0644 | 2 | 87,208 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0645 | 2 | 87,208 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 12 unit(s) measured; 12 of 12 forecast at plan time.**
Unmeasured: US0638, US0639, BG0495, BG0520, BG0510, BG0525, US0640, US0641, US0642, US0643, US0644, US0645. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- The forecast's own calibration record says est/actual 0.44x out of sample on one sprint: the model under-prices, and this sprint's points were sized against a 34-point appetite the plan's own slices summed to 41. Read the points as relative sizing, not as a cost forecast.

## Actions raised

| Finding | Disposition |
| --- | --- |
| The plan's headline appetite (~34 points) contradicted its own slice arithmetic (41) | declined: corrected at plan time and delivered in full; the sizing note now states the real number |
| `conformance.tier_covers` carried an unreachable guard clause | fixed-in: 8f95263e |
| `close --dry-run`'s write-nothing contract broken by the pre-flight cost record | fixed-in: 238e830d |
| A test patched `import config` rather than the module `plan_review` imported, passing in isolation and failing under the suite | fixed-in: c725a53 |
| Two test classes appended below a `__main__` guard, silently dropped on a direct run | fixed-in: 8f95263e |
| VELOCITY.md's schema is enumerated three times with nothing making the three agree | fixed-in: 238e830d (header/writer pinned; the reader is still a third enumeration) |
| `loop_guard budget` still has no programmatic caller | BG0526 |
| The commit gate is over its 380s budget on every selected run of this sprint | declined: it is CR0510's own evidence and belongs in CR0510's next slice, not in a fresh finding |

<!-- file one with: scripts/file_finding.py · check with: scripts/retro.py dispose --id RETROxxxx -->

## Close loop (gated)

- [ ] this retro exists AND passes its content check
- [ ] its lessons are in the project store, not just in this file
- [ ] open lessons re-validated
- [ ] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons

## Metrics

- Tokens: captured at close from the harness meter · Duration: see the run state · Critic rejects: 0 recorded (the adversarial pass is owed)
