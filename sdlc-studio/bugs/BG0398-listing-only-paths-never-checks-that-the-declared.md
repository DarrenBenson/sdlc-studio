# BG0398: listing_only_paths never checks that the declared read IS a listing, and applies one module's declaration globally

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** adversarial review of RUN-01KYMJEM, reproduced by the reviewer
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

The guard is `rel in paths`, which a CONTENT read satisfies as well as a listing read - the docstring promises the declaration is 'never widened beyond the measurement'. A module that declares a directory and also opens files under it de-relevances the whole tree, and the union means another module's content read of the same directory is silenced too. `.githooks` is a directory-level content read and is not in the protected set.

## Steps to Reproduce

A test module declaring `GATE_LISTING_ONLY`=('docs',) that also reads docs/*.md gives test-relevant: no on a docs edit, while its own assertion fails.

## Proposed Fix

Scope the declaration to the declaring module's own contribution and reject one for a path that module also opens.

## Acceptance Criteria

### AC1: one module's declaration does not silence another module's read

- **Given** one module declaring a directory listing-only and a second reading the same directory without declaring it
- **When** the listing-only scopes are read
- **Then** the directory is NOT listing-only, because a declaration is one module's statement about its own read and cannot speak for a neighbour's
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::DeclarationScopedToItsDeclarerTests::test_one_modules_declaration_does_not_silence_anothers_read
- **Verified:** yes (2026-07-29)

### AC2: a directory every reader declares is still narrowed

- **Given** every module that reads the directory declaring it listing-only
- **When** the listing-only scopes are read
- **Then** the narrowing applies, so unanimity is a condition on the feature rather than a refusal of it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::DeclarationScopedToItsDeclarerTests::test_a_directory_every_reader_declares_is_still_narrowed
- **Verified:** yes (2026-07-29)

### AC3: a directory-level content read can never be declared listing-only

- **Given** `.githooks`, read at directory level for its contents
- **When** the listing-only scopes are read
- **Then** no declaration makes it listing-only, because a declaration is a narrowing and its floor has to be stated rather than inferred
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::DeclarationScopedToItsDeclarerTests::test_a_content_read_directory_can_never_be_declared_listing_only
- **Verified:** yes (2026-07-29)

### AC4: the rule is held against the real repository

- **Given** this repository, where two modules read `sdlc-studio` and one declares it
- **When** the listing-only scopes are read
- **Then** the narrowing is withheld and the test says so - the saving US0554 delivered is suspended, honestly, until BG0400 corrects the fixture-path attribution behind the second reader
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::WorkspaceRelevanceGranularityTests::test_the_repo_s_own_workspace_narrows_only_when_every_reader_agrees
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
