# US0675: Every COUNT in Verification depth is read from the mutation ledger, and an unexecuted row SAYS so

> **Status:** Draft
> **Delivers:** CR0548
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Epic:** EP0217
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** Every COUNT in Verification depth is read from the mutation ledger, and an unexecuted row SAYS so
**So that** CR0548 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a unit with a Test Plan and a mutation ledger, when its `Verification depth` is rendered, then every COUNT in it - criteria, declared rows, executed, killed, survived - is read from the ledger, and a figure the ledger does not support cannot appear
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DerivedDepthTests::test_every_count_is_read_from_the_ledger
- [ ] **AC2** Given a unit whose ledger says a row was never executed, when the field is rendered, then it SAYS so by naming the criterion and row - a derived field that can only report success is the defect this replaces, and BG0592 AC13 row 3 is the live case
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DerivedDepthTests::test_an_unexecuted_row_is_named_not_omitted
- [ ] **AC3** Given a unit's criteria, when the field is rendered, then it carries a DERIVED count of how many resolve through a subprocess against how many run in-process, read from the verify report. CR0548's motivating defect was a prose claim of shipped-CLI coverage that did not exist - at 300080d8 on 2026-08-18, repaired the next day at 369d217f - and that claim is PROSE, so deriving only the five mutation counts would leave it in the preserved judgement half untouched. Deriving the entry-point fact is what actually retires it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DerivedDepthTests::test_the_entry_point_split_is_derived_from_the_verify_report
- [ ] **AC4** Given a unit ALL of whose criteria run in-process, when the field is rendered, then the derived entry-point count says zero through the CLI rather than omitting the line - the paired control, because a renderer that only ever reports coverage it found cannot contradict a false claim of coverage
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DerivedDepthTests::test_an_all_in_process_unit_reports_zero_cli_coverage
- [ ] **AC5** Given a unit with NO ledger entries at all, when the field is rendered, then it reports the evidence as ABSENT rather than rendering zeros - nought executed and nothing recorded are different facts, and a reader who cannot tell them apart cannot judge the unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DerivedDepthTests::test_an_absent_ledger_is_reported_not_rendered_as_zero

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
| 2026-08-21 | sdlc-studio | Goal review round 2: the pinned regression case named a commit that holds the REPAIR, not the defect, and the ledger it would read is gitignored - re-pinned as a named fixture. Exemption taxonomy added, without which the check refuses correct units |
