# BG0958: `mutation.py` finds no changed lines when git's `diff.mnemonicPrefix` is set, so a mutation probe scoped to a unit's changes has nothing to mutate

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, changelog.d/BG0958.md
> **Evidence:** Pre-push boundary gate on 65e36b98, 2026-10-06; reproduced alone in a clean worktree; `git config --global diff.mnemonicprefix` is true on this machine.
> **Created:** 2026-10-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-06T18:30:03Z

## Summary

`changed_lines` runs `git diff -U0 <since>` and keeps the files from lines starting `+++ b/` (mutation.py:234-240). With `diff.mnemonicPrefix=true`, set globally on the operator's machine, git writes `+++ w/<path>`, and under `diff.noprefix` it writes `+++ <path>`, so no file matches and the changed-line map is empty. `ChangedLinesTests::test_reports_touched_lines_and_untracked_files` and `ChangedLineScopeCLITests::test_mutants_are_scoped_to_the_units_changed_lines` fail with KeyError on that machine and pass on CI. In use, `mutation.py run` scoped to a unit's changed lines finds nothing to mutate, which reads as a probe with nothing to report rather than one that never looked. Already in the code; triggered by a user's git config.

## Steps to Reproduce

git config --global diff.mnemonicPrefix true; pytest .claude/skills/sdlc-studio/scripts/tests/`test_mutation.py`::ChangedLinesTests::`test_reports_touched_lines_and_untracked_files` -> KeyError on the fixture path.

## Proposed Fix

Pass explicit prefixes to that `git diff` (`--src-prefix=a/ --dst-prefix=b/`, which override both mnemonicPrefix and noprefix), and pin it with tests whose fixture repository sets each config.

## Acceptance Criteria

- [ ] **AC1** With `diff.mnemonicPrefix` set in the repository's config, `changed_lines` reports the touched lines of each changed file
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::ChangedLinesTests::test_mnemonic_prefix_config_still_reports_lines
- [ ] **AC2** With `diff.noprefix` set, `changed_lines` reports the same lines
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::ChangedLinesTests::test_noprefix_config_still_reports_lines
- [ ] **AC3** The existing changed-line tests pass whatever the operator's global git config holds
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::ChangedLinesTests::test_reports_touched_lines_and_untracked_files

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | sdlc-studio | Filed |
