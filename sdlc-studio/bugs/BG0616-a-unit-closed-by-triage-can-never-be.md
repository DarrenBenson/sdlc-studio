# BG0616: a unit CLOSED by triage can never be covered by a retro, so it owes a close-down for ever and the advisory can only be cleared by lying

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py
> **Evidence:** `close_owed.py detect` on 2026-08-26 reports BG0599 and BG0602 owed. Both are at Closed. RETRO0109 names BG0599 four times and neither in its Batch line. Coverage mechanism quoted from source at close_owed.py:167-176, and the epic precedent at close_owed.py:549-553, per D0151.
> **Verification depth:** functional [[derived: criteria 6; plan rows 6; executed 6; killed 6; survived 0; not-run 0; entry point 1 of 6 criteria through the shipped CLI, 5 in-process | fp 7b5e035a740e ]] (six criteria, every mutant applied to the real file with bytecode purged and the tree restored after each. One drives `close_owed.py detect` as a subprocess, and its wiring mutant is invisible to all five library rows. AC5 is measured on this repository's own corpus with a corpus-only mutant - read the first id of a `fixed-in:` detail, which drops BG0602 from RETRO0109's multi-id row and which no fixture here is obliged to have. Measured delta: covered 1032 to 1037, owed six to four.)
> **Created:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`close_owed.covered_ids` (`close_owed.py`:167-176) builds the covered set from each retro's `Batch` field and nothing else. A unit closed by pre-code triage - premise did not reproduce at HEAD, closed WON'T FIX or Closed rather than built - is by definition NOT in the run's batch, and putting it there would misstate what the run delivered. So it is uncovered permanently and no future close can clear it. Measured 2026-08-26: `close_owed.py detect` reports BG0599 and BG0602 owed, while RETRO0109 names BG0599 FOUR times - in its Blocked and deferred section and in its findings table as `fixed-in: BG0599, BG0602 and BG0463 closed with their source lines recorded` - and names neither in its Batch line, correctly. The retro that accounts for them exists and the checker cannot see it. `owed`'s own docstring already records this exact failure mode for EPICS at `close_owed.py`:549-553: an epic is never named in a Batch, so requiring it manufactured debt no further close could clear, and epics were given an inheritance rule. Triage-closures have the same shape and no rule.

## Steps to Reproduce

1. Open a run whose pre-code goal review finds a unit's premise does not reproduce. 2. Close that unit by triage rather than building it, and account for it by name in the retro's Blocked/deferred section. 3. Close the run. 4. `close_owed.py detect` reports the unit owed, and every subsequent `hint` and `status` repeats the advisory. Measured on BG0599 and BG0602, closed before RUN-01M0WCCG and named in RETRO0109.

## Proposed Fix

Give a triage-closure the same treatment epics already have, and take the account from the
retro's `## Actions raised` table ALONE - specifically its `fixed` dispositions, the rows that
say a finding was closed in-sprint and name what closed it. `retro.dispositions_in`
(`retro.py`:456) already parses that table and classifies each row filed / fixed / declined /
undecided, so no second parser is needed for it.

Three readings are deliberately NOT taken, and each would be a hole:

- a `filed` row names FUTURE work. RETRO0109 files BG0612, CR0557 and CR0556 that way, so
  counting them would let the retro that RAISED a bug also discharge it.
- an id inside a `declined:` reason names what the decline defers to, which `dispositions_in`'s
  own docstring warns about.
- the `Blocked / deferred` section is NOT read, and an earlier draft of this fix said it was
  gated content needing no second parser. That was FALSE and a review measured it: `Blocked /
  deferred` is not in `REQUIRED_SECTIONS`, no undecided check reaches it, and neither
  `retro.py` nor `close_owed.py` mentions it - it is free prose. Worse, RETRO0109's own bullet
  reads "BG0599, BG0602 and BG0463 were CLOSED ... Their surviving limbs are re-filed as
  BG0612 and CR0557": future work in the same sentence as the units being accounted for. An
  id-scan there forgives BG0612 the day it reaches terminal, which is the `filed` hazard
  arriving by a route nothing was watching.

The corpus instance survives that narrowing: RETRO0109 accounts for BG0599 and BG0602 in a
`fixed-in:` row as well as in the prose, so the gated source alone is enough. Measured
delta: covered goes 1032 to 1037 repo-wide - five ids - and the owed set goes from BG0599,
BG0602, BG0622, BG0625, BG0626, BG0629 to exactly the four this run raised.

One shape this deliberately does NOT rescue, recorded so it is a known edge rather than a
surprise: a triage closure accounted for in a `declined:` row still owes for ever, because
the id normally sits in the finding column rather than the detail, and 45 of 204 declined
rows repo-wide carry an id in the reason that names what the decline DEFERS to. Excluding
them is right; the escape is to record the closure as `fixed-in:`, which is what RETRO0109
did.

Two fixture shapes the criteria depend on, stated rather than left to the implementer:
AC1's `fixed-in:` row carries a SINGLE id, or AC5's first-id-only mutant kills AC1 too and
stops being corpus-only; and AC2's prose fixture sits OUTSIDE any `Blocked / deferred`
heading, or AC4's mutant kills AC2 as well and the two rows collapse into one.

What must NOT happen is the only currently available remedy: adding a non-delivered unit to a
`Batch` line, which would make the retro's own delivered count false and would be read by
`retro accuracy` as delivery.

## Acceptance Criteria

