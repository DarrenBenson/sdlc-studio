# BG1488: reference-outputs.md still calls Deferred a story terminal status at lines 134, 745 and 755, against its own Story row and sdlc_md.TERMINAL_STATUS

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-outputs.md, .claude/skills/sdlc-studio/scripts/tests/test_status_vocab_doc.py, changelog.d/BG1488.md
> **Evidence:** sdlc-studio/reviews/verdicts/BG0947/23493850ddcb-71762c8e.txt
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T23:35:41Z

## Summary

BG0947's QA review (verdict 23493850ddcb-71762c8e) found that reference-outputs.md's 'Any -> Deferred' item under Terminal status transitions (line 134) and the cascade sentences at 745 and 755 call Deferred a story terminal, while the Story row BG0947 corrected (line 275) and `sdlc_md.TERMINAL_STATUS` do not. transition.py's `_STORY_TICKED` also counts Deferred as ticked for the epic cascade, so the page should say which reading each rule uses rather than calling Deferred terminal outright. git log -S puts the line 745 sentence at de3c3563.

## Steps to Reproduce

Read reference-outputs.md lines 134, 275, 745 and 755 and compare with `sdlc_md.TERMINAL_STATUS.`

## Proposed Fix

Move Deferred out of the terminal list on the page, and say that the epic cascade counts a Deferred child as closed (a recorded decision) though it is not terminal; extend `test_status_vocab_doc.py` to the cascade sentences.

## Acceptance Criteria

- [ ] **AC1** Given reference-outputs.md, when its Terminal status transitions list and its Story Completion Cascade prose are compared with `sdlc_md.TERMINAL_STATUS`, then no sentence calls Deferred a story terminal status, and the cascade text says a Deferred child is counted as closed for the epic cascade though it is not terminal. Fails on: Deferred listed as terminal in the transitions list or either cascade sentence, against the page's own Story row.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status_vocab_doc.py::StatusVocabDocTests::test_no_prose_calls_deferred_a_story_terminal_status
- [ ] **AC2** Given a copy of the corrected page with Deferred put back in the cascade's terminal list, when the same comparison runs over the copy, then it fails naming story and Deferred. Fails on: a check that reads only the status table and so passes the old prose.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status_vocab_doc.py::StatusVocabDocTests::test_deferred_restored_to_the_cascade_prose_is_named

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
