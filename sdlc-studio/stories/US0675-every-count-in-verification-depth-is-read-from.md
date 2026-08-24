# US0675: Every COUNT in Verification depth is read from the mutation ledger, and an unexecuted row SAYS so

> **Status:** Done
> **Delivers:** CR0548
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Verification depth:** functional [[derived: criteria 5; plan rows 5; executed 5; killed 5; survived 0; not-run 0; entry point 5 of 5 criteria through the shipped CLI, 0 in-process | fp 1eac765f2fb5 ]] (every count is asserted to MOVE with the ledger rather than merely to be present, and the ledger is written by `mutation.register_mutant` rather than hand-built as JSON. NOT covered: the gate half that refuses a hand-edit inside the delimiters - that is US0676, which lands in the gate-lane commit)
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Epic:** EP0217
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** Every COUNT in Verification depth is read from the mutation ledger, and an unexecuted row SAYS so
**So that** CR0548 is delivered by work that can be planned and checked

## Acceptance Criteria

- [x] **AC1** Given a unit with a Test Plan and a mutation ledger, when its `Verification depth` is rendered, then every COUNT in it - criteria, declared rows, executed, killed, survived - is read from the ledger, and a figure the ledger does not support cannot appear
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DerivedDepthTests::test_every_count_is_read_from_the_ledger
  - **Verified:** yes (2026-08-21)
- [x] **AC2** Given a unit whose ledger says a row was never executed, when the field is rendered, then it SAYS so by naming the criterion and row - a derived field that can only report success is the defect this replaces, and BG0592 AC13 row 3 is the live case
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DerivedDepthTests::test_an_unexecuted_row_is_named_not_omitted
  - **Verified:** yes (2026-08-21)
- [x] **AC3** Given a unit's criteria, when the field is rendered, then it carries a DERIVED count of how many resolve through a subprocess against how many run in-process, derived by the same `_enters_the_lane` detector `lane-check` uses, over each criterion's own named test node. CR0548's motivating defect was a prose claim of shipped-CLI coverage that did not exist - at 300080d8 on 2026-08-18, repaired the next day at 369d217f - and that claim is PROSE, so deriving only the five mutation counts would leave it in the preserved judgement half untouched. Deriving the entry-point fact is what actually retires it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DerivedDepthTests::test_the_entry_point_split_is_derived_per_criterion
  - **Verified:** yes (2026-08-21)
- [x] **AC4** Given a unit ALL of whose criteria run in-process, when the field is rendered, then the derived entry-point count says zero through the CLI rather than omitting the line - the paired control, because a renderer that only ever reports coverage it found cannot contradict a false claim of coverage
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DerivedDepthTests::test_an_all_in_process_unit_reports_zero_cli_coverage
  - **Verified:** yes (2026-08-21)
- [x] **AC5** Given a unit with NO ledger entries at all, when the field is rendered, then it reports the evidence as ABSENT rather than rendering zeros - nought executed and nothing recorded are different facts, and a reader who cannot tell them apart cannot judge the unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DerivedDepthTests::test_an_absent_ledger_is_reported_not_rendered_as_zero
  - **Verified:** yes (2026-08-21)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `verify_ac.py`, replace `verdicts.count("killed")` with `len(rows)` in `depth_facts`, so the count no longer comes from the ledger's own verdicts | Given a unit with a Test Plan and a mutation ledger, when its `Verification depth` is rendered, then every COUNT in it - criteria, declared rows, executed, killed, survived - is read from the ledger, and a figure the ledger does not support cannot appear |
| AC2 | in `verify_ac.py`, drop the `NOT RUN` branch from `render_depth` | Given a unit whose ledger says a row was never executed, when the field is rendered, then it SAYS so by naming the criterion and row - a derived field that can only report success is the defect this replaces, and BG0592 AC13 row 3 is the live case |
| AC3 | in `verify_ac.py`, return `through_cli = located` from `_entry_point_split` | Given a unit's criteria, when the field is rendered, then it carries a DERIVED count of how many resolve through a subprocess against how many run in-process, derived by the same `_enters_the_lane` detector `lane-check` uses, over each criterion's own named test node. CR0548's motivating defect was a prose claim of shipped-CLI coverage that did not exist - at 300080d8 on 2026-08-18, repaired the next day at 369d217f - and that claim is PROSE, so deriving only the five mutation counts would leave it in the preserved judgement half untouched. Deriving the entry-point fact is what actually retires it |
| AC4 | in `verify_ac.py`, emit the entry-point clause from `render_depth` only when `through_cli` is non-zero | Given a unit ALL of whose criteria run in-process, when the field is rendered, then the derived entry-point count says zero through the CLI rather than omitting the line - the paired control, because a renderer that only ever reports coverage it found cannot contradict a false claim of coverage |
| AC5 | in `verify_ac.py`, drop the `ledger_absent` branch from `render_depth` | Given a unit with NO ledger entries at all, when the field is rendered, then it reports the evidence as ABSENT rather than rendering zeros - nought executed and nothing recorded are different facts, and a reader who cannot tell them apart cannot judge the unit |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
| 2026-08-21 | sdlc-studio | Goal review round 2: the pinned regression case named a commit that holds the REPAIR, not the defect, and the ledger it would read is gitignored - re-pinned as a named fixture. Exemption taxonomy added, without which the check refuses correct units |
| 2026-08-21 | sdlc-studio | AC3 named the verify report as the source of the entry-point split. The report stores no verifier expression for a PASSING criterion (`write_report` keeps `passed` as bare ids and expressions only inside `failures`), so that source cannot supply the fact. Re-pointed at `_enters_the_lane`, the detector `lane-check` already uses. The falsifiable claim is unchanged |
