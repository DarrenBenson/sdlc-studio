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

- [ ] **AC1** The behaviour described is corrected: The archive command of `archive.py` interpolates its `--release` label straight into the sub-index path at line 91, with no check for path separators or...
- [ ] **AC2** The proposed fix lands, pinned by a test: Validate the release label before any path is built: accept only a single path segment (letters, digits, dot, underscore and hyphen), refuse the bare dot and...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
