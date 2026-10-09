# US1008: A sprint-checklist waiver scoped to a unit in one run answers that unit's part of a row and nothing else

> **Status:** Draft
> **Delivers:** CR0614
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_checklist_waiver_unit_scope.py, changelog.d/US1008.md
> **Epic:** EP0279
> **Points:** 5
> **Depends on:** US1007, US1010, BG0997
> **Persona:** Maya Okafor

## User Story

**As** a founder-engineer whose closing-review row is wrong about one unit and right about the rest
**I want** to waive the row for that one unit in this run
**So that** another unit the row holds open, or the same unit in a later run, still holds it

## Acceptance Criteria

- **AC1:** Given run RUN-AAAA1111 whose closing-review row is open on BG-01JQK3F8 alone and a waiver recorded with the dashed spelling `rule:sprint-checklist:closing-review:RUN-AAAA1111:BG-01JQK3F8`, when `sprint_report.py checklist --format json` runs, then the row reads waived and names that waiver.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_checklist_waiver_unit_scope.py::UnitScopedChecklistWaiverTests::test_a_unit_waiver_answers_a_row_only_that_unit_holds_open
- **AC2:** Given the closing-review row open on BG0460 and US0002 in RUN-AAAA1111 and a waiver naming RUN-AAAA1111 and BG0460 only, when the checklist runs, then the row stays outstanding and its detail names US0002 as still open and BG0460 as waived.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_checklist_waiver_unit_scope.py::UnitScopedChecklistWaiverTests::test_a_second_open_unit_still_holds_the_row
- **AC3:** Given a waiver naming RUN-AAAA1111 and BG0460 and a later run RUN-BBBB2222 whose closing-review row is open on BG0460 again, when the checklist runs for RUN-BBBB2222, then the row stays outstanding.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_checklist_waiver_unit_scope.py::UnitScopedChecklistWaiverTests::test_the_same_unit_in_a_later_run_stays_outstanding
- **AC4:** Given the subject `rule:sprint-checklist:closing-review:RUN-01M4APNQ` on a row that also takes a unit scope, when it is recorded and the checklist runs for that run, then it is read as a run scope and answers the whole row.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_checklist_waiver_unit_scope.py::UnitScopedChecklistWaiverTests::test_a_run_tail_on_a_unit_scoped_row_reads_as_a_run
- **AC5:** Given the subject `rule:sprint-checklist:retro:RUN-AAAA1111:US0001`, when `decisions.py waive` runs, then it exits 2 naming closing-review and tick-verification as the rows that take a unit scope, and writes nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_checklist_waiver_unit_scope.py::UnitScopedChecklistWaiverTests::test_a_unit_tail_on_a_run_level_row_is_refused

## Notes

- Release: later (D0355 breakdown G5, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the unit tail is accepted at record time but never compared with the units holding the row open; or it is compared as stored (lower-cased, dash kept) rather than through the BG0997 matcher.
- AC2 must fail on: any one unit-scoped waiver for the item clears the whole row.
- AC3 must fail on: a unit-scoped waiver is matched on the unit alone, so it answers that unit in every later run, which is the permanent waiver again at unit grain.
- AC4 must fail on: the tail is classified by `sdlc_md.is_v3_id`, which accepts a run id, so it is read as a unit that holds nothing open and answers nothing.
- AC5 must fail on: a unit tail is accepted on every checklist row, including the run-level ones no unit holds open.
- Grammar: `<item>[:<run id>[:<unit id>]]`. A unit is accepted only after a run, so a unit-scoped waiver is bound to the run it was written for (panel change 7). The first tail segment is always read as a run, by run_state's grammar and the `RUN-` prefix (panel change 8). A bare `closing-review:BG0460` is therefore refused at record time as a tail that names no run, by US-1's check.
- Only two rows name the units that hold them open: closing-review (`rejected + unreviewed`, sprint_report.py:1170) and tick-verification (`contradicted`, sprint_report.py:1402). Each CHECKLIST entry declares whether it takes a unit scope, and `scope_tail_error` reads that declaration.
- Each such resolver returns its open units beside (state, value, detail), in every outstanding branch. Closing-review's 'none recorded' branch holds every batch unit open. A row with no unit list cannot be unit-waived, which fails towards holding.
- The row is waived only when every open unit is covered. Otherwise it stays outstanding and its detail lists both sets.
- This story extends the tail grammar `sprint_report` publishes and the literal `--subject` help. US-4's test, which composes the expected help from the published grammar, then holds the two together.
- Deferred to later by the panel: the run scope removes the live harm, and a waived row's detail already names every open unit (US-1 AC1).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G5 after the refine panel's review |
