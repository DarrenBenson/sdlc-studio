# CR-0728: Carry each changelog fragment's unit id into the composed CHANGELOG entry at the release cut

> **Status:** In Progress
> **Decomposed-into:** EP0365
> **Priority:** Low
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/changelog.py, .claude/skills/sdlc-studio/scripts/tests/test_changelog.py, .claude/skills/sdlc-studio/reference-scripts-domain.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, cross lens, survived 3 of 3 refute votes; observed at .claude/skills/sdlc-studio/scripts/changelog.py compose (lines 158-225): the fragment filename is used for error messages and then unlinked; CHANGELOG.md section '## [6.4.0] - 2026-11-16' (lines 10-1054)
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:30:07Z

## Summary

The paperwork rule keys each changelog fragment to its unit by file name, as a file named for the unit id under changelog.d/. The compose function in `changelog.py` folds only the fragment's body into the Unreleased section and then deletes the file, so the id survives only where the author happened to type it in the prose. In the 6.4.0 section of CHANGELOG.md, 79 of 137 top-level entries name no story, bug or request id, including the entry for the release's headline evidence-pack command, and the fragment directory no longer exists after the cut. A reader of the CHANGELOG cannot go from an entry to its unit, its criteria or its verdict without searching git history for a deleted file. The evidence pack and the CHANGELOG are both built at the cut from the same units and cannot be joined.

## Impact

Anyone reading a release's CHANGELOG to trace an entry back to the work behind it, such as a change board, an auditor or a maintainer chasing a regression, has no id to follow for most entries. The release notes promise that every entry is in the CHANGELOG section, but the unit ids they list per passage cannot be matched against it.

## Acceptance Criteria

- [ ] When compose runs with apply, each top-level entry it folds carries the unit id taken from its fragment's file name, in one fixed place in the entry, unless the entry text already names that id
- [ ] A fragment whose file name is not a unit id is folded without an id and compose reports it, so the gap is visible at the cut
- [ ] The compose dry run reports the same ids it would write and changes nothing
- [ ] A test in `test_changelog.py` composes two fixture fragments, one naming its id in the prose and one not, and asserts each resulting entry names its unit id exactly once

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
