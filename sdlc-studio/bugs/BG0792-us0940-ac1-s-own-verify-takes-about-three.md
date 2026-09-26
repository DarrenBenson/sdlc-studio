# BG0792: US0940 AC1's own Verify takes about three minutes, so the release gate's verify lane reads it red at the 120-second default

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** tools/tests/test_lean_release_verify.py, sdlc-studio/stories/US0940-every-criterion-on-a-done-story-passes-when.md
> **Created:** 2026-09-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-26T18:16:18Z

## Summary

tools/tests/`test_lean_release_verify.py`::ReleaseVerifyTests::`test_the_measured_red_criteria_pass_or_are_retired` runs 31 criteria and took 177s alone; gate.py --release at the default `SDLC_VERIFY_TIMEOUT`=120 reported US0940::AC1 red on the v6.0.0-rc.1 release commit. CI's corpus-verify job sets 300s, so CI is green; a local release gate at the default is not.

## Steps to Reproduce

python3 .claude/skills/sdlc-studio/scripts/gate.py --root . --release: verify lane names US0940::AC1.

## Proposed Fix

Split the AC1 check so no single verifier exceeds the default (one criterion per selector, or the lane's own per-AC run), or raise the gate's default to CI's 300 with a recorded reason.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: tools/tests/`test_lean_release_verify.py`::ReleaseVerifyTests::`test_the_measured_red_criteria_pass_or_are_retired` runs 31 criteria and took 177s alone...
- [ ] **AC2** The proposed fix lands, pinned by a test: Split the AC1 check so no single verifier exceeds the default (one criterion per selector, or the lane's own per-AC run), or raise the gate's default to CI's...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Filed |
