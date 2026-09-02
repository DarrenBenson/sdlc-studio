# BG0631: a repair row names neither the rejection nor the phase it answers, so it is joined by date alone and one day's repair discharges every rejection recorded that day

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-schema.md, sdlc-studio/reviews/repair-record.md
> **Verification depth:** functional [[derived: criteria 5; plan rows 9; executed 9; killed 9; survived 0; not-run 0; entry point 0 of 5 criteria through the shipped CLI, 5 in-process | fp fef06dcc7216 ]] (every criterion driven through the shipped command in a throwaway fixture, with the paired control beside each refusal)
> **Evidence:** Found 2026-08-27 by two independent plan reviews of BG0629. Columns quoted from critic.py:781; the join from critic.py:1253, `mine = [r for r in rows if str(r.get('verdict_date') or '') == when]`. `repairs_for` at critic.py:1209 takes no phase. Measured over the corpus: 17 plan-review and 19 delivery units carry two or more REJECTs on a single date, 3 and 11 of them respectively with a repair row stamped that date; US0671 and US0674 carry rejections in BOTH phases on 2026-08-24 with repair rows on that date. 109 repair rows exist to backfill.
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_REPAIR_COLS`is`(unit, verdict_date, author, date, closed, outstanding)`. There is no column saying WHICH rejection a repair answers and none saying which PHASE it belongs to, so `repair_state`joins on the rejection's date at DAY granularity and`repairs_for` does not filter by phase at all.

Two consequences, both live rather than hypothetical. A repair-and-re-review cycle happens within one day by construction, so several rejections of one unit routinely share a date and pool into one bucket - measured, 17 plan-review and 19 delivery units are in that state, and US0674 and US0675 read `complete` in the delivery phase TODAY only because of the pooling. And a DELIVERY repair answers a PLAN-REVIEW rejection recorded the same day, which US0671 and US0674 both demonstrate.

This has been harmless while `repair_state`fed reporting. BG0629 makes a complete repair unblock a delivery gate, which turns both into ways to open that gate with a stale or unrelated repair. So the join must be repaired - but NOT inside BG0629, because it is a ledger schema change: a new column, 109 rows to backfill,`record_repair`and`cmd_repair` writer changes, and the schema contract. BG0629 instead ships the cheap residual guard and names this unit.

## Steps to Reproduce

1. Record two REJECTs for one unit on the same date. 2. Record ONE repair answering only the first. 3. `critic.repair_state`reports`complete`, because the join pools both rejections into the date bucket. 4. Separately, record a delivery REJECT and a plan-review REJECT for one unit on one date, then repair only the delivery one: `repair_state(..., 'plan-review')` reports it answered. Measured on US0671 and US0674, 2026-08-24.

## Proposed Fix

Give a repair row the two identifiers it lacks: the phase it belongs to, and a key naming the rejection it answers - the verdict row's brief fingerprint is the obvious candidate, since it already identifies seat and round, with the date kept for rows that predate it. Both are appended columns, which `_read_rows` already tolerates: a row SHORT by trailing columns is read with those columns absent, so the 109 existing rows keep working and read as pre-adoption.

Backfill deliberately does NOT guess. A row that cannot be attributed to one rejection stays attributed by date and is REPORTED as such, because inventing a key would manufacture exactly the false precision this bug is about. The count of un-attributable rows is the number to publish, not to minimise.

## Acceptance Criteria

- [x] **AC1** Given a unit carrying the SAME finding text raised in BOTH phases on ONE date, and a DELIVERY repair closing it, when the PLAN-REVIEW repair state is read, then the plan-review rejection is NOT answered. This is the criterion the unit was missing: the two shapes originally filed - two same-date delivery rejections, and a delivery repair against a plan-review rejection with DIFFERENT text - both already pass on HEAD, because `repair_state`loops per rejection and`resolve_finding` separates distinct texts. What still fails is text COLLISION, which is the ordinary shape rather than an exotic one: a plan-review finding surviving into delivery is what a review round normally produces
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairPhaseJoinTests::test_a_delivery_repair_does_not_answer_a_same_text_plan_review_rejection
- [x] **AC2** Given the same fixture with the DELIVERY phase read instead, when the repair state is read, then it IS complete. The paired control: refusing to join a repair to anything satisfies AC1 on its own, and would break every repair record in the corpus
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairPhaseJoinTests::test_the_delivery_phase_still_reads_its_own_repair
- [x] **AC3** Given a repair row written after this lands, when it is read back, then it names the PHASE and the rejection it answers, and `repairs_for`is asked for a phase rather than returning every row for the unit.`_REPAIR_COLS`carries neither today, so the join is`verdict_date` equality alone
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairPhaseJoinTests::test_a_written_row_carries_its_phase_and_rejection
- [x] **AC4** Given the repair rows that predate the new columns, when they are read, then each is attributed where the date makes it unambiguous and REPORTED as un-attributable where it does not - never guessed. A backfill that assigns a phase it cannot know is the record made prettier rather than truer, which this project has already refused once
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairPhaseJoinTests::test_legacy_rows_are_attributed_or_named_unattributable
- [x] **AC5** Given the delivery conformance population before and after the change, when the two are compared, then every unit that moves is NAMED with the reason. The comparison is taken with `conformance.py` AFTER BG0628 lands in this same batch: today that lane reports 304, 671 or 732 for one corpus depending only on which directories were copied, so a before-and-after taken with it would be arithmetic on a number nobody can reproduce
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RepairPhaseJoinTests::test_every_unit_that_moves_is_named_with_its_reason

## Impact

It decides whether a gate can be opened by a repair that answered something else. Until BG0629 nothing gated on this, so the cost was a misleading report; after it, a stale same-day repair admits a unit whose rejection nobody addressed. It also silently moves the delivery conformance answer for at least two units, because `conformance.py`:355 reads `repair_state` at the delivery default and two units read complete today only through the pooling.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/critic.py`, drop the phase argument from `repair_state`'s call so rows are joined by date alone | Given a unit carrying the SAME finding text raised in BOTH phases on ONE date, and a DELIVERY repair closing it, when the PLAN-REVIEW repair state is read, then the plan-review rejection is NOT answered. This is the criterion the unit was missing: the two shapes originally filed - two same-date delivery rejections, and a delivery repair against a plan-review rejection with DIFFERENT text - both already pass on HEAD, because `repair_state`loops per rejection and`resolve_finding` separates distinct texts. What still fails is text COLLISION, which is the ordinary shape rather than an exotic one: a plan-review finding surviving into delivery is what a review round normally produces |
| AC2 | in `.claude/skills/sdlc-studio/scripts/critic.py`, return an empty list from `repairs_for` so nothing ever answers its phase | Given the same fixture with the DELIVERY phase read instead, when the repair state is read, then it IS complete. The paired control: refusing to join a repair to anything satisfies AC1 on its own, and would break every repair record in the corpus |
| AC3 | in `.claude/skills/sdlc-studio/scripts/critic.py`, replace the phase argument in the write tuple with an empty string | Given a repair row written after this lands, when it is read back, then it names the PHASE and the rejection it answers, and `repairs_for`is asked for a phase rather than returning every row for the unit.`_REPAIR_COLS`carries neither today, so the join is`verdict_date` equality alone |
| AC3 | in `.claude/skills/sdlc-studio/scripts/critic.py`, replace the rejection cell's expression with a constant, so the row names no rejection | Given a repair row written after this lands, when it is read back, then it names the PHASE and the rejection it answers, and `repairs_for`is asked for a phase rather than returning every row for the unit.`_REPAIR_COLS`carries neither today, so the join is`verdict_date` equality alone |
| AC3 | in `.claude/skills/sdlc-studio/scripts/critic.py`, narrow the width bound in `_read_rows` from two cells to `len(cols) - 1`, which drops every six-cell legacy row | Given a repair row written after this lands, when it is read back, then it names the PHASE and the rejection it answers, and `repairs_for`is asked for a phase rather than returning every row for the unit.`_REPAIR_COLS`carries neither today, so the join is`verdict_date` equality alone |
| AC4 | in `.claude/skills/sdlc-studio/scripts/critic.py`, widen the unambiguous-date test to accept an ambiguous one, skipping the closure consultation | Given the repair rows that predate the new columns, when they are read, then each is attributed where the date makes it unambiguous and REPORTED as un-attributable where it does not - never guessed. A backfill that assigns a phase it cannot know is the record made prettier rather than truer, which this project has already refused once |
| AC4 | in `.claude/skills/sdlc-studio/scripts/critic.py`, replace the closure fallback with a constant false | Given the repair rows that predate the new columns, when they are read, then each is attributed where the date makes it unambiguous and REPORTED as un-attributable where it does not - never guessed. A backfill that assigns a phase it cannot know is the record made prettier rather than truer, which this project has already refused once |
| AC4 | in `.claude/skills/sdlc-studio/scripts/critic.py`, narrow the ambiguity test to `> 1`, leaving the zero-hit branch unreported | Given the repair rows that predate the new columns, when they are read, then each is attributed where the date makes it unambiguous and REPORTED as un-attributable where it does not - never guessed. A backfill that assigns a phase it cannot know is the record made prettier rather than truer, which this project has already refused once |
| AC5 | in `.claude/skills/sdlc-studio/scripts/critic.py`, invert the ambiguity test in `unattributable_repairs`so no row is ever appended | Given the delivery conformance population before and after the change, when the two are compared, then every unit that moves is NAMED with the reason. The comparison is taken with `conformance.py` AFTER BG0628 lands in this same batch: today that lane reports 304, 671 or 732 for one corpus depending only on which directories were copied, so a before-and-after taken with it would be arithmetic on a number nobody can reproduce |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Filed |
