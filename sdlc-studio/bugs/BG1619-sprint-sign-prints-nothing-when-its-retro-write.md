# BG1619: sprint sign prints nothing when its retro write fails, so a mistyped --retro id now reaches that silence, and the close tail still prefers the scaffolded retro

> **Status:** Fixed
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sign_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_close.py, changelog.d/BG1619.md
> **Evidence:** run eighteen, 2026-11-19: sdlc-studio/reviews/verdicts/BG1607/9071429ca6c1-45a8c747.txt and sdlc-studio/reviews/verdicts/BG1607/d7052f4f7c95-4667bf4b.txt
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T14:55:06Z

## Summary

Non-blocking findings, pre-existing, from both seats' reviews of sign's retro choice (run eighteen): a failed write of the accuracy block to the retro prints nothing, and since sign now honours `--retro`, a mistyped id reaches that silence; the close tail (`_apply_signoff_tail`, which reads `scaffolded_retro` before the `--retro` it was given) still picks the scaffolded retro first.

## Steps to Reproduce

Run `sprint.py sign ... --retro RETRO9999` on a run whose retro is another id: the sign completes and says nothing about the retro it could not write.

## Proposed Fix

Refuse a --retro id with no file and report a failed write; make the close tail use the same choice as sign.

## Acceptance Criteria

- [ ] **AC1** Given a run whose retro is RETRO0002, when `sprint.py sign --retro RETRO9999` runs (no such file), then it exits non-zero naming RETRO9999 as missing and writes no seal. Fails on: sign completes silently with the accuracy write refused inside `_cascade_after_signature`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_retro.py::SignRetroTests::test_a_mistyped_retro_id_is_refused_before_the_seal
  - **Verified:** yes (2026-11-25)
- [ ] **AC2** Given a retro that exists but whose `retro.py accuracy --write` exits non-zero, when `sprint sign` runs, then stderr says `velocity row NOT recorded` with the exit and its output. Fails on: only `rc == 0` is handled, so a non-zero return prints nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_retro.py::SignRetroTests::test_a_failed_accuracy_write_is_said_on_stderr
  - **Verified:** yes (2026-11-25)
- [ ] **AC3** Given a run state with `scaffolded_retro` RETRO0001 and `sign --retro RETRO0002`, when the close tail (`_apply_signoff_tail`) runs, then it writes RETRO0002, the same retro `_sign_retro` picks. Fails on: the tail prefers the scaffolded retro, so it writes RETRO0001.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_retro.py::SignRetroTests::test_the_close_tail_writes_the_retro_sign_chooses
  - **Verified:** yes (2026-11-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-six: executable criteria for the mistyped id, the silent failed write and the tail's retro choice; the sign flow is one fix with its tail, so 2 pts not 1; the tail's `scaffolded_retro`-first pick is now at sprint.py `_apply_signoff_tail`, not line 7252 |
