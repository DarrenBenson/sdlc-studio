# BG0637: critic._clean escapes underscores INSIDE code spans, corrupting 655 identifiers across the three review ledgers, and never escapes a backtick

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Verification depth:** functional (authored at plan time as the tier this unit is driven to; the derived half is written by `verify_ac.py depth --write` at delivery, never by hand)
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py
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
  - **Verified:** yes (2026-09-09)
- [ ] **AC2** Given the same text carrying an underscored identifier OUTSIDE any code span, when it is recorded, then that one IS still escaped. Without this row the likeliest careless implementation - deleting the escape outright, a one-token edit - satisfies AC1 and passes its test
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CleanEscapesForContextTests::test_an_underscore_outside_a_span_is_still_escaped
  - **Verified:** yes (2026-09-09)
- [ ] **AC3** Given a value that has ALREADY been cleaned once, when it is cleaned again, then the result is unchanged. The repair record carries 943 doubled escapes today, which is the largest measured half of this defect and the half no criterion covered
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CleanEscapesForContextTests::test_cleaning_an_already_cleaned_value_changes_nothing
  - **Verified:** yes (2026-09-09)
- [ ] **AC4** Given text carrying a pipe or a newline INSIDE a code span, when it is recorded, then both are still neutralised. The rows are built by f-string rather than by a row joiner, so this function is the only thing standing between a reviewer's piped shell command and a forged column - and leaving span interiors verbatim, as the fix proposes, would put the pipe back
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CleanEscapesForContextTests::test_a_pipe_or_newline_inside_a_span_is_still_neutralised
  - **Verified:** yes (2026-09-09)
- [ ] **AC5** Given free text carrying an ODD number of backticks, when it is recorded, then the write is REFUSED naming the value, rather than the text being silently rewritten. An unbalanced span turns the rest of the row into code and markdownlint then refuses the whole file, and rewriting a reviewer's words to fix it is a worse answer than telling the author while they can still edit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CleanEscapesForContextTests::test_an_odd_backtick_count_is_refused_at_the_write
  - **Verified:** yes (2026-09-09)
- [ ] **AC6** Given free text carrying an EVEN number of backticks, when it is recorded, then every backtick is written through unchanged - the paired control, because a writer that strips or appends backticks satisfies AC5 on its own
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CleanEscapesForContextTests::test_an_even_backtick_count_is_written_through_unchanged
  - **Verified:** yes (2026-09-09)

- [ ] **AC7** Given an underscored identifier inside a DOUBLE-backtick code span, when it is recorded, then that span's interior also reaches the ledger unescaped. Markdown pairs a run of N backticks with the next run of exactly N, and a delimiter definition that knows only a single pair reads the two backticks OPENING the span as a complete empty span - which is the artefact's own first reproduction, and it survived the first fix
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CleanSpanWidthAndRefusalTests::test_a_double_backtick_span_interior_is_left_alone
- [ ] **AC8** Given a repair whose closures answer two rejections and whose LATER row carries an unwritable value, when it is recorded, then NOTHING is written. The repair record is append-only, so a row written before the refusal cannot be taken back: the command exited 2 with one row committed, and the corrected re-run duplicated it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CleanSpanWidthAndRefusalTests::test_a_refused_repair_leaves_no_row_behind
- [ ] **AC9** Given a value longer than the excerpt whose stray backtick falls beyond it, when the write is refused, then the message quotes the text AROUND the stray and says how long the value is. Seventy-one per cent of this repo's review-ledger findings cells run past 120 characters, and in every corpus row this rule refuses the first 120 hold no backtick at all - so a leading excerpt named a remedy over text that could not be the fault, which is the complaint this bug's own Impact section makes about the old failure
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CleanSpanWidthAndRefusalTests::test_the_refusal_quotes_the_stray_backtick_and_the_value
- [ ] **AC10** Given `plan_review.py record` invoked with an unwritable `--notes`, when it runs, then it prints a named refusal and exits 2 rather than a Python traceback. Every sibling write path answers a refusal that way, and reference-config.md tells the user to PREFER this command over `critic.py record --phase plan-review`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py::RecordRefusalTests::test_an_unwritable_note_is_a_named_refusal_not_a_traceback
- [ ] **AC11** Given a value carrying a backslash-escaped backtick, when it is recorded, then it is written through rather than refused. An escaped backtick is a literal one and never opened a span, so counting it toward parity refused a value markdown holds and told the author to close a span that was never open
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CleanSpanWidthAndRefusalTests::test_an_escaped_backtick_is_not_a_delimiter

