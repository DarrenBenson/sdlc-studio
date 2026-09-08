# BG0637: critic._clean escapes underscores INSIDE code spans, corrupting 655 identifiers across the three review ledgers, and never escapes a backtick

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Verification depth:** functional (authored at plan time as the tier this unit is driven to; the derived half is written by `verify_ac.py depth --write` at delivery, never by hand)
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-09-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_clean`is`value.replace('|','/').replace('\n',' ').strip().replace('_', r'\_')`. The underscore escape is applied to the WHOLE string, including inside code spans, where markdown does not process backslashes - so `_read_rows`is written to the ledger as a literal backslash-underscore and renders corrupted. Measured on the live ledgers: 99 corrupted code spans in critic-verdicts.md, 127 in plan-review-verdicts.md, 429 in repair-record.md, plus 442 double-escaped sequences in repair-record.md - the doubling a comment in the same file claims is avoided. The second half of the same defect is an omission:`_clean` does not escape a backtick, so one stray backtick in a reviewer's finding writes a row with odd backtick parity that fails this repo's own markdownlint. This is the residual under BG0634, whose filed premise (a fixed-width truncation) does not exist; it is filed separately so closing BG0634 NOT-REPRODUCING does not discharge the class.

## Steps to Reproduce

1. `python3 -c "import critic; print(critic._clean('``_read_rows``'))"` prints a backticked span containing literal backslashes.
2. `grep -c '`[^`]*\\_[^`]*`' sdlc-studio/reviews/repair-record.md` returns 429.
3. `grep -c '\\\\_' sdlc-studio/reviews/repair-record.md` returns 442 - the double escape.
4. Record a verdict whose finding text carries one unbalanced backtick; the row reaches the ledger with odd parity and markdownlint MD038 fires on the file.

## Proposed Fix

Escape for the CONTEXT rather than for the string. Split the value on code-span boundaries and apply the underscore escape only OUTSIDE spans, leaving span interiors verbatim - markdown does not interpret emphasis there, which is why the escape was never needed. Make the pass idempotent so re-cleaning an already-escaped value cannot double it. Then balance backticks on the way in: a row whose backtick count is odd is refused at the write, where the author can still fix it, rather than discovered by a pre-commit hook minutes later pointing at the wrong column. The existing corpus rows are corrupt data rather than a code defect; repairing them is a separate decision and should not be smuggled into this fix.

## Acceptance Criteria

- [ ] **AC1** Given free text carrying an underscored identifier INSIDE a code span, when a critic verdict, an evidence row or a repair closure is recorded, then the span's interior reaches the ledger unescaped, because a backslash inside a code span is literal and renders as one
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CleanEscapesForContextTests::test_an_underscore_inside_a_code_span_is_not_escaped
  - **Verified:** no
- [ ] **AC2** Given the same text carrying an underscored identifier OUTSIDE any code span, when it is recorded, then that one IS still escaped. Without this row the likeliest careless implementation - deleting the escape outright, a one-token edit - satisfies AC1 and passes its test
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CleanEscapesForContextTests::test_an_underscore_outside_a_span_is_still_escaped
  - **Verified:** no
- [ ] **AC3** Given a value that has ALREADY been cleaned once, when it is cleaned again, then the result is unchanged. The repair record carries 943 doubled escapes today, which is the largest measured half of this defect and the half no criterion covered
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CleanEscapesForContextTests::test_cleaning_an_already_cleaned_value_changes_nothing
  - **Verified:** no
- [ ] **AC4** Given text carrying a pipe or a newline INSIDE a code span, when it is recorded, then both are still neutralised. The rows are built by f-string rather than by a row joiner, so this function is the only thing standing between a reviewer's piped shell command and a forged column - and leaving span interiors verbatim, as the fix proposes, would put the pipe back
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CleanEscapesForContextTests::test_a_pipe_or_newline_inside_a_span_is_still_neutralised
  - **Verified:** no
- [ ] **AC5** Given free text carrying an ODD number of backticks, when it is recorded, then the write is REFUSED naming the value, rather than the text being silently rewritten. An unbalanced span turns the rest of the row into code and markdownlint then refuses the whole file, and rewriting a reviewer's words to fix it is a worse answer than telling the author while they can still edit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CleanEscapesForContextTests::test_an_odd_backtick_count_is_refused_at_the_write
  - **Verified:** no
- [ ] **AC6** Given free text carrying an EVEN number of backticks, when it is recorded, then every backtick is written through unchanged - the paired control, because a writer that strips or appends backticks satisfies AC5 on its own
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CleanEscapesForContextTests::test_an_even_backtick_count_is_written_through_unchanged
  - **Verified:** no

## Impact

Every identifier a reviewer names in a finding is written wrong, in the three files this project uses as its record of what review found. It is invisible in the terminal and visible in every rendered view, and it compounds: 442 rows are already double-escaped. The backtick half additionally blocks commits - it did so twice during RUN-01M11MEP's close, each time reporting a column hundreds of characters away from the real stray.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/critic.py, revert `_clean` to a single unconditional `replace("_", "\\_")` over the whole value | Given free text carrying an underscored identifier INSIDE a code span, when a critic verdict, an evidence row or a repair closure is recorded, then the span's interior reaches the ledger unescaped, because a backslash inside a code span is literal and renders as one |
| AC2 | in .claude/skills/sdlc-studio/scripts/critic.py, delete the underscore escape from `_clean` altogether | Given the same text carrying an underscored identifier OUTSIDE any code span, when it is recorded, then that one IS still escaped. Without this row the likeliest careless implementation - deleting the escape outright, a one-token edit - satisfies AC1 and passes its test |
| AC3 | in .claude/skills/sdlc-studio/scripts/critic.py, remove the already-escaped test so a backslash-underscore pair is escaped a second time | Given a value that has ALREADY been cleaned once, when it is cleaned again, then the result is unchanged. The repair record carries 943 doubled escapes today, which is the largest measured half of this defect and the half no criterion covered |
| AC4 | in .claude/skills/sdlc-studio/scripts/critic.py, hoist the pipe and newline substitutions into the branch that handles text outside a span | Given text carrying a pipe or a newline INSIDE a code span, when it is recorded, then both are still neutralised. The rows are built by f-string rather than by a row joiner, so this function is the only thing standing between a reviewer's piped shell command and a forged column - and leaving span interiors verbatim, as the fix proposes, would put the pipe back |
| AC5 | in .claude/skills/sdlc-studio/scripts/critic.py, replace the odd-parity refusal with an appended backtick that balances the value silently | Given free text carrying an ODD number of backticks, when it is recorded, then the write is REFUSED naming the value, rather than the text being silently rewritten. An unbalanced span turns the rest of the row into code and markdownlint then refuses the whole file, and rewriting a reviewer's words to fix it is a worse answer than telling the author while they can still edit |
| AC6 | in .claude/skills/sdlc-studio/scripts/critic.py, strip every backtick from the value before writing it | Given free text carrying an EVEN number of backticks, when it is recorded, then every backtick is written through unchanged - the paired control, because a writer that strips or appends backticks satisfies AC5 on its own |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-02 | sdlc-studio | Filed |
| 2026-09-08 | Claude Fable 5.1 | Figures re-measured at the goal review, where the engineering seat found them stale by two to five times. On this tree today: `repair-record.md` carries 571 code spans holding an escaped underscore and 943 double escapes; `critic-verdicts.md` 494 spans and ZERO doubles; `plan-review-verdicts.md` 512 spans and zero doubles. The corruption is 1,577 spans across three ledgers, and the double-escape half is confined to one file - the count in the Summary was taken on 2026-08-28 and the ledgers have grown since |
| 2026-09-08 | Claude Fable 5.1 | This bug reproduced against the plan review that judged it. Recording two independent seats' verdicts wrote six spans markdownlint refuses into `plan-review-verdicts.md` and the commit was blocked: four came from the pipe substitution, which turned a reviewer's quoted table cell into a code span with a space at each end, and two from odd backtick parity, one of them a reviewer quoting the very truncation this bug is about. Both halves of the defect, on the same commit, in the file the tool writes. The rows were repaired by hand to make the tree committable; the fix is this unit |
