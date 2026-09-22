# BG0739: close_owed reads the Raised-in-batch stamp by its last token while asserting it reads it exactly as sprint_report does, and the two now genuinely disagree

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py
> **Evidence:** Found by the independent engineering seat reviewing BG0715, 2026-09-22, and reported as out of that unit's Affects rather than fixed there. At round 1 the divergence was stale prose; the seat re-checked at round 2 and reported it had become real, with a table of stamp shapes against both readers showing them differing on `prose + Created in-window` with the window closed.
> **Created:** 2026-09-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`close_owed._raised_in_batch_stamp` takes the last whitespace-separated token of a `Raised-in-batch` stamp, which returns the word `batch` for the prose stamp `file_finding` writes outside a delivery batch. Its docstring states it reads the field `exactly as sprint_report._open_findings reads it, because the two must agree about which run a finding belongs to`. BG0715 changed `_open_findings` to parse the stamp by shape and to fall back to `Created`, so the claim is now false in substance rather than only in wording: against a closed window, `close_owed` attributes nothing for a prose-stamped finding while `_open_findings` attributes those carrying a `Created` inside the window.

## Steps to Reproduce

1. Take a finding stamped `none open - raised outside a delivery batch` carrying a `Created` inside a closed run's window.
2. Ask `sprint_report._open_findings` - it is attributed.
3. Ask `close_owed._raised_in_batch_stamp` - it returns `batch` and the finding is not attributed.
4. Read `close_owed`'s docstring, which says the two read the field identically.

## Proposed Fix

Import the parse rather than restating it: `sprint_report._stamp_timestamp` and `_created_date` are the single reading, and `close_owed` should call them. Then delete the docstring's claim of agreement, because agreement asserted in prose is what allowed the two to drift.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `close_owed._raised_in_batch_stamp` takes the last whitespace-separated token of a `Raised-in-batch` stamp, which returns the word `batch` for the prose stamp...
- [ ] **AC2** The proposed fix lands, pinned by a test: Import the parse rather than restating it: `sprint_report._stamp_timestamp` and `_created_date` are the single reading, and `close_owed` should call them.

## Impact

The close and the ledger disagree about which run a finding belongs to, and one of them carries a docstring promising they cannot. A reader trusting that promise will take either answer as authoritative. The cost is a wrong attribution rather than a crash, which is the kind that survives a long time.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-22 | sdlc-studio | Filed |
