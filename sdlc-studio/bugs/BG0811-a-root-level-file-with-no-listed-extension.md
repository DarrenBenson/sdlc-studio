# BG0811: A root-level file with no listed extension drops out of a unit's Affects, so review scope and the plan's file checks never see it

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_affects_root_files.py, changelog.d/BG0811.md, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Evidence:** v6.0.0-rc.1 soak: sdlc-studio-web W2 review, 2026-09-27; code: lib/sdlc_md.py affects_files
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-27T21:52:39Z

## Summary

`sdlc_md.affects_files` keeps an Affects token only when it contains `/` or ends in .py, .md, .yaml, .yml or .sh. A root-level `package.json`, `astro.config.mjs`, `pyproject.toml`, `tsconfig.json`, `Makefile`, `go.mod` or `Cargo.toml` is silently dropped. Found in the v6.0.0-rc.1 soak on the website project: `critic.py brief --unit US-01M3HRXZ --seat qa` left `astro.config.mjs` out of the review's diff scope although the story's Affects lists it. Every reader of the parser inherits the gap: the review brief's bounded scope, the plan's shared-file and delivery-mode checks, and any close guard that reads declared files. For any project not written in Python, root config files leave the review.

## Steps to Reproduce

A story whose Affects reads `astro.config.mjs, package.json, src/pages/index.astro`; `sdlc_md.affects_files(text)` returns only `src/pages/index.astro`.

## Proposed Fix

Treat a token as a path when it contains `/`, or has a file extension (a dot followed by an alphanumeric suffix), or names a file that exists in the repository (Makefile, Dockerfile); keep refusing prose tokens such as `none` or `-`.

## Acceptance Criteria

- [ ] **AC1** Given an Affects line naming `astro.config.mjs, package.json, pyproject.toml, Makefile, src/x.ts`, when `affects_files` reads it in a repository where `Makefile` exists, then all five are returned. Fails on: HEAD's extension list, which returns only `src/x.ts`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_affects_root_files.py::AffectsRootFilesTests::test_root_files_are_kept
  - **Verified:** yes (2026-09-28)
- [ ] **AC2** Given an Affects line of `none` or `-`, or with a parenthetical note, then no prose token is returned as a path. Fails on: treating every comma-separated token as a path
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_affects_root_files.py::AffectsRootFilesTests::test_prose_is_not_a_path
  - **Verified:** yes (2026-09-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Filed |