## Impact

Every identifier a reviewer names in a finding is written wrong, in the three files this project uses as its record of what review found. It is invisible in the terminal and visible in every rendered view, and it compounds: 442 rows are already double-escaped. The backtick half additionally blocks commits - it did so twice during RUN-01M11MEP's close, each time reporting a column hundreds of characters away from the real stray.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/critic.py, revert `_clean` to a single unconditional `replace("_", "\\_")` over the whole value | Given free text carrying an underscored identifier INSIDE a code span, when a critic verdict, an evidence row or a repair closure is recorded, then the span's interior reaches the ledger unescaped, because a backslash inside a code span is literal and renders as one |
| AC2 | in .claude/skills/sdlc-studio/scripts/critic.py, delete the underscore escape from `_clean` altogether | Given the same text carrying an underscored identifier OUTSIDE any code span, when it is recorded, then that one IS still escaped. Without this row the likeliest careless implementation - deleting the escape outright, a one-token edit - satisfies AC1 and passes its test |
| AC3 | in .claude/skills/sdlc-studio/scripts/critic.py, remove the already-escaped test so a backslash-underscore pair is escaped a second time | Given a value that has ALREADY been cleaned once, when it is cleaned again, then the result is unchanged. The repair record carries 943 doubled escapes today, which is the largest measured half of this defect and the half no criterion covered |
| AC4 | in .claude/skills/sdlc-studio/scripts/critic.py, delete the pipe substitution so a pipe inside a code span survives | Given text carrying a pipe or a newline INSIDE a code span, when it is recorded, then both are still neutralised. The rows are built by f-string rather than by a row joiner, so this function is the only thing standing between a reviewer's piped shell command and a forged column - and leaving span interiors verbatim, as the fix proposes, would put the pipe back |
| AC5 | in .claude/skills/sdlc-studio/scripts/critic.py, replace the odd-parity refusal with an appended backtick that balances the value silently | Given free text carrying an ODD number of backticks, when it is recorded, then the write is REFUSED naming the value, rather than the text being silently rewritten. An unbalanced span turns the rest of the row into code and markdownlint then refuses the whole file, and rewriting a reviewer's words to fix it is a worse answer than telling the author while they can still edit |
| AC6 | in .claude/skills/sdlc-studio/scripts/critic.py, strip every backtick from the value before writing it | Given free text carrying an EVEN number of backticks, when it is recorded, then every backtick is written through unchanged - the paired control, because a writer that strips or appends backticks satisfies AC5 on its own |

