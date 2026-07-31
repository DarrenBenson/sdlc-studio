# BG0458: Five checklist rows report a state they never established: planned units read from the retro's Batch rather than the plan, a delivered unit rendered as held, a blind known-issue scan rendered as 'none carried', a lens count that counts reviewer names, and an impediment row that never names the blocker

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Independent adversarial review of RUN-01KYTKA1 tranche F (QA seat, isolated worktree, 28 mutants applied, 26 killed). US0570=REJECT, US0571=REJECT, US0575=REJECT, US0576=REJECT.
> **Created:** 2026-07-31
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The compulsory checklist exists so a stage nobody held is visible on the page rather than inferred from its absence. Five of its rows state a conclusion they did not establish, and one of them fails OPEN - which is the defect class the whole checklist was built to end.

`_ck_not_delivered` iterates the retro's Batch field instead of the run's planned set, so a unit that was planned and never reached the retro is reported nowhere, and the row positively asserts "none - every planned unit was delivered" while `planned-vs-delivered` on the same page reads 1/2.

`held` is read from the append-only `deferred_units` list with no pending or terminal check, and `sprint decision resolve` deletes from `pending_decisions` but never from `deferred_units`. A unit whose decision was resolved and which then shipped renders as "held (operator decision pending)" and is simultaneously counted delivered.

`_ck_known_issues` fails open. `_open_findings` returns empty whenever the run record is missing or lacks `started_at`, and `_carried_issues` swallows every exception and returns empty, so a scan that saw nothing renders ANSWERED as "none carried - this sprint left no finding open" with an open bug on disk, and does not hold the close. The sibling `_ck_impediments` distinguishes exactly that blindness as UNANSWERED "unreadable" on the very same page, so the honest treatment already exists beside it.

The lens count counts distinct reviewer NAMES, not lenses, though `seat_for` is already called eight lines above. Two reviewers both in seat `qa` report "2 lens(es)" and escape the UNDER-COVERED mark, contradicting AC2, the constant name `MIN_LENSES`, the row title and the shipped doctrine.

`_ck_impediments` emits only `f"blocked {u}"` and never reads the blocker, so neither half of US0576 AC1 holds: no blocker is named, and "blocked with no recorded blocker" is never rendered - although `Blocked By` / `Depends on` is a shipped read convention and "blocked with blocker" is shipped doctrine.

## Steps to Reproduce

Driven through `sprint_report.checklist()` over purpose-built trees, one property per tree.

```text
planned unit absent from the retro Batch
  -> not-delivered row: "none - every planned unit was delivered"
  -> planned-vs-delivered row on the same page: 1/2

deferred unit, decision resolved, then shipped
  -> "held US0001 (operator decision pending)" AND counted delivered

dropped unit still non-terminal in the retro batch
  -> "1 dropped, 0 held, 1 carried over", naming US0002 twice

no run record / no started_at / forced carried_issues exception
  -> ANSWERED "none carried - this sprint left no finding open"
  -> close NOT held, with an Open bug on disk

two reviewers, both seat qa
  -> "2 lens(es)", not marked UNDER-COVERED

blocked unit with a recorded blocker
  -> "blocked US0001", blocker never read
```

## Proposed Fix

Read the planned set from the run's plan, not from the retro's Batch - the retro is a record of what happened, and the question the row asks is what was promised.

Give `deferred_units` a remover, or derive held from the pending decisions rather than from the append-only list. An append-only list is a log, not a state.

Make `_ck_known_issues` distinguish a scan that saw nothing from a scan that could not see, exactly as `_ck_impediments` already does on the same page: blindness is UNANSWERED, not "none".

Count lenses with `seat_for`, which is already called. Name the blocker in the impediment row, and render "blocked with no recorded blocker" when there is none - the absent case is the one the row exists for.

## Acceptance Criteria

- [ ] The not-delivered row is derived from the run's PLANNED set, so a planned unit absent from the retro Batch is named rather than absorbed into 'every planned unit was delivered'
- [ ] A unit whose deferral decision was resolved and which then shipped is not rendered as held, and is not counted both held and delivered
- [ ] The known-issues row distinguishes a scan that saw nothing from a scan that could not see: an unreadable or absent run record renders UNANSWERED and holds the close, rather than ANSWERED 'none carried'
- [ ] The lens count counts SEATS via `seat_for`, so two reviewers sharing one seat report one lens and are marked UNDER-COVERED
- [ ] The impediment row names the recorded blocker, and renders 'blocked with no recorded blocker' when a blocked unit has none

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Filed |
