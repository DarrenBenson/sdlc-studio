# BG1676: reconcile stops on an index that is not UTF-8 without naming the file or how to fix it

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile_index_not_utf8.py, changelog.d/BG1676.md, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Evidence:** Run twenty-one lane T builder (BG0956) noticed it at reconcile.py:620; reproduced 2026-11-21 in a throwaway repository: reconcile detect printed the bare codec error.
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T10:13:49Z

## Summary

reconcile.py `_dead_row_links` reads every index with strict UTF-8, so one `_index.md` holding a byte such as 0xe9 (an index hand-edited in a non-UTF-8 editor) stops reconcile detect, reconcile apply and transition set with only "Error: 'utf-8' codec can't decode byte 0xe9 in position 86". The message names neither the index nor a remedy.

## Steps to Reproduce

In a fresh git repository, write sdlc-studio/bugs/_index.md with a table row whose title holds the byte 0xe9, then run reconcile.py detect --root <repo>. It prints the codec error above and names no file.

## Proposed Fix

Read index files through `sdlc_md.read_text_safe`, or catch UnicodeDecodeError in `_dead_row_links`, and refuse naming the index path, the line and the remedy (save it as UTF-8), as `persona_resolve` does for a seat card. Pin it with a test that writes a non-UTF-8 index.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: reconcile.py `_dead_row_links` reads every index with strict UTF-8, so one `_index.md` holding a byte such as 0xe9 (an index hand-edited in a non-UTF-8 editor)...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: In a fresh git repository, write sdlc-studio/bugs/_index.md with a table row whose title holds the byte 0xe9, then run reconcile.py detect --root <repo>.
- [ ] **AC3** The proposed fix lands, pinned by a test: Read index files through `sdlc_md.read_text_safe`, or catch UnicodeDecodeError in `_dead_row_links`, and refuse naming the index path, the line and the remedy...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