- [ ] **AC1** Given a unit closed by TRIAGE and named in a retro's `fixed` disposition, when close-owed runs, then it is COVERED - a rejection answered by a decision is answered, and a `Batch` line is not the only way to account for a unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::TriageClosureCoverageTests::test_a_fixed_disposition_covers_a_triage_closure
  - **Verified:** yes (2026-08-27)
- [ ] **AC2** Given a unit named in a retro's PROSE but in no disposition row at all, when close-owed runs, then it is still OWED. The fixture matters: a unit named in NO retro stays owed however widely the reading is loosened, so a control written that way survives the named-anywhere mutant it exists to catch
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::TriageClosureCoverageTests::test_a_mention_in_prose_does_not_cover_a_unit
  - **Verified:** yes (2026-08-27)
- [ ] **AC3** Given a unit named ONLY in a `filed` disposition - the row that raises future work rather than accounting for delivered work - when close-owed runs, then it is still OWED. Without this, widening coverage lets the retro that FILED a bug discharge it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::TriageClosureCoverageTests::test_a_filed_disposition_does_not_cover_the_unit_it_raises
  - **Verified:** yes (2026-08-27)
- [ ] **AC4** Given a unit named in a retro's `Blocked / deferred` section but in NO disposition row, when close-owed runs, then it is still OWED. That section is free prose - it is not in `REQUIRED_SECTIONS` and no check reaches it - and RETRO0109's own bullet names future work in the same sentence as the units it accounts for, so reading it would forgive BG0612 the day it reaches terminal
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::TriageClosureCoverageTests::test_the_blocked_section_is_not_a_coverage_source
  - **Verified:** yes (2026-08-27)
- [ ] **AC5** Given this repository's own corpus, when the widened check runs, then BG0599 and BG0602 are COVERED by RETRO0109, which names them in a multi-id `fixed-in:` row, and every OTHER owed unit is still reported. The assertion is on those two ids, never on an empty owed set: six units are owed at HEAD, four of them this run's own
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::TriageClosureCoverageTests::test_the_live_corpus_covers_the_two_triage_closures_and_nothing_else
  - **Verified:** yes (2026-08-27)
- [ ] **AC6** Given the shipped command rather than the library, when `close_owed.py detect` runs, then it does not name BG0599 or BG0602. The advisory this bug is about is printed by `status` and named by that command, and a library test cannot see either stopping to call the coverage it reads
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::TriageClosureCoverageTests::test_the_detect_command_no_longer_names_the_two_triage_closures
  - **Verified:** yes (2026-08-27)

## Impact

An advisory that cannot be cleared by correct behaviour is one operators learn to ignore, and it sits on `hint` and `status` - the two commands every session runs first, and the same surface BG0615 was found on. It also punishes exactly the behaviour this project wants: a pre-code goal review that kills a unit before any code is written is the cheapest possible outcome, and it is the one that manufactures permanent debt.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/close_owed.py`, narrow the disposition reading to `declined` rows only, so a `fixed` row stops covering anything while the branch itself still runs | Given a unit closed by TRIAGE and named in a retro's `fixed` disposition, when close-owed runs, then it is COVERED - a rejection answered by a decision is answered, and a `Batch` line is not the only way to account for a unit |
| AC2 | in `.claude/skills/sdlc-studio/scripts/close_owed.py`, widen the reading to scan the whole retro for ids rather than its disposition rows, so a passing mention in prose discharges a unit | Given a unit named in a retro's PROSE but in no disposition row at all, when close-owed runs, then it is still OWED. The fixture matters: a unit named in NO retro stays owed however widely the reading is loosened, so a control written that way survives the named-anywhere mutant it exists to catch |
| AC3 | in `.claude/skills/sdlc-studio/scripts/close_owed.py`, count a `filed` disposition as covering, so the retro that RAISED a unit also discharges it | Given a unit named ONLY in a `filed` disposition - the row that raises future work rather than accounting for delivered work - when close-owed runs, then it is still OWED. Without this, widening coverage lets the retro that FILED a bug discharge it |
| AC4 | in `.claude/skills/sdlc-studio/scripts/close_owed.py`, add the `Blocked / deferred` section as a second coverage source and scan it for ids | Given a unit named in a retro's `Blocked / deferred` section but in NO disposition row, when close-owed runs, then it is still OWED. That section is free prose - it is not in `REQUIRED_SECTIONS` and no check reaches it - and RETRO0109's own bullet names future work in the same sentence as the units it accounts for, so reading it would forgive BG0612 the day it reaches terminal |
| AC5 | in `.claude/skills/sdlc-studio/scripts/close_owed.py`, read only the FIRST id out of a `fixed-in:` detail, the `ARTEFACT_ID_RE.search(...).group(1)` shape already in the file. A corpus-only mutant: it drops BG0602 from RETRO0109's multi-id row, which no fixture is obliged to have | Given this repository's own corpus, when the widened check runs, then BG0599 and BG0602 are COVERED by RETRO0109, which names them in a multi-id `fixed-in:` row, and every OTHER owed unit is still reported. The assertion is on those two ids, never on an empty owed set: six units are owed at HEAD, four of them this run's own |
| AC6 | in `.claude/skills/sdlc-studio/scripts/close_owed.py`, stop `cmd_detect` calling the widened `covered_ids` and have it read the batch-only set directly - the wiring a library test cannot see | Given the shipped command rather than the library, when `close_owed.py detect` runs, then it does not name BG0599 or BG0602. The advisory this bug is about is printed by `status` and named by that command, and a library test cannot see either stopping to call the coverage it reads |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
