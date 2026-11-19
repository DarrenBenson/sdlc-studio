# BG1619: sprint sign prints nothing when its retro write fails, so a mistyped --retro id now reaches that silence, and the close tail still prefers the scaffolded retro

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sign_retro.py, changelog.d/BG1619.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** run eighteen, 2026-11-19: sdlc-studio/reviews/verdicts/BG1607/9071429ca6c1-45a8c747.txt and sdlc-studio/reviews/verdicts/BG1607/d7052f4f7c95-4667bf4b.txt
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T14:55:06Z

## Summary

Non-blocking findings, pre-existing, from both seats' reviews of sign's retro choice (run eighteen): a failed write of the accuracy block to the retro prints nothing, and since sign now honours `--retro`, a mistyped id reaches that silence; the close tail (sprint.py around line 7252) still picks the scaffolded retro first.

## Steps to Reproduce

Run `sprint.py sign ... --retro RETRO9999` on a run whose retro is another id: the sign completes and says nothing about the retro it could not write.

## Proposed Fix

Refuse a --retro id with no file and report a failed write; make the close tail use the same choice as sign.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Non-blocking findings, pre-existing, from both seats' reviews of sign's retro choice (run eighteen): a failed write of the accuracy block to the retro prints...
- [ ] **AC2** The proposed fix lands, pinned by a test: Refuse a --retro id with no file and report a failed write; make the close tail use the same choice as sign.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
