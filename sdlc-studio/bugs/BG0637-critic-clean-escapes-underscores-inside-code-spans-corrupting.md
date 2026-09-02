# BG0637: critic._clean escapes underscores INSIDE code spans, corrupting 655 identifiers across the three review ledgers, and never escapes a backtick

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
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

- [ ] **AC1** The behaviour described is corrected: `_clean`is`value.replace('|','/').replace('\n',' ').strip().replace('_', r'\_')`.
- [ ] **AC2** The proposed fix lands, pinned by a test: Escape for the CONTEXT rather than for the string.

## Impact

Every identifier a reviewer names in a finding is written wrong, in the three files this project uses as its record of what review found. It is invisible in the terminal and visible in every rendered view, and it compounds: 442 rows are already double-escaped. The backtick half additionally blocks commits - it did so twice during RUN-01M11MEP's close, each time reporting a column hundreds of characters away from the real stray.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-02 | sdlc-studio | Filed |
