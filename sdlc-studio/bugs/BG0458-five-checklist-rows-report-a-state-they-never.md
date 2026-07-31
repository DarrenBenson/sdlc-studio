# BG0458: Five checklist rows report a state they never established: planned units read from the retro's Batch rather than the plan, a delivered unit rendered as held, a blind known-issue scan rendered as 'none carried', a lens count that counts reviewer names, and an impediment row that never names the blocker

> **Status:** Fixed
> **Verification depth:** functional (all seven repairs mutation-verified: each defect restored as its own mutant, `assert count(old)==1`, `__pycache__` purged, `python3 -B`, reverted byte-identical. Four survived the first pass and were pinned before the second; one survivor exposed that a test was named for a branch it never reached, and another that my own fix double-counted a unit across two headings)
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

### AC1: the not-delivered row is derived from the PLAN, not the retro

- **Given** a planned unit the retro's Batch never lists
- **When** the row is composed
- **Then** it is named as UNACCOUNTED rather than absorbed into "every planned unit was delivered", and carry-over is measured against the planned set so an unplanned unit is not reported as a broken promise; the two buckets are disjoint, because a unit reported twice under two headings makes the counts stop adding up
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistNotDeliveredTests::test_a_PLANNED_unit_the_retro_never_lists_is_named_not_absorbed
- **Verified:** yes (2026-07-31)

### AC2: held is a live state, and `decision resolve` clears it

- **Given** a unit deferred on an operator decision whose question is later answered, and which then ships
- **When** the row is composed
- **Then** it is not reported held, because `decision resolve` now removes it from `deferred_units` as well as from `pending_decisions` - `defer` writes both lists and only one had a remover, so the close reported a unit held on a decision while counting it delivered on the same page
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistNotDeliveredTests::test_a_unit_whose_decision_was_ANSWERED_and_which_shipped_is_not_held
- **Verified:** yes (2026-07-31)

### AC3: the known-issues row distinguishes an empty scan from a blind one

- **Given** a run record carrying no start time, and separately a retro that cannot be located
- **When** the row is composed
- **Then** each reports UNANSWERED "unreadable" and says which, rather than ANSWERED "none carried" - the sibling impediments row draws exactly this distinction on the same page, so the honest treatment already existed and this row contradicted it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistKnownIssuesBlindnessTests::test_the_carried_table_reports_BLINDNESS_rather_than_an_empty_table
- **Verified:** yes (2026-07-31)

### AC4: lenses are counted by SEAT

- **Given** two different reviewers both standing in the qa seat
- **When** the review row is composed
- **Then** it reports one lens and marks the round UNDER-COVERED, because a lens is a point of view rather than a person; two reviewers with NO declared seat still count separately, since under-reporting coverage is no better than over-reporting it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistReviewRowTests::test_two_reviewers_sharing_ONE_SEAT_are_one_lens
- **Verified:** yes (2026-07-31)

### AC5: the impediment row names the blocker, and names its absence

- **Given** a blocked unit carrying a recorded blocker, and separately one carrying none
- **When** the row is composed
- **Then** the first names what it waits on and the second says NO RECORDED BLOCKER, because an operator told a unit is blocked and not what to unstick has been told half of it, and an impediment nobody can act on is the worse case rather than an equivalent one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::SprintChecklistImpedimentTests::test_a_blocked_unit_with_NO_recorded_blocker_is_named_as_such
- **Verified:** yes (2026-07-31)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Filed |
| 2026-07-31 | Claude Opus 5 | All five findings repaired, plus the root cause behind the second: `decision resolve` now clears `deferred_units`. The scope statements added to these rows earlier are removed, since the rows now do what they said. Mutation found four unpinned repairs on the first pass, and two defects in the repairs themselves - a test named for a branch it never reached, and carry-over double-counting a unit the retro never listed. |
