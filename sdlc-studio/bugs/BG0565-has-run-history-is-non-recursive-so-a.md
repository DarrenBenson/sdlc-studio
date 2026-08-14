# BG0565: has_run_history is non-recursive, so a project that archives its retros into a subdirectory reads as never having closed a sprint and is silently softened

> **Status:** Fixed
> **Verification depth:** functional (executed: a retro filed under retros/archive/v5.0.0/ reads True where it read False, with the empty-directory case still False)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/plan_review.py, .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py
> **Evidence:** Round-2 delivery review of RUN-01KZM49Y, 2026-08-10. `has_run_history` iterates `sdlc-studio/retros/` one level deep, so a retro moved into `retros/archive/` is invisible to it. `archive.py` exists precisely to move terminal rows out of a live index as a project grows, which makes this the state a long-lived project arrives at rather than an exotic one.
> **Created:** 2026-08-10
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The predicate decides whether the plan-review gate is armed. It answers by listing `sdlc-studio/retros/` and looking for a file whose stem starts with RETRO - one level, no recursion.

A project that archives its retros into a subdirectory therefore reads as having closed no sprint, and the first-run softening applies to it for ever. That is the failure direction the predicate was explicitly written to avoid: it fails towards history for an UNREADABLE directory, and then fails away from history for an archived one.

The other fooling directions are all safe because they are stricter - a stray `retro-notes.md` arms the gate, as does a directory named `RETRO0001-x.md`. Only the nesting one softens, and it is the one a growing project reaches on its own.

## Steps to Reproduce

1. Take a project with one retro at `sdlc-studio/retros/RETRO0001-x.md` and confirm the gate refuses. 2. Move it to `sdlc-studio/retros/archive/RETRO0001-x.md`. 3. The gate now reports rather than refuses, and nothing says why.

## Acceptance Criteria

- [x] **AC1** Given a project whose retros are filed under `retros/archive/<version>/`, when `has_run_history` reads it, then it reports True - archiving closed runs must not make an established project read as brand new and take the new-project concession for ever.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan_review.py -k an_archived_retro_still_counts_as_run_history

## Proposed Fix

Walk the retro directory recursively, or read the retro index rather than the directory listing. Pin it with a fixture whose only retro is nested, asserting the gate still refuses - and keep the flat case beside it as the positive control, since a recursive walk that finds nothing would satisfy a test that only checks the nested one.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in plan_review.py `has_run_history`, revert d.rglob('*.md') to d.iterdir() so an archived retro is invisible | Given a project whose retros are filed under `retros/archive/<version>/`, when `has_run_history` reads it, then it reports True - archiving closed runs must not make an established project read as brand new and take the new-project concession for ever. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-10 | sdlc-studio | Filed |
