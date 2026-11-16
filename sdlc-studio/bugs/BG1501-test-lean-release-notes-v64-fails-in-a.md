# BG1501: test_lean_release_notes_v64 fails in a tree that is not a git clone: its text checks read v6.3.0 through git, so FrozenNotesTests' copy goes red and the push gate refuses

> **Status:** Fixed
> **Severity:** High
> **Points:** 2
> **Affects:** tools/tests/test_lean_release_notes_v64.py, changelog.d/BG1501.md
> **Evidence:** Push of 3e7f8cd4 refused on devserver1, 2026-11-16, full-suite 2 red.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T06:33:27Z

## Summary

The push of 3e7f8cd4 was refused at the push boundary: tools/tests/`test_lean_release_notes.py`::FrozenNotesTests::`test_filing_a_finding_reddens_no_test` copies the working tree (no .git) and runs every module that reads the notes; in that copy `test_lean_release_notes_v64` (US1170, run fifteen) fails `test_every_changed_behaviour_names_what_to_do` ('the section says `sprint.fresh_session` de...') and `test_the_63_upgrade_path_is_given` ('premise: 6.4's shipped defaults add keys', an empty dict). setUpModule skips only the CLI checks outside a clone; the text checks that diff 6.4's shipped defaults against v6.3.0 read the tag through git and find nothing, so they fail instead of skipping.

## Steps to Reproduce

pytest tools/tests/`test_lean_release_notes.py`::FrozenNotesTests::`test_filing_a_finding_reddens_no_test`

## Proposed Fix

Skip, naming why, every check in `test_lean_release_notes_v64` that needs git history (the v6.3.0 tag) when the tree is not a git clone, as setUpModule already does for the CLI checks; keep failing a clone that lacks the tag.

## Acceptance Criteria

- [ ] **AC1** Given a copy of the working tree that is not a git clone, when FrozenNotesTests files a finding and runs every notes reader, then `test_lean_release_notes_v64` skips its history checks and the run is green. Fails on: a history check failing outside a clone.
  - **Verify:** pytest tools/tests/test_lean_release_notes.py::FrozenNotesTests::test_filing_a_finding_reddens_no_test
  - **Verified:** yes (2026-11-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
