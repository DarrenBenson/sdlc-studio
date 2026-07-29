# BG0388: The seam owner check matches by naive substring, so a unit's own test file owns the seam over its source

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py
> **Evidence:** adversarial review of RUN-01KYMJEM, reproduced by the reviewer
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

`any(s.lower() in declared for s in shared)` means `Preserves: tests/test_critic.py keeps passing` owns the seam on `critic.py`, because `'critic.py' in 'tests/test_critic.py'` is true. `critic._verifier_names` already documents and fixes this exact rule three files away, and the seam block claims to be modelled on it.

## Steps to Reproduce

US0001 Affects critic.py+tests/`test_critic.py` with Preserves naming only the test file; US0002 Affects critic.py -> `seam_findings` returns [].

## Proposed Fix

Match at path boundaries, reusing the sibling's predicate rather than a second reading.

## Acceptance Criteria

### AC1: a Preserves naming only the test file does not own the source seam

- **Given** a unit declaring `src/critic.py` and `tests/test_critic.py` whose Preserves names only the test file
- **When** the seam map runs
- **Then** the seam on the shared source is still reported unowned, because the match is at path boundaries rather than by substring
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::SeamOwnershipDefectsTests::test_a_preserves_naming_only_the_test_file_does_not_own_the_source_seam
- **Verified:** yes (2026-07-29)

### AC2: the predicate is the sibling's, not a second reading

- **Given** a Preserves line that names the shared source itself
- **When** the seam map runs
- **Then** the seam IS owned - the same `critic._verifier_names` predicate decides both, so a matcher that never matches is not mistaken for a fix
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::SeamOwnershipDefectsTests::test_naming_the_shared_source_itself_does_own_it
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
