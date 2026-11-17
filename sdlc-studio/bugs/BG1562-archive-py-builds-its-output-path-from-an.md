# BG1562: archive.py builds its output path from an unvalidated release label and can write outside the workspace

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/archive.py, .claude/skills/sdlc-studio/scripts/tests/test_archive.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, code lens, survived 3 of 3 refute votes; observed at .claude/skills/sdlc-studio/scripts/archive.py line 91 (where archive_rel is built from the release label) and the --release argument at line 159
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:29:39Z

## Summary

The archive command of `archive.py` interpolates its `--release` label straight into the sub-index path at line 91, with no check for path separators or parent-directory segments. A label containing parent-directory segments makes the tool create directories and write the sub-index outside the type's archive folder, and outside the repository if enough segments are given. It then removes the rows from the live index and reports success. The moved rows sit outside the archive tree that the index parser unions, so the census the module promises to keep correct no longer sees them. This is path traversal through an unvalidated path component, reachable by any caller that passes a label derived from free text.

## Steps to Reproduce

1. Create a throwaway fixture repository with one Closed bug under sdlc-studio/bugs/ and build its index with reconcile.py apply.
2. From the fixture root run archive.py with the archive verb, --root set to the fixture, --type bug and --release set to a label made of four parent-directory segments followed by the word escaped.
3. Observe that the command exits 0 and prints that it archived one bug row to a path under sdlc-studio/bugs/archive/ that climbs out through the parent segments.
4. Search above the fixture root: a file escaped/bug.md exists one level above the repository.
5. Open the live bug index: it now holds an archive pointer line carrying the traversing label, and the row itself has gone from the live table.

## Proposed Fix

Validate the release label before any path is built: accept only a single path segment (letters, digits, dot, underscore and hyphen), refuse the bare dot and double-dot segments, and refuse with a message naming the label. As a second guard, resolve the computed sub-index path and refuse when it is not under the type's archive directory. Add tests to `test_archive.py`: a label with a separator, a label with a parent segment and an absolute label are each refused with nothing written and the live index untouched, and a plain label such as r2.5 still archives.

## Acceptance Criteria

- [ ] **AC1** Given a fixture workspace with one Closed bug in the live index, when `archive.py archive` runs with a `--release` label made of parent-directory segments, then it exits non-zero with a message naming the label, creates no file or directory inside or outside the workspace, and leaves the live index byte-identical. Fails on: the sub-index written outside the type's archive folder and the row removed from the live table.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_archive.py::ReleaseLabelTraversalTests::test_a_label_with_parent_segments_is_refused_and_nothing_is_written
- [ ] **AC2** Given the same fixture, when the label holds a path separator, is absolute, or is a bare dot or double-dot, then each is refused the same way with nothing written. Fails on: a traversal that survives by a spelling the first check missed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_archive.py::ReleaseLabelTraversalTests::test_a_separator_an_absolute_label_and_a_dot_segment_are_refused
- [ ] **AC3** Given the same fixture, when the label is a plain single segment such as r2.5, then the row is archived under the type's archive folder and the census still counts it. Fails on: the validation refusing a legitimate release label.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_archive.py::ReleaseLabelTraversalTests::test_a_plain_label_still_archives

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
