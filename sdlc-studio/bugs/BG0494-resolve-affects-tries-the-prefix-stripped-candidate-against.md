# BG0494: resolve_affects tries the prefix-stripped candidate against the repo root first, so a consuming project's own file wins

> **Status:** Open
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Severity:** Medium
> **Points:** 2
> **Verification depth:** functional

## Summary

BG0436 added a skill-relative fallback to `resolve_affects` (lib/`sdlc_md.py`:2925-2950), but the loop is `for base ... for cand_rel ...`, so the prefix-stripped candidate is tried against the REPO ROOT before the skill bases.

In a project holding its own `templates/core/story.md`, `resolve_affects(root, ".claude/skills/sdlc-studio/templates/core/story.md")` therefore returns the PROJECT's file rather than the skill's. New at this commit - at 4e7d5e6c the stripped candidate did not exist, so nothing resolved. Invisible in this repo because the vendored copy wins either way, which is why it shipped.

## Steps to Reproduce

1. Create a project with its own `templates/core/story.md`.
2. Call `resolve_affects(root, '.claude/skills/sdlc-studio/templates/core/story.md')`.
3. It returns the project's file, not the skill's.

## Proposed Fix

Swap the loop nesting, or restrict the prefix-stripped candidate to the skill bases only - it is a skill-relative spelling and has no business matching at the project root.

## Acceptance Criteria

- [x] **AC1: a skill-relative spelling resolves to the SKILL's file, even when the project holds a same-named path.**
  - **Given** a consuming project that holds its own `templates/core/story.md`, and the declared
    path `.claude/skills/sdlc-studio/templates/core/story.md`
  - **When** `resolve_affects` runs against that project root
  - **Then** it returns the SKILL's copy, because the declared spelling is skill-relative and a
    prefix-stripped candidate has no business matching at the project root - the current loop
    nests base outside candidate, so the stripped form is tried at the root first and the
    project's file wins silently
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::SkillRelativeResolutionTests::test_a_skill_spelling_does_not_resolve_to_a_project_file_of_the_same_name
  - **Verified:** yes (2026-08-04)

- [x] **AC2: an ordinary project-relative path still resolves at the project root.**
  - **Given** a declared path that is not skill-relative, naming a file the project does hold
  - **When** `resolve_affects` runs
  - **Then** it resolves at the project root exactly as before, so the fix narrows the
    skill-relative candidate rather than reordering resolution for everything
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::SkillRelativeResolutionTests::test_an_ordinary_project_path_is_unaffected
  - **Verified:** yes (2026-08-04)

## Verification evidence

Functional. The stripped candidate is now offered to the skill bases only, so a skill-relative
spelling can no longer match at the project root. One mutant executed, `__pycache__` purged and
the child run under `python3 -B`, anchor asserted unique, source restored byte-identical:

| Mutant | Result |
| --- | --- |
| offer the stripped candidate to the project root as well | killed by 1 test |

Three tests, because the fix has two ways to be wrong and only one of them is the filed defect:
the project's decoy must lose, an ordinary project-relative path must still resolve at the root,
and a project that genuinely VENDORS the skill must still resolve to its vendored copy. The
second and third are controls - a narrowing that broke either would trade one wrong answer for
another.

The reviewer at the goal review noted AC2 is non-discriminating on its own, returning the same
result on the broken code and on either candidate fix. That is correct and it is why it is
labelled a control rather than counted as coverage: AC1 is the criterion that discriminates.

## Impact

A consuming project that happens to hold a same-named path silently shadows the skill's copy in every Affects resolution. This repo cannot see it, which makes it exactly the kind of defect that reaches consumers first.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
