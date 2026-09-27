# BG0792: US0940 AC1's own Verify takes about three minutes, so the release gate's verify lane reads it red at the 120-second default

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_release_verify_ceiling.py, .claude/skills/sdlc-studio/templates/workflows/release-gate.md, changelog.d/BG0792.md
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

- [ ] **AC1** Given no `SDLC_VERIFY_TIMEOUT` in the environment, when the verify lane runs, then its per-verifier ceiling is 300 s, CI's measured figure, and an explicit positive `SDLC_VERIFY_TIMEOUT` still wins. Fails on: HEAD's 120 s default, under which US0940 AC1's 177 s verifier read red on the v6.0.0-rc.1 release commit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_release_verify_ceiling.py::ReleaseVerifyCeilingTests::test_the_verify_ceiling_defaults_to_ci_s_figure

## Notes

- Sprint 6 engineering: take the bug's second option (raise the default with the reason recorded beside the constant) rather than splitting US0940 AC1's check. Removes `SDLC_VERIFY_TIMEOUT=300` from the cut runbook. BG0708 (the hermetic tests that read the environment) stays separate.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Filed |
| 2026-09-27 | sdlc-studio v6 planning | Groomed for Sprint 6: raise the default to 300 s; Affects moved from the US0940 test to gate.py |
