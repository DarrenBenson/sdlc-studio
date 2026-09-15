# BG0671: critic.py's brief-practice and claim-pass checks are called by no production path, while reference-review.md says the brief verb refuses a brief that fails them

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-review.md
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** backlog sweep 2026-09-15; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

reference-review.md:452 states '`critic.py` refuses to issue a brief missing any of these practices, or a claim-inventory pass that omits one of the four prose surfaces, so the discipline holds by construction'. The two functions that would do it, `assert_brief_practices` (critic.py:3177) and `assert_brief_claim_pass` (critic.py:3202), are called only by tests: `cmd_brief` never calls either, and no other production module does. So the shipped doctrine describes a refusal the tool never makes - the silent-misleading shape LL0009 ranks above a loud failure, and the shipped-but-unwired gate LL0027 warns of. Reproduced at 51f264db (grep of scripts/ excluding tests/); found by the 2026-09-15 backlog sweep.

## Steps to Reproduce

1. `grep -rn 'assert_brief_practices\|assert_brief_claim_pass' .claude/skills/sdlc-studio/scripts --include=*.py | grep -v /tests/` - only the two definitions print.
2. Read reference-review.md:452-454, which claims the brief verb refuses.

## Proposed Fix

Call both checks on the rendered brief inside the brief verb before it is printed, refusing (non-zero, naming the missing practice or surface) rather than printing a brief that fails them. If a check cannot pass on a brief the tool itself renders, fix the renderer, not the check.

## Acceptance Criteria

- [ ] **AC1** `critic.py brief` refuses, naming the practice, when the brief it would print lacks one of the standing practices
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefRefusesMissingPracticeTests::test_a_brief_missing_a_practice_is_refused_by_the_cli
- [ ] **AC2** `critic.py brief` refuses, naming the surface, when the brief's claim-inventory pass omits one of the four prose surfaces
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefRefusesMissingPracticeTests::test_a_brief_missing_a_surface_is_refused_by_the_cli
- [ ] **AC3** A brief rendered from the shipped seat cards passes both checks and prints - the paired control
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BriefRefusesMissingPracticeTests::test_the_shipped_brief_prints

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | backlog sweep 2026-09-15 | Filed |
