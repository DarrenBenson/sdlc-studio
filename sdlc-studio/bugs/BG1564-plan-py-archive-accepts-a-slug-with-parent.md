# BG1564: plan.py archive accepts a slug with parent segments and moves a file from outside the plans directory

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/plan.py, .claude/skills/sdlc-studio/scripts/tests/test_plan.py
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

- [ ] **AC1** The behaviour described is corrected: The archive command of `plan.py` joins its slug argument into both the source and the destination path as given, in `cmd_archive` at lines 140 to 162.
- [ ] **AC2** The proposed fix lands, pinned by a test: Refuse a slug that is not a single path component: no path separator, no parent or current-directory segment and not absolute, with a message naming the slug.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
