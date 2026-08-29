# BG0629: a plan-review REJECT can never be retired, because repairing the plan changes the brief fingerprint the retirement must match - 44 of 44 stand, and a COMPLETE repair record discharges nothing

> **Status:** Fixed
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** Hit 2026-08-27 in RUN-01M11MEP, which it BLOCKS. BG0622 was rejected at plan review (brief e968308171ed), repaired, re-reviewed and APPROVED (brief 43e68b01a06a), and `critic.repair_state` reads `complete` with all six findings closed - yet `critic.verdict_for` still returns the r1 REJECT and `transition set BG0622 'In Progress'` refuses. Swept over the whole ledger: 44 units have ever carried a plan-review REJECT and the standing verdict is REJECT for 44 of 44. Not one has ever been retired. Guard quoted from critic.py:525-533; the gate's sole input from transition.py:2467.
> **Verification depth:** functional [[derived: criteria 7; plan rows 7; executed 7; killed 7; survived 0; not-run 0; entry point 5 of 7 criteria through the shipped CLI, 2 in-process | fp e80086a79160 ]] (seven criteria, every mutant applied to the real file with bytecode purged and the tree restored after each. Five reach the shipped CLI - the wall was hit through `transition.py set`, and a library test cannot see the gate that calls it. The two in-process rows are the placement guard and the closure join, which are claims about `critic.py`'s own contract rather than about a command.)
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_unanswered_rejects` retires a REJECT only when a LATER APPROVE carries the SAME brief fingerprint. The fingerprint is a content hash of the brief, and the brief embeds the unit's own acceptance criteria and test plan. So repairing the thing the reviewer rejected necessarily changes the fingerprint, and the approval of the REPAIRED plan can never match the rejection of the ORIGINAL one. The only APPROVE that could retire a rejection is one against a byte-identical artefact - a reviewer changing its mind with nothing fixed.

The loop is therefore unclosable by correct behaviour, and the corpus shows it: 44 of 44 rejected units still stand REJECTed. `critic.py repair` exists for exactly this, records `complete`, and NO gate reads it - `transition.py`:2467 calls `critic.verdict_for` and nothing else, so a fully dispositioned repair discharges nothing.

The gate then behaves inconsistently rather than strictly, because it fires on ENTRY to `In Progress`. A unit rejected while still Open is blocked for ever; a unit rejected after it started is never re-checked. That is how 41 of the 44 reached Done or Fixed carrying a standing rejection, while the three rejected before starting - BG0622, BG0625 and BG0626, all in the open run - cannot move at all. The rule is not enforced consistently AND cannot be satisfied: the worst of both.

## Steps to Reproduce

1. Record a plan-review REJECT for an Open unit. 2. Repair the unit's criteria or test plan. 3. Re-brief - the fingerprint necessarily differs, because the brief embeds the criteria. 4. Record the re-review's APPROVE. 5. `critic.py repair --closed-file ...` and confirm `repair_state` reads `complete`. 6. `transition.py set <unit> 'In Progress'` still refuses, naming the round-1 REJECT. There is no sixth step that clears it.

## Proposed Fix

The rule already exists and already ships - for the DELIVERY phase. `conformance.py`:350-357
reads the standing verdict and, when it is a REJECT, returns
`critic.repair_state(root, rid)["state"] == "complete"`. A rejection answered by a complete
repair is not held against the unit. The plan-review gate is the one place that reading was
never applied, so this is a missing application of a shipped rule rather than a new rule.

So the consultation goes in the CALLER, `transition._test_plan_gate`, in the same shape. Two
placements were considered and BOTH are rejected on recursion, which is why this section names
the one that ships:

- inside `_unanswered_rejects` - UNCONDITIONALLY recursive. `repair_state` calls
  `_unanswered_rejects`, so every call for every unit cycles. It also needs a signature change,
  since that function takes rows and has no repo root.
- inside `verdict_for` - recursion-REACHABLE. `repair_state` falls back to `verdict_for`, and
  the two row sets differ: `verdict_for` filters by `kind` and drops superseded rows while
  `repair_state` filters by neither. A superseded or different-kind APPROVE carrying the
  matching fingerprint makes the fallback fire and recurse, doubling per level. It is broken
  today only by an `or` short-circuit, which is a data-dependent accident. It would also flip
  all 22 `verdict_for` call sites, and the conformance `critiqued` lane hardest: a unit
  conformant today by the repair route would newly face an independence and a tier-depth check
  it has never been held to.

The caller placement flips exactly one call site - the one this bug's evidence is about.

Two things must be true for the rule to be SAFE here, because this gate makes `repair_state`
load-bearing for the first time.

The repair must be read in the RIGHT PHASE. `repairs_for` (`critic.py`:1209) takes no phase
and the ledger has no phase column, so a DELIVERY repair recorded on the same date as a
plan-review rejection answers it - US0671 and US0674 are live instances from 2026-08-24.
This unit passes `phase="plan-review"` and filters the REJECTION rows it reads, which is in
scope because it is the call this unit adds. It does NOT filter the repair rows - those carry
no phase column, and adding one is BG0631 - so the cross-phase leak survives here whenever a
repair's closures resolve by ORDINAL rather than by quoted text. AC4's fixture names its
closures by text for that reason, and the residue is stated rather than claimed closed.

And a stale same-day repair must not open the gate. `repair_state` joins on `verdict_date` at
DAY granularity (`critic.py`:1253), and a repair-and-re-review cycle happens within one day by
construction - this run recorded three rejections of one unit on 2026-08-27. Repairing that
join properly is a LEDGER SCHEMA change - a new column, 109 rows to backfill, writer changes,
the schema contract - and it moves the delivery conformance answer for US0674 and US0675,
which read complete today only through the pooling. That is BG0631, not this unit. Here the
residual is guarded cheaply and stated rather than hidden: the gate refuses when the unit
carries more unanswered rejections on the repair's date than it has repair rows, so a single
repair cannot discharge a day's worth of them.

AC7 was added AFTER this plan was approved at round three, on a defect found while recording
this unit's own repair: `cmd_repair` resolves closures against the standing verdict only, so
the findings of an earlier rejection can be counted as outstanding and never closed. It is in
scope rather than a new unit because without it the rule this unit ships cannot be used - a
twice-rejected unit could never reach COMPLETE, and this unit is itself twice-rejected. The
addition is disclosed here rather than folded in silently, and it has had no independent
review at plan time.

NOT in this unit, recorded so the boundary is explicit rather than forgotten:

- the gate is skipped on `In Progress -> Done` and `Review -> Done`, because `from_canon` is
  already in `_IMPL_TARGETS`. That skip is documented idempotency for a forward walk, and
  reversing it is a second behaviour change this bug's evidence does not reach - the evidence
  here is three Open units that cannot ENTER In Progress. A direct `Ready -> Done` already
  fires the gate and is already refused, so the original wording of this bug was wrong about
  it. Filed as BG0630.
- the 44 standing rejections. Measured: 7 carry a complete repair, 2 partial, 35 none. This
  fix retires the 7. The remaining 37 are an ADOPTION problem, not a repair problem -
  plan-review is the only gate of its family with no adoption cutoff, which is CR0543, already
  open. Thirty-seven hand-written waivers into a mechanism `critic.py` does not have is not
  the proportionate answer and is not five points.

## L-0344 disclosure

This unit repairs the gate that is refusing its own run, and afterwards that gate reads green
for BG0622, BG0625 and BG0626 by construction. The lesson says a self-authored gate repair is
invisible afterwards, so: the operator was shown the wall and ruled on it before any code was
written, and every criterion below is verified in an ISOLATED FIXTURE rather than against the
live ledger. No criterion asserts anything about this run's own three units: a test that reads
the live workspace becomes unfalsifiable the moment the dispositions land.

An earlier draft of this section claimed that of five criteria while two of them did not meet
it - one argued from this run's own BG0625 and one could only be read against the live corpus,
and those were precisely the two touching the gate refusing this run. Both were rewritten
rather than the claim narrowed, which is recorded here because a disclosure that overstates
itself is worse than none.

## Acceptance Criteria

- [x] **AC1** Given an ISOLATED FIXTURE holding PLAN-REVIEW rows only, in which a unit's REJECT is answered by a repair `repair_state` reports COMPLETE, when the test-plan gate runs, then it does NOT block - the reading `conformance.py`:355 already applies in the delivery phase, applied in the one place it never was. The call passes `phase="plan-review"` explicitly, because `repair_state` defaults to delivery
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::PlanReviewRepairGateTests::test_a_complete_repair_clears_the_test_plan_gate
  - **Verified:** yes (2026-08-27)
- [x] **AC2** Given the same fixture with a PARTIAL repair, when the gate runs, then it still blocks AND its refusal names the outstanding findings. The message matters: a partial repair was blocked before this change too, by the plain REJECT path, so a criterion asserting only the block passes on pre-existing behaviour - naming what is still outstanding is computable only through the new consultation
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::PlanReviewRepairGateTests::test_a_partial_repair_still_blocks_and_names_what_is_outstanding
  - **Verified:** yes (2026-08-27)
- [x] **AC3** Given a fixture whose `.config.yaml` sets `review.test_plan_after` so the gate is ACTIVE, when `transition.py set <unit> 'In Progress'` is run through the shipped CLI, then it SUCCEEDS for the repaired unit and REFUSES for an unrepaired one. Both halves are required: the gate stands down entirely when the cutoff is unset, which is the default, so a success asserted alone goes green on a gate that never fired
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::PlanReviewRepairGateTests::test_the_cli_admits_a_repaired_unit_and_refuses_an_unrepaired_one
  - **Verified:** yes (2026-08-27)
- [x] **AC4** Given a fixture in which a unit carries a DELIVERY repair and a PLAN-REVIEW rejection recorded on the SAME DATE, when the plan-review gate runs, then it still blocks. `repairs_for` takes no phase and the ledger has no phase column, so without this the gate this unit adds is opened by a repair from another phase entirely
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::PlanReviewRepairGateTests::test_a_delivery_repair_does_not_answer_a_plan_review_rejection
  - **Verified:** yes (2026-08-27)
- [x] **AC5** Given a unit carrying TWO unanswered rejections that raise DIFFERENT findings, when a repair answers only one of them, then the gate still BLOCKS and names the other. This is `repair_state`'s own per-rejection computation rather than a count of repair rows: an earlier version counted rows per date as a proxy, and once each closure is dispatched to the rejection it answers, that count refused a genuinely complete repair whenever ONE row legitimately closed two same-date rejections - the ordinary shape
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::PlanReviewRepairGateTests::test_a_repair_does_not_discharge_a_rejection_it_did_not_answer
- [x] **AC6** Given an isolated fixture holding a DELIVERY rejection whose repair is complete but whose tier depth is NOT covered, when `critic.verdict_for` is read, then it still returns REJECT and conformance reaches its answer through `conformance.py`:355. This is the placement guard, stated as a property rather than as a before-and-after snapshot: relocating the consultation into `verdict_for` makes `per_unit_ok` true, runs `tier_covers`, and flips the answer
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairPlacementTests::test_the_delivery_lane_still_answers_through_the_conformance_branch
  - **Verified:** yes (2026-08-27)
- [x] **AC7** Given a unit carrying TWO unanswered rejections, when a repair is recorded naming a finding the EARLIER one raised, then it is accepted and counted. `cmd_repair` resolves closures against the standing verdict alone while `repair_state` computes outstanding across every unanswered rejection, so a finding from an earlier rejection can be counted against you and never closed. Without this the rule this unit ships is unusable: a twice-rejected unit can never reach COMPLETE, so its gate can never clear
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairPlacementTests::test_a_closure_can_answer_an_earlier_rejection_not_only_the_standing_one
  - **Verified:** yes (2026-08-27)

## Impact

It blocks delivery outright. Three units of the currently open run cannot enter `In Progress` and no sequence of correct actions unblocks them. More broadly it makes the plan-review gate dishonest in both directions at once: unsatisfiable for anyone who is rejected early, and inert for everyone rejected late. The project's own doctrine says the cheapest defect is the one a plan review catches before code; this makes accepting that review's verdict a dead end.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/transition.py`, delete the repair consultation from `_test_plan_gate` so it blocks on the standing REJECT alone - the pre-fix behaviour, which is what makes 44 of 44 stand | Given an ISOLATED FIXTURE holding PLAN-REVIEW rows only, in which a unit's REJECT is answered by a repair `repair_state` reports COMPLETE, when the test-plan gate runs, then it does NOT block - the reading `conformance.py`:355 already applies in the delivery phase, applied in the one place it never was. The call passes `phase="plan-review"` explicitly, because `repair_state` defaults to delivery |
| AC2 | in `.claude/skills/sdlc-studio/scripts/transition.py`, weaken the gate's test from `state == complete` to the presence of any repair row, so a unit with one closure and nine outstanding findings passes | Given the same fixture with a PARTIAL repair, when the gate runs, then it still blocks AND its refusal names the outstanding findings. The message matters: a partial repair was blocked before this change too, by the plain REJECT path, so a criterion asserting only the block passes on pre-existing behaviour - naming what is still outstanding is computable only through the new consultation |
| AC3 | in `.claude/skills/sdlc-studio/scripts/transition.py`, remove the `_test_plan_gate` call from the block list at line 1049 so the library gate stays correct and the shipped command stops consulting it - the wiring mutant AC1 survives | Given a fixture whose `.config.yaml` sets `review.test_plan_after` so the gate is ACTIVE, when `transition.py set <unit> 'In Progress'` is run through the shipped CLI, then it SUCCEEDS for the repaired unit and REFUSES for an unrepaired one. Both halves are required: the gate stands down entirely when the cutoff is unset, which is the default, so a success asserted alone goes green on a gate that never fired |
| AC4 | in `.claude/skills/sdlc-studio/scripts/transition.py`, call `repair_state` without the `phase` argument, taking its delivery default, so a repair from the other phase answers a plan-review rejection | Given a fixture in which a unit carries a DELIVERY repair and a PLAN-REVIEW rejection recorded on the SAME DATE, when the plan-review gate runs, then it still blocks. `repairs_for` takes no phase and the ledger has no phase column, so without this the gate this unit adds is opened by a repair from another phase entirely |
| AC5 | in `.claude/skills/sdlc-studio/scripts/critic.py`, pool every closure against every rejection sharing a date rather than resolving each against the rejection it answers, so a closure set answering one reads as answering its sibling | Given a unit carrying TWO unanswered rejections that raise DIFFERENT findings, when a repair answers only one of them, then the gate still BLOCKS and names the other. This is `repair_state`'s own per-rejection computation rather than a count of repair rows: an earlier version counted rows per date as a proxy, and once each closure is dispatched to the rejection it answers, that count refused a genuinely complete repair whenever ONE row legitimately closed two same-date rejections - the ordinary shape |
| AC6 | in `.claude/skills/sdlc-studio/scripts/critic.py`, relocate the consultation from the caller into `verdict_for` itself, immediately after `unanswered` is computed, so that every one of the twenty-two call sites reads the repair-adjusted verdict and `conformance.py`'s critiqued branch at line 355 becomes unreachable | Given an isolated fixture holding a DELIVERY rejection whose repair is complete but whose tier depth is NOT covered, when `critic.verdict_for` is read, then it still returns REJECT and conformance reaches its answer through `conformance.py`:355. This is the placement guard, stated as a property rather than as a before-and-after snapshot: relocating the consultation into `verdict_for` makes `per_unit_ok` true, runs `tier_covers`, and flips the answer |
| AC7 | in `.claude/skills/sdlc-studio/scripts/critic.py`, narrow `cmd_repair`'s closure resolution so it builds its candidate finding list from the standing verdict alone rather than from every unanswered rejection, so a closure quoting an earlier rejection's finding resolves against nothing | Given a unit carrying TWO unanswered rejections, when a repair is recorded naming a finding the EARLIER one raised, then it is accepted and counted. `cmd_repair` resolves closures against the standing verdict alone while `repair_state` computes outstanding across every unanswered rejection, so a finding from an earlier rejection can be counted against you and never closed. Without this the rule this unit ships is unusable: a twice-rejected unit can never reach COMPLETE, so its gate can never clear |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Filed |
