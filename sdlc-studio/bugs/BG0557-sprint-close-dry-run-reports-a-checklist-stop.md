# BG0557: sprint close --dry-run reports a checklist STOP the real close does not

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-08-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio-authoring-session; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

During RUN-01KZF9AF's close, `sprint close --retro RETRO0099 --dry-run` reported `STOP checklist: 1 compulsory checklist item(s) unanswered` on three consecutive runs. The real close, run immediately afterwards against the same tree with no edits in between, reported `checklist: ok - 22 compulsory item(s), none outstanding`. Calling `sprint._close_checklist(root, retro, state)` directly also returned ok=True, and `sprint_report.checklist()` returned ok=True with outstanding=[] under both the bare and the `unit_ids`-passing call the two paths use.

## Relationship to BG0460

The filer warned this may duplicate BG0460, and it does not. BG0460 (Fixed) was about a step
reported as NEITHER refusing nor unevaluated, and about a count claiming seven steps over a
ten-step chain - both defects in how the dry run DESCRIBES its own pass. This one is that the
dry run and the real close reach different verdicts on the same tree, which is a defect in what
the dry run computes rather than in how it reports it. They share `sprint.py` and the close
path, which is why the wording overlaps.

## Steps to Reproduce

Close a run whose retro has just had its carried-issues table completed. Run `sprint.py close --retro RETROxxxx --dry-run` and read the checklist step, then run the real close. The dry run refused where the real one passed. The refusal is also unactionable on its own: the renderer truncates the multi-line detail at the first line, so the item the step is refusing on is never named in the output.

## Proposed Fix

Two things, and the second is worth more than the first. Find why the dry-run path composes a different checklist from the real one - the state each is handed is the first place to look. Then stop the renderer truncating the detail: `_close_checklist` builds a multi-line block naming each outstanding item, and the close's line renderer cuts it at the first newline, so a refusal that was written to name its cause prints without it.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: During RUN-01KZF9AF's close, `sprint close --retro RETRO0099 --dry-run` reported `STOP checklist: 1 compulsory checklist item(s) unanswered` on three...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Close a run whose retro has just had its carried-issues table completed.
- [ ] **AC3** The proposed fix lands, pinned by a test: Two things, and the second is worth more than the first.

## Impact

A dry run exists to be trusted about what the real run will do. One that refuses where the real one passes trains its reader to skip it, which is the same as not having it - and this one refuses WITHOUT naming the item, so the only way past is to run the thing the dry run was meant to save you from.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio-authoring-session | Filed |
