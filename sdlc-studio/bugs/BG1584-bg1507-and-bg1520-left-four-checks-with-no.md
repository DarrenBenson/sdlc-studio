# BG1584: BG1507 and BG1520 left four checks with no test: --includes, includeIf identities, the self-check-author refusal and the retro's owed branches

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_git_identity_guard.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG1584.md
> **Evidence:** Run sixteen QA round-2 verdicts for BG1507 and BG1520.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T03:26:16Z

## Summary

The QA seat's round-2 APPROVEs of BG1507 and BG1520 (run sixteen) carried non-blocking gaps. BG1507: the identity guard's `--includes` read has no test, and an identity set through includeIf depends on the directory the command runs from. BG1520: no test covers the self-review refusal when the author comes from the self-check, and the retro learnings review's two `owed` branches from round one are still untested.

## Steps to Reproduce

See sdlc-studio/reviews/verdicts/BG1507/c13628931241-69b23dfe.txt and sdlc-studio/reviews/verdicts/BG1520/ddc2d546e492-f1e7594f.txt.

## Proposed Fix

Pin each with a test beside a positive control; read the identity from the repository root so includeIf resolves the same way a commit does.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The QA seat's round-2 APPROVEs of BG1507 and BG1520 (run sixteen) carried non-blocking gaps.
- [ ] **AC2** The proposed fix lands, pinned by a test: Pin each with a test beside a positive control; read the identity from the repository root so includeIf resolves the same way a commit does.

## Impact

Guards that could be removed with the suite still green; an includeIf identity read from the wrong directory.

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. Four checks with no test.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
