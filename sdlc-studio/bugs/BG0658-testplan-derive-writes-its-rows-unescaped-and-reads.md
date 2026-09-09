# BG0658: testplan derive writes its rows unescaped and reads them back by splitting on a raw pipe, so a mutant naming a piped command is silently truncated

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
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
- [ ] **AC2** Given a row written before this fix, carrying an unescaped pipe already on disk, when it is read, then it is read whole rather than truncated - escaping the writer alone would leave every existing row unreadable
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TestPlanCellEscapingTests::test_a_row_written_before_the_fix_is_still_read_whole
  - **Verified:** yes (2026-09-09)
- [ ] **AC3** Given a mutant carrying no pipe at all, when it is written and read, then the bytes are unchanged from today. The paired control: an escaper applied unconditionally rewrites every row in the corpus and its diff would be indistinguishable from the defect
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TestPlanCellEscapingTests::test_a_mutant_with_no_pipe_is_written_byte_identically
  - **Verified:** yes (2026-09-09)

## Impact

A mutant is the load-bearing half of a test plan: it is what says the criterion can fail. One that is silently truncated is a plan that reads as complete and measures less than it says. The gate that would notice - markdownlint's column count - fires on the artefact rather than on the mutant, so the author is sent to the wrong problem.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-09 | sdlc-studio | Filed |
