# BG1607: sprint sign rewrites RETRO0001's accuracy block and velocity row when the run state names no scaffolded retro, ignoring --retro

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG-SIGN-RETRO.md
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

- [ ] **AC1** The behaviour described is corrected: After sealing, `sprint sign` runs `retro.py accuracy --id <retro> --write --tokens-from-harness`, taking the retro from the run state's `scaffolded_retro` and...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Scaffold a run's retro with `artifact.py new --type retro`, close with `sprint close --retro RETROnnnn`, then `sprint sign --report RPTxxxx --principal P...
- [ ] **AC3** The proposed fix lands, pinned by a test: Resolve the sign's retro from `--retro`, then the retro the close recorded on the run, then `scaffolded_retro`, and refuse to write when none is known rather...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
