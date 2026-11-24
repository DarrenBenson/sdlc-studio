# BG1564: plan.py archive accepts a slug with parent segments and moves a file from outside the plans directory

> **Status:** Fixed
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/plan.py, .claude/skills/sdlc-studio/scripts/tests/test_plan.py, changelog.d/BG1564.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, code lens, survived 3 of 3 refute votes; observed at .claude/skills/sdlc-studio/scripts/plan.py cmd_archive() lines 140-162 (source and destination both built from the slug, then moved with shutil.move)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:29:52Z

## Summary

The archive command of `plan.py` joins its slug argument into both the source and the destination path as given, in `cmd_archive` at lines 140 to 162. A slug that begins with a parent-directory segment resolves the source outside the plans directory and the destination outside the month folder, and the tool moves the file and prints that it was archived. With the default plans directory, a slug naming the parent directory's CLAUDE file moves the user's global instruction file into the plans archive, where it lands beside the month folders and is missed by the lookup the already-archived message uses. This is path traversal through an unvalidated path component, the same class as the release label in `archive.py`, in a different script. The realistic route is an agent passing a slug derived from a heading or a file name.

## Steps to Reproduce

1. Create a scratch directory holding claude/CLAUDE.md and claude/plans/real.md.
2. Run plan.py with the archive verb, a slug made of one parent-directory segment followed by CLAUDE, and --plans-dir set to the scratch claude/plans directory.
3. Observe that the command exits 0 and prints that it archived the slug to a path under the month folder that climbs back out through the parent segment.
4. List the scratch tree: claude/CLAUDE.md has gone and claude/plans/archive/CLAUDE.md exists, beside the month folder and not inside it.
5. Run the same command again: it reports no active plan of that name, because the already-archived lookup only searches inside month folders.

## Proposed Fix

Refuse a slug that is not a single path component: no path separator, no parent or current-directory segment and not absolute, with a message naming the slug. As a second guard, resolve the source and require its parent to be the plans directory before moving anything. Add tests to `test_plan.py`: a slug with a parent segment, a slug with a separator and an absolute slug are each refused with exit 1 and no file moved, and a plain slug still archives into the month folder.

## Acceptance Criteria

- [ ] **AC1** Given a scratch directory holding a file beside the plans directory, when `plan.py archive` runs with a slug that begins with a parent-directory segment and names that file, then it exits 1 with a message naming the slug, the file is still where it was, and nothing is created under the archive folder. Fails on: exit 0, the file moved to `plans/archive/<name>.md` beside the month folder (reproduced at HEAD with slug `../CLAUDE`).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan.py::ArchiveTests::test_archive_refuses_a_slug_with_a_parent_segment
  - **Verified:** yes (2026-11-24)
- [ ] **AC2** Given a plans directory holding a plan, when the slug holds a path separator or is absolute, then each is refused with exit 1 and no file moved. Fails on: a traversal that survives by a spelling the first check missed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan.py::ArchiveTests::test_archive_refuses_a_separator_and_an_absolute_slug
  - **Verified:** yes (2026-11-24)
- [ ] **AC3** Given a plain slug naming an active plan, when `plan.py archive` runs, then the plan moves into the month folder as before. Fails on: the validation refusing a legitimate slug.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_plan.py::ArchiveTests::test_archive_happy_path
  - **Verified:** yes (2026-11-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced at HEAD in a throwaway tree (slug `../CLAUDE` moved a file from beside the plans directory, exit 0); AC2 no longer says 'in a subfolder' |