| AC7 | in .claude/skills/sdlc-studio/scripts/critic.py, narrow the code-span delimiter pattern back to a single backtick | Given an underscored identifier inside a DOUBLE-backtick code span, when it is recorded, then that span's interior also reaches the ledger unescaped |
| AC8 | in .claude/skills/sdlc-studio/scripts/critic.py, append each repair row inside the per-rejection loop, so a later refusal leaves the earlier row written | Given a repair whose closures answer two rejections and whose LATER row carries an unwritable value, when it is recorded, then NOTHING is written |
| AC9 | in .claude/skills/sdlc-studio/scripts/critic.py, quote the value's first 120 characters instead of the text around the stray backtick | Given a value longer than the excerpt whose stray backtick falls beyond it, when the write is refused, then the message quotes the text AROUND the stray and says how long the value is |
| AC10 | in .claude/skills/sdlc-studio/scripts/plan_review.py, delete the try/except around record_review so the refusal escapes as a traceback | Given `plan_review.py record` invoked with an unwritable --notes, when it runs, then it prints a named refusal and exits 2 rather than a Python traceback |
| AC11 | in .claude/skills/sdlc-studio/scripts/critic.py, drop the not-a-backslash lookbehind from the delimiter pattern | Given a value carrying a backslash-escaped backtick, when it is recorded, then it is written through rather than refused |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-02 | sdlc-studio | Filed |
| 2026-09-08 | Claude Fable 5.1 | Figures re-measured at the goal review, where the engineering seat found them stale by two to five times. On this tree today: `repair-record.md` carries 571 code spans holding an escaped underscore and 943 double escapes; `critic-verdicts.md` 494 spans and ZERO doubles; `plan-review-verdicts.md` 512 spans and zero doubles. The corruption is 1,577 spans across three ledgers, and the double-escape half is confined to one file - the count in the Summary was taken on 2026-08-28 and the ledgers have grown since |
| 2026-09-08 | Claude Fable 5.1 | This bug reproduced against the plan review that judged it. Recording two independent seats' verdicts wrote six spans markdownlint refuses into `plan-review-verdicts.md` and the commit was blocked: four came from the pipe substitution, which turned a reviewer's quoted table cell into a code span with a space at each end, and two from odd backtick parity, one of them a reviewer quoting the very truncation this bug is about. Both halves of the defect, on the same commit, in the file the tool writes. The rows were repaired by hand to make the tree committable; the fix is this unit |
| 2026-09-08 | Claude Fable 5.1 | Third reproduction in one day, now in the DELIVERY ledger: a reviewer quoting a bare word inside a code span with a trailing space produced a row markdownlint refuses, and the commit was blocked again. Same writer, same absent parity and spacing check |
| 2026-09-09 | Claude Fable 5.1 | A FOURTH reproduction, and a shape the earlier three did not show: a closure whose finding key was a 60-character quote was cut inside a code span, leaving an unclosed backtick in the repair record and blocking the commit. The other three came from a reviewer's own text; this one came from a caller TRUNCATING text before handing it to the writer. Both belong to AC5: the writer must refuse odd parity whatever produced it, rather than trusting that its callers hand it balanced text |
| 2026-09-09 | Claude Fable 5.1 | A FIFTH reproduction on the same day, and the plainest one: a reviewer quoting the withdrawal sentinel literal, whose trailing space is part of the value, produced a code span markdownlint refuses. There is no way to write that literal in a ledger row today, so the writer is refusing to record a fact about its own sibling's contract |
| 2026-09-09 | Claude Fable 5.1 | SIXTH and SEVENTH reproductions, both from one review round: a reviewer quoting an http verifier with a trailing ellipsis, and another quoting a level-two heading marker whose trailing space is the whole point of the quote. Every one of the seven this week is a reviewer or a caller writing a value the ledger cannot hold, and the writer accepting it. Seven blocked commits is now the measured cost of this bug |
| 2026-09-09 | Claude Fable 5.1 | Delivered. AC4's row was corrected at delivery: it named hoisting the substitutions into the outside-a-span branch, and the fix keeps them in one place ABOVE the span walk rather than inside it, so there is no such branch to hoist into. The edit that reddens AC4 is deleting the pipe substitution, which is what the row now names. The refusal shape was also settled here rather than left to the implementation: an odd backtick count raises, and the message says why it is not balanced - rewriting a reviewer's words is worse than refusing them, and refusing also catches the caller that truncated a quotation mid-span, which balancing would have papered over |
| 2026-09-09 | Claude Opus 5 | Round two of delivery review. Three seats rejected in the same place: the fix knew what a code span was only for a SINGLE pair of backticks, and its refusal fired from INSIDE the per-rejection write loop. AC7 to AC11 added, one per blocking finding, each with a mutant killed: a double-backtick span was still corrupted (the artefact's own Steps to Reproduce 1, live after the first fix); a refused repair answering two rejections left the earlier row in an append-only record, so the corrected re-run duplicated it; the message quoted the value's first 120 characters, which in every corpus row this rule refuses holds no backtick at all; `plan_review.py record` met the new refusal with a traceback; and a backslash-escaped backtick, which needs no partner, was counted toward parity. AC5's own test was strengthened to pin the naming-the-value half, which was revertible with the suite green. Figures re-measured today over the three ledgers: 1,136 doubled escapes (1,134 of them in repair-record.md) and 2,987 escaped underscores inside code spans by a single-pair span walk. The fix backfills none of them, which is what the Proposed Fix says. The MD038 trailing-space class - four of this artefact's seven recorded reproductions - is NOT covered by any criterion here and is filed as BG0659 rather than left unrecorded |
