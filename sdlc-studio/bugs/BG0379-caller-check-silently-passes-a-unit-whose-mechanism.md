# BG0379: caller-check silently passes a unit whose mechanism surface its own verifier emptied, so US0512's criterion cannot fail

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; the indeterminate branch mutation-killed)
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, sdlc-studio/stories/US0512-a-unit-adding-a-mechanism-carries-an-acceptance.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (round 3 review of RUN-01KYKVZM, run wf_95377bad); agent; skill v5.0.0

## Summary

`mechanism_files` derives the surface a unit adds by subtracting every Affects path named by the unit's own Verify lines - the rule that stops a unit's test file counting as its own mechanism. The BG0376 repair pointed US0512's criterion at a shell verifier that INVOKES critic.py, and critic.py is the unit's only non-markdown Affects entry not already named elsewhere, so the surface became empty. `caller_findings` then hits its skip-when-no-mechanism branch and never judges the unit at all. Deleting the Caller declaration leaves the check at exit 0; replacing it with text naming no consumer also leaves it at exit 0. The criterion is vacuous, which is exactly the defect BG0376 was filed to remove, reintroduced on one of the five units by BG0376's own fix. Four of the five are genuinely pinned; this one is not.

## Steps to Reproduce

Verified at HEAD. Delete the Caller bullet from US0512 and run caller-check against it: exit 0. At the parent commit `mechanism_files` returned critic.py for the same unit; at HEAD it returns nothing. The subtraction cannot tell a path being INVOKED by a shell verifier from a path being PROVEN by a test selector.

## Proposed Fix

Two candidates, and the choice needs a clear head rather than a sixth repair in one day. Either narrow the subtraction so it removes only proof-shaped paths (a test selector, a test file) and not a path a shell verifier merely invokes; or make the skip explicit - a unit that declares a Caller while presenting an empty mechanism surface is a unit the check could not judge, and an unjudgeable unit should be reported rather than passed, which is the absence-is-not-an-answer rule this project already carries.

## Acceptance Criteria

### AC1: a mechanism surface emptied by the unit's own verifier is REPORTED, not skipped

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CallerIndeterminateTests::test_a_surface_emptied_by_its_own_verifier_is_reported_not_skipped
- **Verified:** yes (2026-07-28)

### AC2: the verdict changes when the Caller declaration does, so the check's greenness means something

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CallerIndeterminateTests::test_the_verdict_changes_when_the_declaration_does
- **Verified:** yes (2026-07-28)

### AC3: a documentation-only unit is still not asked for a caller, so the carve-out does not widen into firing on everything

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CallerIndeterminateTests::test_a_documentation_only_unit_is_still_not_asked_for_a_caller
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (round 3 review of RUN-01KYKVZM, run wf_95377bad) | Filed |
| 2026-07-28 | Claude Opus 5 | Criteria authored at delivery; executable since BG0356/BG0360. |
