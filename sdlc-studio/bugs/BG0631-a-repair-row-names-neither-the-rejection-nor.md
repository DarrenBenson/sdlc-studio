# BG0631: a repair row names neither the rejection nor the phase it answers, so it is joined by date alone and one day's repair discharges every rejection recorded that day

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-schema.md, sdlc-studio/reviews/repair-record.md
> **Evidence:** Found 2026-08-27 by two independent plan reviews of BG0629. Columns quoted from critic.py:781; the join from critic.py:1253, `mine = [r for r in rows if str(r.get('verdict_date') or '') == when]`. `repairs_for` at critic.py:1209 takes no phase. Measured over the corpus: 17 plan-review and 19 delivery units carry two or more REJECTs on a single date, 3 and 11 of them respectively with a repair row stamped that date; US0671 and US0674 carry rejections in BOTH phases on 2026-08-24 with repair rows on that date. 109 repair rows exist to backfill.
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_REPAIR_COLS` is `(unit, verdict_date, author, date, closed, outstanding)`. There is no column saying WHICH rejection a repair answers and none saying which PHASE it belongs to, so `repair_state` joins on the rejection's date at DAY granularity and `repairs_for` does not filter by phase at all.

Two consequences, both live rather than hypothetical. A repair-and-re-review cycle happens within one day by construction, so several rejections of one unit routinely share a date and pool into one bucket - measured, 17 plan-review and 19 delivery units are in that state, and US0674 and US0675 read `complete` in the delivery phase TODAY only because of the pooling. And a DELIVERY repair answers a PLAN-REVIEW rejection recorded the same day, which US0671 and US0674 both demonstrate.

This has been harmless while `repair_state` fed reporting. BG0629 makes a complete repair unblock a delivery gate, which turns both into ways to open that gate with a stale or unrelated repair. So the join must be repaired - but NOT inside BG0629, because it is a ledger schema change: a new column, 109 rows to backfill, `record_repair` and `cmd_repair` writer changes, and the schema contract. BG0629 instead ships the cheap residual guard and names this unit.

## Steps to Reproduce

1. Record two REJECTs for one unit on the same date. 2. Record ONE repair answering only the first. 3. `critic.repair_state` reports `complete`, because the join pools both rejections into the date bucket. 4. Separately, record a delivery REJECT and a plan-review REJECT for one unit on one date, then repair only the delivery one: `repair_state(..., 'plan-review')` reports it answered. Measured on US0671 and US0674, 2026-08-24.

## Proposed Fix

Give a repair row the two identifiers it lacks: the phase it belongs to, and a key naming the rejection it answers - the verdict row's brief fingerprint is the obvious candidate, since it already identifies seat and round, with the date kept for rows that predate it. Both are appended columns, which `_read_rows` already tolerates: a row SHORT by trailing columns is read with those columns absent, so the 109 existing rows keep working and read as pre-adoption.

Backfill deliberately does NOT guess. A row that cannot be attributed to one rejection stays attributed by date and is REPORTED as such, because inventing a key would manufacture exactly the false precision this bug is about. The count of un-attributable rows is the number to publish, not to minimise.

## Acceptance Criteria

- [ ] **AC1** Given a unit with two rejections recorded on ONE date and a repair answering only the first, when the repair state is read, then it is PARTIAL - the second rejection is unanswered, and pooling by date is what hides that
- [ ] **AC2** Given a unit with one rejection and a repair answering it, when the repair state is read, then it is COMPLETE - the paired control, so identifying the rejection does not become a way to refuse every repair that predates the new column
- [ ] **AC3** Given a DELIVERY repair and a PLAN-REVIEW rejection recorded on the same date, when the plan-review repair state is read, then the rejection is NOT answered - `repairs_for` takes no phase today, and US0671 and US0674 are live instances
- [ ] **AC4** Given the 109 repair rows that predate the new columns, when they are read, then each is attributed where it can be and REPORTED as un-attributable where it cannot - a backfill that guesses a key manufactures the false precision this bug exists to remove
- [ ] **AC5** Given the DELIVERY conformance lane before and after the backfill, when the non-conformant population is compared, then every unit that moves is named with the reason it moved - at least US0674 and US0675 read complete today only through date pooling, and a lane that moves silently is how this ships as a surprise

## Impact

It decides whether a gate can be opened by a repair that answered something else. Until BG0629 nothing gated on this, so the cost was a misleading report; after it, a stale same-day repair admits a unit whose rejection nobody addressed. It also silently moves the delivery conformance answer for at least two units, because `conformance.py`:355 reads `repair_state` at the delivery default and two units read complete today only through the pooling.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Filed |
