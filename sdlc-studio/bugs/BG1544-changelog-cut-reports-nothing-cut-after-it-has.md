# BG1544: changelog-cut reports nothing cut after it has already folded and deleted every pending fragment

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, code lens, survived 3 of 3 refute votes; observed at .claude/skills/sdlc-studio/scripts/release_cut.py `cut_changelog`, lines 50-55
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:27:33Z

## Summary

`cut_changelog` in `release_cut.py` calls the changelog compose step in apply mode before it checks whether the cut can go ahead. Compose rewrites the Unreleased section of CHANGELOG.md and deletes every file under changelog.d. Only afterwards does the function refuse a version that already has a section, or a changelog with no Unreleased section, with a message ending in nothing cut and exit 2. A refused cut has therefore changed CHANGELOG.md and consumed the whole pending fragment set while reporting that nothing happened. The entry text survives under Unreleased, but the per-unit fragments the commit hooks require are gone from the working tree, and the existing test of a refused second cut runs with no pending fragment, so nothing pins the side effect.

## Steps to Reproduce

1. In a throwaway directory write a CHANGELOG.md holding an Unreleased section and a section for [1.0.0] dated 2026-01-01.
2. Add one fragment at changelog.d/BG0001.md with a Fixed entry.
3. Run `release_cut.py` with --root pointing at the directory, the changelog-cut verb and --version 1.0.0.
4. Observed: it prints that CHANGELOG.md already carries a section for 1.0.0 and nothing was cut, exit 2, yet changelog.d is now empty and the Unreleased section holds the BG0001 entry.
5. Expected: the refusal leaves CHANGELOG.md and changelog.d byte for byte as they were.
6. Positive control: the same fixture cut as version 1.1.0 folds the fragment and writes the new section.

## Proposed Fix

Move both refusal checks ahead of the compose call in `cut_changelog`: read CHANGELOG.md, refuse when the version already has a section or when there is no Unreleased section, and only then compose the fragments and cut. Extend the refused-cut tests in `test_release_cut.py` to run with a pending fragment and assert that the fragment file and CHANGELOG.md are unchanged after each refusal.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `cut_changelog` in `release_cut.py` calls the changelog compose step in apply mode before it checks whether the cut can go ahead.
- [ ] **AC2** The proposed fix lands, pinned by a test: Move both refusal checks ahead of the compose call in `cut_changelog`: read CHANGELOG.md, refuse when the version already has a section or when there is no...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
