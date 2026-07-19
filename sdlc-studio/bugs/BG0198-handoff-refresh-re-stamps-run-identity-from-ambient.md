# BG0198: handoff.refresh re-stamps run identity from ambient run state, not the run being refreshed

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/handoff.py
> **Created:** 2026-07-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

handoff.refresh scopes the UNIT LIST via build(root, batch=batch) but `_meta_lines` and the appetite block read `run_state.read(root)` unconditionally. Refreshing a closed run's handoff while a different run is open therefore rewrites its Run/Outcome/Goal/Batch source lines with the OTHER run's identity, writes `handoff_remaining` into that run's state, and overwrites the shared worklist. The docstring promises 'same id, same index row, same retro link' - the run identity should be in that set, because a handoff belongs to a run. Found by the independent review of RUN-01KXVD74. NOT reachable through `sprint close --apply-signoff`: `open_run` resets to `_blank()` on a spent run, clearing the recorded `handoff`, so the tail skips the refresh. It is a live footgun for a hand-run or out-of-band refresh - it overwrote the shipped HO-0007 twice during that sprint.

## Steps to Reproduce

1. Write a handoff HO0001 whose meta names RUN-AAAAAAAA. 2. Open a different run RUN-BBBBBBBB in run-state.json. 3. Call handoff.refresh(root, 'HO-0001', batch=['US0101']) - the same scoped shape `_apply_signoff_tail` uses. 4. Read the file: Run/Outcome/Goal now describe RUN-BBBBBBBB and Batch source flipped to 'argument'.

## Proposed Fix

Pass the closing run's identity into refresh (or have it read the handoff's own recorded Run line) so `_meta_lines` describes the run the document belongs to. Guard `handoff_remaining` and the worklist write the same way. Consider also appending a Revision History row for the rewrite, and keeping 'Batch source' as recorded rather than flipping it to 'argument' on every refresh.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-18 | sdlc-studio | Filed |
