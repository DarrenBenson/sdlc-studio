# BG1542: release_cut.py tag-check passes a symbolic ref recorded green at one commit and checked at another

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py, changelog.d/BG1542.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, code lens, survived 3 of 3 refute votes; observed at .claude/skills/sdlc-studio/scripts/release_cut.py `record_green` (line 69) and `tag_check` (line 293, `if green != commit`)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:27:20Z

## Summary

The release gate stamp in `release_cut.py` is compared as a literal string. `record_green` stores the `--commit` argument unresolved, and `tag_check` tests the stored value against its own `--commit` argument by string equality before anything resolves either side. Recording green on HEAD, committing again and checking HEAD therefore reports that the gate was green on the tagged commit, although the gate never ran on that tree. With no remote, or a forge that is not GitHub, the tag is allowed outright. This is the false claim the module's own docstring says the check exists to prevent. BG1281, closed as Won't Fix, covered only the opposite direction, a false refusal for an abbreviated sha.

## Steps to Reproduce

1. Create a throwaway git repository with no remote and make one empty commit.
2. Run `release_cut.py` with --root pointing at it, the record-green verb and --commit HEAD. It prints that the release gate was recorded green on HEAD, and the stamp file holds the word HEAD.
3. Make a second empty commit.
4. Run `release_cut.py` tag-check with --commit HEAD.
5. Observed: it prints that the gate green on HEAD matches the tagged commit and there is no forge to ask, exit 0.
6. Expected: a refusal naming the first commit as the one the gate ran on.
7. Positive control: record the first commit by its full sha, then tag-check the second by its full sha, and the refusal is printed.

## Proposed Fix

Resolve both sides to a full commit sha before storing or comparing. In `record_green`, resolve the argument with git rev-parse in verify mode peeled to a commit, store the full sha, and refuse when it does not resolve. In `tag_check`, resolve the `--commit` argument the same way before the comparison, and resolve a stored value that is not already a full sha so an old stamp is read safely. The existing `_full_sha` helper used for the forge query can serve both. Add tests in `test_release_cut.py` for the symbolic ref case, an abbreviated sha on either side, and an unresolvable argument.

## Acceptance Criteria

- [ ] **AC1** Given a throwaway repository with no remote where the gate was recorded green with `--commit HEAD` and a second commit was then made, when `release_cut.py tag-check --commit HEAD` runs, then it refuses, naming the first commit as the one the gate ran on. Fails on: 'green on HEAD' matching a tree the gate never ran on.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::TagCheckResolvesCommitsTests::test_a_symbolic_ref_recorded_at_one_commit_is_refused_at_another
- [ ] **AC2** Given `record-green` called with a symbolic ref or an abbreviated sha, when the stamp is read, then it holds the full commit sha; and `tag-check` given an abbreviated sha of that same commit is allowed. Fails on: an unresolved name stored in the stamp, or a false refusal of the same commit spelt differently.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::TagCheckResolvesCommitsTests::test_both_sides_are_compared_as_full_shas
- [ ] **AC3** Given an argument git cannot resolve to a commit, when `record-green` or `tag-check` is run with it, then the verb refuses naming the argument and `record-green` writes no stamp. Fails on: a stamp holding a name that is not a commit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::TagCheckResolvesCommitsTests::test_an_unresolvable_commit_is_refused_and_stamps_nothing

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
