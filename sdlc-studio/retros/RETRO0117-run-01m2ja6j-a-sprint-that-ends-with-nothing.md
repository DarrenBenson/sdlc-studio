# RETRO-0117: RUN-01M2JA6J: a sprint that ends with nothing unanswered - 23 units, the stop-ship rule, and the coverage gate's attribution

> **Date:** 2026-09-15
> **Batch:** US0625, US0626, US0627, US0628, US0823, BG0659, BG0661, BG0662, BG0664, BG0665, BG0666, BG0667, BG0668, BG0669, BG0670, BG0671, BG0672, BG0673, BG0674, BG0675, BG0676, BG0677, BG0678
> **Goal:** Nothing is left open silently: the sixteen bugs open at planning (BG0659, BG0661, BG0662, BG0664-BG0676) reach Fixed on their own verifiers; a corpus-verify run dispatched on the commit BG0676 closes on - delivered last, carrying the whole batch - passes against a baseline measured in CI; and a run can no longer end silently over an unanswered unit or an unanswered REJECT (D0193, D0194, D0196)
> **Delivered:** 22 / 23   **Blocked:** 0

## Delivered

- US0625 - the doctrine states CR0526's rule: a non-stop-ship finding becomes its own artefact and its unit closes pointing at it; a stop-ship ruling lives in one store, the retro's Known issues carried table, and the operator rules it (D0194)
- US0626 - an unfinished batch unit holds the close through its stop-ship step and names where its findings went; Review and rung-end units do not (two delivery rounds)
- US0627 - no story or bug reaches Done or Fixed over an unanswered REJECT unless its findings are filed or the REJECT is repaired; abandoned units are no longer fanned to Done (two delivery rounds)
- US0628 - a unit closed over a REJECT names, in its own record, the artefact its findings were filed to
- US0823 - stop, file-and-close, the boundary stop and the handoff read the same unanswered-unit predicate as the close, and `stop --force` records what it waived
- BG0659 - a code span ending in a space can be recorded in the review ledgers without markdownlint refusing the row
- BG0661 - revert-check names the units it set aside, and their count survives once one unit is examined
- BG0662 - `changelog.py shape` checks a fragment's shape at commit time, not first at the release cut
- BG0664 - the pre-push boundary gate runs the boundary-only tests, and its refusal's re-run line carries the marker
- BG0665 - every `review.*` setting is declared in the file that calls itself the single source of truth
- BG0666 - an unauthored Test Plan row no longer buys a clean derive; derive and the plan-review brief name unauthored mutants
- BG0667 - the root-effect control's real-tree marker is no longer bound to an id range the project had outgrown
- BG0668 - tag-check reads the close-owed predicate's units half, so it no longer refuses a close that predicate says is not owed
- BG0669 - a story retired unbuilt owes `decomposed` alone; the six waivers D0187-D0192 are withdrawn (D0198-D0203, confirmed as D0205)
- BG0670 - `config.py show` prints a config holding an unquoted YAML date
- BG0671 - the brief-practice and claim-pass checks are called by `critic.py brief`, as reference-review.md says
- BG0672 - `critic record` refuses a `--brief` fingerprint no brief produced
- BG0673 - the repair-plan gate is wired: plans and verdicts are recorded by command, and turning the gate on refuses what it should
- BG0674 - `sprint next` leaves a charter's discovery items out of the batch it materialises and says so
- BG0675 - an author-declared Points value no longer sets a unit's review tier; the corpus tier shift is recorded in a frame
- BG0677 - `critic.py repair` closes a finding whose text carries the closure separator (added to the run by the operator)
- BG0678 - the repair-plan gate keeps rounds, the brief and the approval pin (added to the run by the operator)
- BG0676 - the corpus-verify lane installs coverage, reads full history and gives verifiers time; its CI baseline re-measure and verified dispatch are the last step

## Blocked / deferred

- None blocked. BG0676 is delivered last by design: AC4 and AC5 need a CI run on the pushed commit that carries the whole batch, which only the operator can dispatch.

## What went well

