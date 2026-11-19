# BG1607: sprint sign rewrites RETRO0001's accuracy block and velocity row when the run state names no scaffolded retro, ignoring --retro

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sign_retro.py, changelog.d/BG1607.md
> **Evidence:** the website's RUN-01M7R7KN sign, 2026-11-19: orchestrator; restored under the website's D0031
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T07:52:26Z

## Summary

After sealing, `sprint sign` runs `retro.py accuracy --id <retro> --write --tokens-from-harness`, taking the retro from the run state's `scaffolded_retro` and falling back to the literal 'RETRO0001' (sprint.py, the sign cascade's velocity step). It does not read `sign --retro` or the retro `sprint close --retro` was given. The website's run scaffolded its retro with `artifact.py new --type retro` and closed with `--retro RETRO0008`, so its run state named no scaffolded retro, and the sign rewrote RETRO0001, a 2026-09-29 retro of an unrelated run: its Batch row lost its recorded 622,552s wall-clock, it gained a 'Priced cost: not stated' line naming the new run, and its VELOCITY.md row was rewritten. Three rehearsals in throwaway copies, with and without `--retro RETRO0008`, did the same.

## Steps to Reproduce

Scaffold a run's retro with `artifact.py new --type retro`, close with `sprint close --retro RETROnnnn`, then `sprint sign --report RPTxxxx --principal P --retro RETROnnnn`: `git diff` shows RETRO0001 and its VELOCITY.md row changed, and RETROnnnn untouched.

## Proposed Fix

Resolve the sign's retro from `--retro`, then the retro the close recorded on the run, then `scaffolded_retro`, and refuse to write when none is known rather than defaulting to RETRO0001; pin it with a test whose state names no scaffolded retro.

## Acceptance Criteria

### AC1: Sign writes the named retro and leaves RETRO0001 alone

- **Given** a closed run whose run state names no `scaffolded_retro`, in a fixture holding RETRO0001 and RETRO0002
- **When** `sprint sign --report <its report> --principal P --retro RETRO0002` seals it
- **Then** the accuracy block and velocity row are written for RETRO0002, and RETRO0001 and its VELOCITY.md row are byte-identical to before. Fails on: any change to RETRO0001 or its row
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_retro.py::SignRetroTests::test_sign_writes_the_named_retro_and_leaves_retro0001
- **Verified:** yes (2026-11-19)

### AC2: Sign falls back to the close's retro, and writes none when no retro is known

- **Given** a closed run whose close was given `--retro RETRO0002`, and a second closed run whose state records no retro at all
- **When** each is signed without `--retro`
- **Then** the first writes RETRO0002's accuracy block; the second writes no retro and prints that the velocity row was not recorded, naming `--retro`. Fails on: either writing RETRO0001
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_retro.py::SignRetroTests::test_sign_uses_the_close_retro_and_writes_none_when_unknown
- **Verified:** yes (2026-11-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
