# RETRO-0089: RUN-01KYZKY5 stopped - 152 points delivered, 27 of 38 units rejected on review

> **Date:** 2026-08-02
> **Batch:** RUN-01KYZKY5 - 44 units (45 planned, 2 dropped, BG0487 added in-batch)
> **Goal:** complete the sprint
> **Delivered:** 45 / 45   **Blocked:** 0 (23 parked in Review by review findings)

## Delivered

All 45 planned units, 152 of 152 points, across 24 commits. Two units were dropped with
recorded reasons (`US0490`, `US0492` - both document a charter queue that does not exist), and
`BG0487` was filed and fixed inside the batch, leaving 44.

Delivered is not the same as accepted. Five independent passes then returned **27 REJECT and
11 APPROVE** over 38 reviewed units, so the run was STOPPED rather than closed: closing it
would have recorded an approval the review withheld.

## Blocked / deferred

Nothing was blocked. 23 delivered units are parked in `Review`, held by review findings
rather than by anything undone. They return cheaply - most need a verifier that can fail, not
a feature.

Filed and carried: `BG0488`-`BG0494`, `CR0523`, `CR0524`, `CR0525`, plus one low-severity
finding consolidated into `CR0511` by the tooling.

## What went well

**The review discriminated, and it discriminated in both directions.** Reviewers reproduced
by execution rather than by impression, and repeatedly withdrew findings after measuring: one
nearly filed "80 of 615 wrongly cleared", re-measured with a corrected regex, found 4, and
withdrew it. Another cleared a suspected laundering path in `_is_cadence_debt` after probing
four vectors and finding none reachable. Eleven units were approved.

**Every finding that was independently re-checked held up.** Zero callers for `close_report`,
`panel_escalation` and `recorded_signoff_panel`; no `--panel` on `critic.py signoff`; six
mirror offenders in the tree `BG0420`'s guard could not see; `LATEST.md` exempted from
claim-drift; the shipped command printing 167 where two surfaces said 178. All verified
directly, none overstated.

**The instruments caught their author.** `run-suite --check` refused a stale verdict I had
already read as current - the exact failure it was built for, firing on the person who built
it. The `NOT FINISHED` warning fired on this retro's own scaffold. The checklist drift guard
caught `sprint appetite` at the gate.

## What was hard / what stalled

**The batch reached 44 units and 25 commits with no independent pass.** `review-batch --open`
exists precisely so a batch is reviewed at its boundary - its own help says a finding is then
delivery work in the batch that caused it rather than close overhead. Zero spans were opened.
The operator noticed, not the tooling: coverage is computed in one place and read at one
moment, the close, when acting on it costs the most. `CR0523`.

**One defect class produced most of the rejections.** A verifier that greps SOURCE TEXT rather
than exercising behaviour, so the feature can be deleted and the test stays green. Ten-plus
instances. `US0608`: reverting the whole feature survives all 390 tests of `test_gate.py`.
`US0609`: deleting its only call site survives all 701 tests of `test_sprint.py`. `BG0401`
shipped this defect inside the bug whose own title is "a grep over source text is not a test
of what the source does".

**`Affects` did not describe the diff on seven units**, `BG0420` with zero overlap. Since
`critic.py brief` derives review scope from `Affects`, those briefs pointed reviewers away
from the code under review - the mechanism trusted to bound scope, fed bad data by its author.

**`lane-check` flagged the failures before any reviewer looked, and shipping continued.** It
reported all seven EP0198 units and both EP0200 units. It is advisory, so it was read as
noise. The rule was available, measured, and did not change behaviour - which is LL0027 with
the number already in hand.

## Lessons

- **A test that asserts the shape of a change cannot fail when the change is deleted.** The
  weakness was not random: it clustered at the end of units, where the feature already worked
  and the test felt like paperwork. `grep -q "NOT FINISHED"` exits 0 against an unreachable
  print; `assertIn("attribute_kill(", src)` is satisfied by the `def` line. Both shipped.
- **Reviewing the test is cheaper than reviewing the code.** This run spent five adversarial
  passes and roughly 800k tokens to discover, after the fact, that ~14 verifiers could not
  fail. A reviewed test plan would have found the same thing before a line of code. The
  `test-spec` artefact type and the name-the-mutant-first rule ALREADY SHIP; the repository
  contains two test specs and this run wrote none. `CR0525`.
- **"Broken" and "unproven" are different facts and want different words.** Roughly 13 of the
  27 rejections were a feature that does not work; roughly 14 were a correct feature with
  evidence that cannot fail. One verdict carried both, so the count read as catastrophe and
  gave no signal about which repairs were urgent. `CR0524`.
- **An advisory detector that fires on the author changes nothing.** `lane-check`'s yield is
  no longer a question: 7 flagged, 6 independently confirmed hollow. That is the number
  `CR0520` asked for.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- EXAMPLE - replace this. A mechanism that reaches no caller is inert, however well it is tested. <!-- example -->
- EXAMPLE - replace this. An absence is not an answer: an empty result and an unanswerable question are different facts. <!-- example -->
- EXAMPLE - replace this. A repair breaks its neighbours, and a rename is cross-unit coupling. <!-- example -->
- EXAMPLE - replace this. An enumerated list silently exempts what it forgot. <!-- example -->
- EXAMPLE - replace this. Verify the premise before building on it. <!-- example -->

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
| BG0000 | not-stop-ship | EXAMPLE - replace this row | 2026-01-01 <!-- example --> |

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

- The points estimate held: 152 planned, 152 delivered, no unit over its size. What the estimate did not price is REVIEW REPAIR. A point measured delivery only, so a batch that delivered exactly to forecast still could not be accepted, and the 90 points now sitting in Review are work the forecast never saw. Until CR0525 moves verification before the code, an estimate should be read as the cost of writing it, not the cost of shipping it.

## Actions raised

| Id | What | Status |
| --- | --- | --- |
| `CR0525` | A unit's test plan written and reviewed BEFORE its code | Proposed, Critical |
| `CR0524` | A verdict separating a broken feature from evidence that cannot fail | Proposed |
| `CR0523` | The unreviewed span reported DURING the run, not found at the close | Proposed |
| `BG0488` | US0608/US0609 ship a feature no CLI invocation can reach | Open |
| `BG0489` | The commit-msg verdict is written before the tool-tests lane | Open |
| `BG0490` | Four bugs Fixed with half their title undelivered | Open |
| `BG0491` | lane-check scans only stories - 487 bugs outside the yield | Open |
| `BG0492` | The verdict binds to the commit, not the tree | Open |
| `BG0493` | Four more verifiers pass on a delivery made inert | Open |
| `BG0494` | resolve_affects lets a project file shadow the skill's | Open |
| `BG0487` | lane-check missed entry through a shared test helper | Fixed in-batch |

**Operator decisions recorded this run:**

1. Stop the run rather than close it or file-and-close. The units stay in `Review` as real
   backlog with the review evidence attached.
2. `lane-check` becomes BLOCKING, once `BG0491` widens its corpus so the yield covers bug
   units as well as stories.

## Close loop (gated)

`gate --require-retro RETROxxxx` (this retro's id, file form) fails until all four are true:

- [ ] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETROxxxx`)
- [ ] its lessons are in the project store, not just in this file (`retro.py extract --id RETROxxxx`)
- [ ] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [ ] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: not attributable to this retro - the run spans a compacted session · Duration: 15.3h working (wall-clock, 0 recorded idle gaps) · Critic rejects: 27 REJECT / 11 APPROVE over 38 units, in 5 independent passes