- The delivery review discriminated. 48 delivery verdicts, 44 APPROVE and 4 REJECT, and all four REJECTs were real: US0626's parked no-artefact regression and US0627's abandoned-unit close stop were both regressions the authors' own suites passed, and both repairs were confirmed CLOSED in round two by both seats.
- One stakeholder consult, run only because the operator asked, found the batch's largest design gap: nothing checks who wrote a stop-ship ruling, so the session that did the work can release its own hold (CR0571). Seventy plan-review verdicts had not raised it. It cost one agent pass and produced RFC0058.
- Splitting the omnibus commit into per-group commits (A to L) turned 455 foreign lines charged to BG0674 into zero, and every unit's coverage gate then measured its own lines.
- Every open review finding reached an id before the close: 25 drafts filed as BG0690-BG0706 and CR0579-CR0583, three Lows folded into CR0511, and each repair record cites them.

## What was hard / what stalled

- Plan review took 70 verdicts, 47 of them REJECT, before a line of code: BG0667 was rejected five times and BG0671 four. The rounds converged on criteria wording rather than defects, which is why D0204 now caps plan review at three rounds and CR0578 will encode it.
- Hash-bound evidence voided repeatedly. Every edit to a shared file (critic.py, sprint.py, test_critic.py) dropped other units' mutant rows and coverage rulings: 99 mutant rows re-registered with anchors across four evidence-drift refusals, and 24 coverage lines re-ruled at the close.
- The triage caps held twice: the run's cap of 20 findings stopped RFC0058 and CR0578, and the operator's session cap stopped the close filings after 21 of 25, because a Low folded into CR0511 counts as a filing.
- The harness killed background suite waiters under a memory limit that real memory never reached, and 45 stale review worktrees (1.9 GB) slowed the suites until removed.
- The push gate outlasts the harness, so every push and every CI dispatch is the operator's, and BG0676's last two criteria wait on them.

## Lessons

- **Attribution by blame turns one commit into a shared charge.** The coverage gate charged all 455 of US0626's added sprint.py lines to BG0674, because both units declare the file and one omnibus commit carried both. Split into per-group commits, the charge fell to BG0674's own lines. Commit per unit, or per group whose Affects files are disjoint, before any gate that attributes lines by `git blame` and the `Refs:` trailer runs. Filed as BG0706.
- **Seats judge the build against the author's criteria; only a stakeholder judges the criteria against the need.** Seventy plan-review verdicts approved a stop-ship rule that the session doing the work could release itself. One stakeholder consult found it in a single pass (CR0571). If the criteria encode the wrong intent, every seat approves a well-built wrong thing. Consult before freezing the design (RFC0058).
- **An uncapped review loop converges on wording, not defects.** Plan review ran to five rounds on one unit and drew 47 REJECTs. Delivery review, capped at two rounds (D0146), drew four REJECTs, and all four were real regressions. A cap plus a complete written repair is cheaper than a sixth round (D0204).
- **Evidence hashed against whole-file bytes is voided by a neighbour's edit, not just your own.** Mutant rows and coverage rulings on critic.py and sprint.py were voided by other units' commits four times this run (LL0053's shape, now crossing units). Register and rule after the last edit ANY unit makes to a shared file, and re-run every unit's done-gate dry-run after the final code commit.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- Commit per unit, or per file-disjoint group, when units share a file: blame-based attribution charges an omnibus commit to every unit that declares the file.
- Both evidence ledgers are hashed against whole-file bytes: register and rule after the LAST edit any unit makes to a shared file, then re-run every unit's dry-run.
- Consult the stakeholders before freezing a design: the seats check the build against the criteria, and only a stakeholder checks the criteria against the need.
- A criterion's words are law and its fixture is the measurement; when they differ the fixture wins silently, and the criterion reads as met.
- Two readers of one rule will disagree, and the one that blocks is the one nobody tested.

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
| BG0679 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0680 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0681 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0682 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0683 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0684 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0685 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0686 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0687 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0688 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0689 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0690 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0691 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0692 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0693 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0694 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0695 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0696 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0697 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0698 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0699 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0700 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0701 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0702 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0703 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0704 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0705 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0706 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0509 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0528 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0529 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0530 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0531 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0533 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0534 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0535 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0536 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0539 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0546 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0547 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0548 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0550 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0551 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0552 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0553 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0554 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0555 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0556 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0557 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0558 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0559 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0560 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0561 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0562 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0563 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0565 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0566 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0567 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0571 | not-stop-ship | Darren Benson (operator, ruled by name at the close review: carried at High; this close works around it by having every row here ruled by the operator, none by the authoring session) | 2026-09-15 |
| CR0572 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0573 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0574 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0576 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0577 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0578 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0579 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0580 | not-stop-ship | Darren Benson (operator, D0206: the refusal is ruled and carried as this CR; no run this sprint used the side door) | 2026-09-15 |
| CR0581 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0582 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| CR0583 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) | 2026-09-15 |
| BG0707 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) - AC4's own dispatch settles the provenance this guard cannot | 2026-09-16 |
| BG0708 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) - the coupling is more permissive in CI, so it cannot redden a run today | 2026-09-16 |
| BG0709 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) - the stale row was refused rather than acknowledged, so nothing false was banked | 2026-09-16 |
| CR0584 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) - the test-cost work this run's measurements argue for, deferred to refine | 2026-09-16 |
| CR0585 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) - deferred to refine; the cap it would retire is raised to 150 in the meantime | 2026-09-16 |
| CR0586 | not-stop-ship | Darren Benson (operator, RUN-01M2JA6J close review: not-stop-ship for every carried item; row drafted by the authoring session) - deferred to refine; the full sweep still runs at every push until then | 2026-09-16 |

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
| US0625 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0626 | 5 | 222,135 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0627 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0628 | 2 | 88,854 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0823 | 3 | 158,571 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0659 | 3 | 158,571 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0661 | 2 | 105,714 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0662 | 2 | 105,714 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0664 | 3 | 158,571 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0665 | 3 | 158,571 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0666 | 2 | 105,714 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0667 | 2 | 105,714 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0668 | 2 | 105,714 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0669 | 2 | 105,714 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0670 | 2 | 105,714 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0671 | 3 | 158,571 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0672 | 3 | 158,571 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0673 | 5 | 264,285 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0674 | 3 | 158,571 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0675 | 3 | 158,571 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0676 | 5 | 264,285 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0677 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0678 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 23 unit(s) measured; 21 of 23 forecast at plan time.**

