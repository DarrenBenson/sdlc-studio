# BG1787: After a release cut folds the last fragment, the changelog.d directory leaves the tree and the fragment check passes every commit until a fragment is written

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/changelog.py, .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_changelog_cut_keeps_dir.py, changelog.d/BG1787.md, .claude/skills/sdlc-studio/scripts/tests/test_changelog.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py
> **Evidence:** Run twenty-eight, 2026-11-28: after f2440fd9b main holds no changelog.d/; executed in a throwaway clone, `changelog.required` returned [] with no directory and refused once one fragment re-created it. US1330's qa seat noted the directory's absence (pre-existing) at c52e294ed593-ae8295f6.
> **Created:** 2026-11-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-28T06:30:35Z

## Summary

`changelog.required` applies only where the project keeps a `changelog.d/` directory. `release_cut.py changelog-cut` folds every fragment and removes each file, and git tracks no empty directory, so after the cut commit the directory is gone from every clone and the commit-msg check returns no refusal for a code commit that carries no fragment. It stays off until some commit writes a fragment and re-creates the directory. The 6.4.0 cut (9fa295586) and the 6.5.0 cut (f2440fd9b) both left the tree this way, so the first commits after each release are not held to their fragment.

## Steps to Reproduce

1. In a clone of main after the 6.5.0 cut, where `changelog.d/` does not exist, stage a change to a code file.
2. Call `changelog.required('.', 'fix(BG9999): a code change with no fragment')`.
3. It returns `[]`. Create `changelog.d/` with any one fragment and the same call refuses: `BG9999: the commit stages code but not changelog.d/BG9999.md`.

## Proposed Fix

Keep the directory through a cut, for example with a tracked keep file that `changelog-cut` leaves in place and compose ignores, or read the rule's presence from the project's config rather than from the directory existing. Pin both: a commit after a cut that stages code and no fragment is refused.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `changelog.required` applies only where the project keeps a `changelog.d/` directory.
- [ ] **AC2** The proposed fix lands, pinned by a test: Keep the directory through a cut, for example with a tracked keep file that `changelog-cut` leaves in place and compose ignores, or read the rule's presence...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-28 | sdlc-studio | Filed |
