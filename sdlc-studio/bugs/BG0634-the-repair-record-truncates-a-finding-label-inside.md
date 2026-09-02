# BG0634: the repair record truncates a finding label INSIDE a code span, leaving an unbalanced backtick that fails the repo's own markdownlint and blocks the commit

> **Status:** Won't Fix
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-08-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`critic.py repair` abbreviates each closure's finding label to a fixed width before writing it. The cut is taken on character count with no regard for markdown, so a label whose backticked span straddles the boundary is written with its opening backtick and no closing one. Every subsequent backtick on that row then pairs one position out, and markdownlint reports MD038 against text that is not the defect - this close saw four false MD038 hits at column 800+ while the actual stray was hundreds of characters earlier. Because the guard runs in pre-commit rather than at the write, the failure surfaces minutes later against a file the author is told not to hand-edit.

## Steps to Reproduce

1. Record a verdict whose findings contain backticked code spans near the truncation width, e.g. a list like `0`, `0.0`, `[]`, `{}`.
2. `critic.py repair --unit <id> --closed-file <doc>`, which exits 0.
3. `npx markdownlint-cli2 sdlc-studio/reviews/repair-record.md` reports MD038, and the reported columns point at innocent spans rather than the unclosed one.
4. `python3 -c "print(open('sdlc-studio/reviews/repair-record.md').read().splitlines()[N].count(chr(96)) % 2)"` prints 1 - the real symptom.

## Proposed Fix

Truncate on a markdown-safe boundary: never cut inside a code span. Either extend the cut to the span's closing backtick, or drop the partial span and end the label before it. Balance is the invariant worth asserting - a written row's backtick count must be even - because that is checkable at the write, where the author can still act on it, rather than in a pre-commit hook that reports the wrong column. The same cut is applied to verdict issues, so the guard belongs beside the shared writer rather than in one caller.

## Acceptance Criteria

- [ ] **AC1** Given a closure whose finding label carries a code span straddling the truncation width, when `critic.py repair`writes the row as a SUBPROCESS, then the written line's backtick count is EVEN ||| pytest .claude/skills/sdlc-studio/scripts/tests/`test_critic.py`::LabelTruncationTests::`test_a_truncated_label_never_leaves_an_unclosed_code_span`- [ ] **AC2** Given a label with no code span at all, when the same command runs, then the label is truncated exactly as it is today - the guard must not change the ordinary case ||| pytest .claude/skills/sdlc-studio/scripts/tests/`test_critic.py`::LabelTruncationTests::`test_a_plain_label_truncates_unchanged`- [ ] **AC3** Given the same closure, when the written ledger is linted, then markdownlint reports no MD038 against the row ||| pytest .claude/skills/sdlc-studio/scripts/tests/`test_critic.py`::LabelTruncationTests::`test_the_written_row_lints_clean`

## Resolution

**NOT REPRODUCING at HEAD, closed 2026-09-02 after re-running the Steps to Reproduce.**

The filed premise was a fixed-width truncation on the repair write path. There is none, and
`git log -S`finds none there has ever been.`record_repair`writes through`_append_row(..., _clean(text), ...)`with no slicing, and every`[:60]`and`[:100]`in`critic.py` (lines 433, 1117, 1275 and 3138) is a stderr or console message that reaches no
file.
Measured on the live ledger: 151 rows, longest **28,517 characters**, and **zero rows with an
odd backtick count**. Step 4's symptom is absent.

What I actually observed and mis-diagnosed was an unbalanced backtick in my own closure text,
which shifted every subsequent code span on that line and made the label LOOK cut. The real
defect underneath is `_clean`at`critic.py`:165, which escapes `|`, newline and `_` but never a
backtick - and escapes `_` blindly inside code spans, corrupting 99 / 127 / 429 identifiers
across the three ledgers with 442 already double-escaped.

**That residue is carried as BG0637, not discharged here.** Closing this artefact must not close
the class: the premise is false, the neighbouring defect is real, and they are different bugs.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-28 | sdlc-studio | Filed |
