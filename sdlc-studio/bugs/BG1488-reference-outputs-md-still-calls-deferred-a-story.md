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

- [ ] **AC1** The behaviour described is corrected: BG0947's QA review (verdict 23493850ddcb-71762c8e) found that reference-outputs.md's 'Any -> Deferred' item under Terminal status transitions (line 134) and...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Read reference-outputs.md lines 134, 275, 745 and 755 and compare with `sdlc_md.TERMINAL_STATUS.`
- [ ] **AC3** The proposed fix lands, pinned by a test: Move Deferred out of the terminal list on the page, and say that the epic cascade counts a Deferred child as closed (a recorded decision) though it is not...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