**Sprint tokens/point: 62,715** (6,459,675 tokens over 103 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity: 3.94 points/elapsed-hour** (103 points ACCEPTED over 26.159h, run-state - a CALENDAR SPAN with no idle deducted, since the run recorded no gap; it is not working time, ceremony included). This is the planning number - points per SESSION within the observed single-session envelope; it is NOT a linear per-point rate to extrapolate to a 1-point or 100-point sprint, and it is descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes, by phase - read from the two verdict ledgers:

  test-plan review: 70 pass(es) over 23 unit(s), 47 rejected

  code review: 58 pass(es) over 23 unit(s), 10 rejected

  ratio: 0.83 code-review pass(es) per test-plan pass - the claim EP0207 is judged on, as a number
Unmeasured: US0625, US0626, US0627, US0628, US0823, BG0659, BG0661, BG0662, BG0664, BG0665, BG0666, BG0667, BG0668, BG0669, BG0670, BG0671, BG0672, BG0673, BG0674, BG0675, BG0676. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: BG0677, BG0678. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- Interactive run: no per-unit actuals were captured, so the per-unit ratio is UNMEASURED; the run's token share is captured from the harness at the close. The plan-review rounds (70 verdicts) are the cost the forecast did not price, which is what D0204's cap addresses.

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
| US0626 round one: a parked batch unit with no artefact on disk was held (regression) | fixed-in: ef5b29e8 |
| US0626 round one: the drop-then-re-add and named-retro clauses had no test that could fail | fixed-in: ef5b29e8 |
| US0627 round one: standing_rejects copied the supersession rule; an abandoned unit carrying a REJECT stopped the close (regression) | fixed-in: 4e780dcb |
| BG0664: the refusal's re-run line lacked the boundary-suite marker | fixed-in: ef5b29e8 |
| BG0669: the vocabulary claim in conformance.py and its fragment over-stated the retired set | fixed-in: ef5b29e8 |
| The omnibus commit charged 455 foreign lines to BG0674 through blame attribution | fixed-in: eeb39384 |
| Blame-based coverage attribution and whole-file-hash rulings charge and void across units | BG0706 |
| critic.py repair re-judges stored findings through the code-span guard | BG0690 |
| changelog.py shape judges unreadable and symlinked fragments differently in its two modes | BG0691 |
| gate.py never sets the boundary-suite marker itself | BG0692 |
| testplan derive and the plan-review brief still name different unauthored sets | BG0693 |
| tag-check's tests pin the override case, not the blocking predicate | BG0694 |
| conformance's ungroomed nudge counts retired skeletons | BG0695 |
| critic.py's brief checks search the whole brief; a no-brief REJECT can never be retired | BG0696 |
| The repair-plan gate fails open on a zero-finding plan, bad config and an unreadable round | BG0697 |
| Repair-plan rounds can be overwritten by concurrent records | BG0698 |
| sprint queue show's not-materialised line is unpinned; the discovery partition is held in three copies | BG0699 |
| The doctrine stop-ship guard passes inverted sentences | BG0700 |
| Run-ending routes still read different sets (stop's two derivations, the boundary stop's --retro) | BG0701 |
| The unanswered set's ways out are picked by substring and rendered in drifting copies | BG0702 |
| The unanswered-set predicate's fail-closed handlers survive mutants no test kills | BG0703 |
| The Done guard reads a filed closure naming the unit itself as a repair | BG0704 |
| The Findings-filed-to line survives a reopen and names only the filed subset | BG0705 |
| Low review findings on BG0665, BG0667 and BG0675 (test pinning, control reach, disclosure) | CR0511 |
| revert-check's set-aside report merges four reasons under one token | CR0579 |
| handoff generate can end a run over an unanswered set with a clean-close outcome (B1, ruled D0206) | CR0580 |
| A forced stop leaves no trace anyone reads and needs no reason or principal | CR0581 |
| No command closes a plan-review REJECT's findings from the approving re-review | CR0582 |
| No command applies a unit's authored Test Plan mutants and registers the kills | CR0583 |
| Plan review is uncapped: 47 REJECTs, five rounds on one unit | CR0578 |
| Stakeholder feedback enters the lifecycle only when someone remembers | RFC0058 |
| A Known issues carried ruling is not checked against who may rule | CR0571 |
| The operator's triage session cap counts a Low folded into CR0511 as a filing | declined: a fold still adds a finding to CR0511's scope, so counting it is the cap doing its job as a volume brake; the operator's session name is the sanctioned escape |
| The harness killed background suite waiters under a memory limit real memory never reached | declined: harness behaviour outside this repository; foreground polling with a 600 s timeout avoided it for the rest of the run |
| 45 stale review worktrees (1.9 GB) slowed the suites | declined: session hygiene, not a tool defect; worktrees are now removed as soon as their patch is saved |
| BG0676's AC4 test judges the baseline's CI-run line by shape, so a hand-typed id reads as a re-measure | BG0707 |
| gate.py reads SDLC_VERIFY_TIMEOUT per call, coupling three previously hermetic test_gate cases to the ambient environment | BG0708 |
| The pre-push red-main check trusts the forge's ordering, so a stale row demands acknowledgement of a two-month-old red and would bank it | BG0709 |
| 386 acceptance criteria select a whole test module, over-claiming and costing most of the corpus pass | CR0584 |
| corpus-verify runs ~1,900 independent criteria serially, 84 minutes in one job under its own cap | CR0585 |
| module-alone re-runs all 133 modules at every push, 551 s of a 749 s gate | CR0586 |

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

- Tokens: captured from the harness at the close (`accuracy --tokens-from-harness`) · Duration: one day, 2026-09-15, 26 commits · Critic rejects: 47 of 70 plan-review verdicts, 4 of 48 delivery verdicts

## Handoff

- [HO-0071](../handoffs/HO0071-nothing-is-left-open-silently-the-sixteen-bugs.md) - 6 remaining item(s): 0 copilot-tail, 6 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
