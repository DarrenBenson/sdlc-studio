# BG0658: testplan derive writes its rows unescaped and reads them back by splitting on a raw pipe, so a mutant naming a piped command is silently truncated

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Verification depth:** functional (authored at plan time as the tier this unit is driven to; the derived half is written by `verify_ac.py depth --write` at delivery, never by hand)
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** US0821 plan review, qa seat, 2026-09-09: measured against the live parsers - a mutant containing a pipe is read back truncated, and the writer reports success.
> **Created:** 2026-09-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`testplan derive` composes each Test Plan row by f-string and `_testplan_rows` reads it back by splitting on a raw pipe. Neither escapes the cell. A mutant naming a piped command - and a shell pipeline is an ordinary thing for a mutant to name - is therefore written as a row with too many cells and read back TRUNCATED at the first pipe, while the writer reports success and markdownlint refuses the file for a column count it never intended.

Found by the plan review of US0821, which was checking whether that story's ruling table reproduced the escaping its sibling already does. It does not exist in either place: this is the live instance, sitting in the very function US0821 extends.

It is the same defect class as BG0637, in a different writer. That one is about `critic._clean` and the three review ledgers; this one is about the Test Plan table. Five separate reproductions of the class have blocked commits in this repository in a single day.

## Steps to Reproduce

1. Author a Test Plan row whose mutant names a piped command.
2. `verify_ac.py testplan derive --unit <id>`, and read the written row: it carries four cells in a three-column table.
3. Read it back with `_testplan_rows` and compare with what was written: the mutant is truncated at the pipe.
4. `npx markdownlint-cli2` on the artefact refuses it with a column-count error.

## Proposed Fix

Escape the cell on write and un-escape on read, on the same terms the coverage rulings table already uses - the pipe substituted, the whitespace folded, and the reader reversing both. The two halves belong together: escaping only the writer leaves every row already on disk unreadable, and un-escaping only the reader corrupts nothing but fixes nothing.

## Acceptance Criteria

- [ ] **AC1** Given a Test Plan row whose mutant names a piped command, when the row is written and read back, then the value round-trips unchanged and the table keeps its three columns
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TestPlanCellEscapingTests::test_a_piped_mutant_round_trips_and_the_table_keeps_its_columns
  - **Verified:** yes (2026-09-09)
- [ ] **AC2** Given a row whose TITLE cell carries a raw pipe, when it is read, then the mutant is the second cell and nothing from the title reaches it. The first cut re-joined cells 1 to -1 whenever a row split into more than three, reading every extra pipe as a mutant that carried one - but a reader cannot tell that from a pipe in the title, and on a title-piped row it fused the title into the mutant and truncated it, so `testplan derive` refused the artefact for restating its own criterion. The re-join is dead for every real row - 0 of 1,032 corpus rows split to anything but three cells, because markdownlint MD056 refuses one that does - and wrong for the only shape it fired on
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TestPlanCellEscapingTests::test_a_title_carrying_a_raw_pipe_leaves_the_mutant_alone
- [ ] **AC3** Given a mutant carrying no pipe at all, when it is written and read, then the bytes are unchanged from today. The paired control: an escaper applied unconditionally rewrites every row in the corpus and its diff would be indistinguishable from the defect
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TestPlanCellEscapingTests::test_a_mutant_with_no_pipe_is_written_byte_identically
  - **Verified:** yes (2026-09-09)

- [ ] **AC4** Given a unit whose authored mutant names a piped command, when the SHIPPED `testplan derive` rewrites its plan, then the row it writes holds three columns and reads back unchanged. Driven through the command, because the writer is the half a hand-built row can never reach: the first cut's three nodes each composed a row by calling the cell helper directly, so reverting the write site left every one green and the repo's own coverage gate named the writer line as executed by no verifier
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TestPlanCellEscapingTests::test_the_shipped_derive_writes_a_piped_mutant_and_reads_it_back
- [ ] **AC5** Given an `unnameable` row whose reason carries an escaped pipe, when the unnameable reader reads it, then the reason is whole and the row is not malformed. It is a second parser of the same table in the same file, and it read the line raw: the reason was truncated at the backslash, and `sprint plan` refused the batch for a row with no reason recorded over a row that had one
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TestPlanCellEscapingTests::test_the_unnameable_reader_uses_the_same_splitter_as_the_row_reader

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/verify_ac.py, delete the pipe escape from the cell writer | Given a Test Plan row whose mutant names a piped command, when the row is written and read back, then the value round-trips unchanged and the table keeps its three columns |
| AC2 | in .claude/skills/sdlc-studio/scripts/verify_ac.py, re-join cells 1 to -1 whenever the row splits into more than three | Given a row whose TITLE cell carries a raw pipe, when it is read, then the mutant is the second cell and nothing from the title reaches it |
| AC3 | in .claude/skills/sdlc-studio/scripts/verify_ac.py, fold whitespace in the cell writer as well as escaping pipes | Given a mutant carrying no pipe at all, when it is written and read, then the bytes are unchanged from today |
| AC4 | in .claude/skills/sdlc-studio/scripts/verify_ac.py, revert the derive row writer to a bare f-string over the raw values | Given a unit whose authored mutant names a piped command, when the SHIPPED testplan derive rewrites its plan, then the row it writes holds three columns and reads back unchanged |
| AC5 | in .claude/skills/sdlc-studio/scripts/verify_ac.py, read the line raw in testplan_unnameable, splitting on every pipe | Given an unnameable row whose reason carries an escaped pipe, when the unnameable reader reads it, then the reason is whole and the row is not malformed |

## Impact

A mutant is the load-bearing half of a test plan: it is what says the criterion can fail. One that is silently truncated is a plan that reads as complete and measures less than it says. The gate that would notice - markdownlint's column count - fires on the artefact rather than on the mutant, so the author is sent to the wrong problem.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-09 | sdlc-studio | Filed |
| 2026-09-09 | Claude Opus 5 | Delivered, then repaired in round two. QA and product both found that AC1's node never drove the writer - reverting the write site passed all 383 tests in the module, and `transition --dry-run` named the writer line as one no verifier executes. AC4 drives the shipped `testplan derive` now. Product found a REGRESSION the first cut introduced: the legacy re-join fused a piped TITLE into the mutant and truncated it, so the command refused the artefact for restating its own criterion - blaming the author for what the reader had done. The re-join is removed, and AC2 now pins the title shape instead. QA found `testplan_unnameable` left on the raw splitter, a second parser of the same table disagreeing with the first about the same row; migrated, pinned by AC5. A Verification depth field and a Test Plan section were both absent and are added |
| 2026-09-09 | Claude Opus 5 | Ruling on the legacy row this fix does NOT read whole: a row whose MUTANT carries a RAW pipe is truncated at it, as it was before this unit. It cannot be read unambiguously - the reader cannot tell that pipe from a column separator - and it cannot exist in a committable tree, because markdownlint MD056 refuses a row whose column count differs from its header. Measured: 0 of this corpus's 1,032 Test Plan rows split to anything but three cells. The pipe is escaped at the write site, which is the one place the ambiguity is decidable. AC2's original promise to read such a row whole is withdrawn on that measurement |
| 2026-09-09 | Claude Opus 5 | Figure corrected. The commit message and a code comment both said half this corpus's shell verifiers are pipelines. Measured: 36 of 370 shell verifiers carry a pipe (10 per cent), and 41 of 600 across every non-pytest verifier (7 per cent). The defect is unchanged - a truncated mutant is a plan that measures less than it says - but the prevalence claim was wrong by five times |
