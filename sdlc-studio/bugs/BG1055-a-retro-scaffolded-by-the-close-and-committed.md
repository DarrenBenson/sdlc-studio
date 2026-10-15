# BG1055: A retro scaffolded by the close and committed before the close re-runs turns the release-verify lane red

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** devserver1 push gate for 58ab4eaa on 2026-10-15: 1 red, test_lean_release_verify.py::ReleaseVerifyTests::test_the_measured_red_criteria_pass_or_are_retired, US0289::AC2 exit 1; locally 'RETRO0134 2026-10-15' listed by velocity --gaps.
> **Created:** 2026-10-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-15T19:04:38Z

## Summary

`sprint.py close` without --retro scaffolds the run's retro and stops, telling the operator to fill it and re-run. Its VELOCITY.md row is written only by the re-run's retro-accuracy step. US0289 AC2's verifier, `retro.py velocity --gaps --since RETRO0029`, reads any retro without a row as a gap and exits 1, and `test_lean_release_verify` runs it in the push boundary suite. So committing the filled-in retro before the close re-runs (a natural point to save it) turns the full push suite red with a message that names a velocity gap, not the cause. Hit on RUN-01M4R168: the devserver1 push gate failed on US0289::AC2 with RETRO0134 staged.

## Steps to Reproduce

Run `sprint.py close` with no --retro, fill the scaffolded retro, commit it, then run `retro.py velocity --gaps --since RETRO0029`: the new retro is listed as a gap and the command exits 1.

## Proposed Fix

Have `velocity --gaps` leave out the open run's own retro until that run closes (its row is the close's to write), or have the scaffold say plainly that the retro is committed with the close, not before.

## Acceptance Criteria

- [ ] **AC1** Given an open run whose scaffolded retro is committed before the close re-runs, when `retro.py velocity --gaps --since RETRO0029` runs, then it does not read that retro as a gap.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-15 | sdlc-studio | Filed |
