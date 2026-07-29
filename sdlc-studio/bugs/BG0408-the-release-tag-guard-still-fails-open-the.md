# BG0408: The release tag guard still fails OPEN: the swallow moved one frame down into the delivery scan, and an unreadable tree reports a clean release

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py
> **Evidence:** Round-2 independent review of commit 06c806d7, repair 2. Measured against a real workspace with `chmod 000 sdlc-studio/stories`.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** round-2 independent review; human; v1

## Summary

The repair is real as far as it goes - a corrupt baseline is now detected (`report.get("corrupt")` is the correct key against `close_owed.owed`'s return shape, and three mutants confirm it), and the old tests that stubbed the function out now drive it.

But the thesis of the fix was that deleting or truncating one tracked file disarmed the release guard. An UNREADABLE delivery tree does exactly the same thing, and the new `except` never fires, because `scan_delivery` reaches `artifact_files`/`read_text_safe`, which swallow the I/O error themselves. `owed()` returns normally with an empty list, so there is nothing for `_close_owed_units` to catch:

```text
READABLE   -> (['US0001'], None) | tag: (False, '1 delivery unit(s) reached a terminal status with no retro...')
chmod 000 sdlc-studio/stories
UNREADABLE -> ([], None)         | tag: (True,  'gate green ... and no close is owed')
```

`unknown` is `None`. The tag guard asserts a positive falsehood - the exact defect the repair was written for, one frame down the stack. A guard that treats "I could not read the tree" as "the tree is clean" is the fail-open direction this project's design says a guard must never take, and this is the only live guard on a release tag.

## Steps to Reproduce

1. In a workspace with one delivery unit at a terminal status and no retro, call `release_cut.tag_check` - it correctly refuses.
2. `chmod 000 sdlc-studio/stories`.
3. Call `tag_check` again: it now ALLOWS the tag, with `unknown` unset. The refusal disappeared because the tree became unreadable.

## Proposed Fix

The read helpers are right to swallow - a corpus scan should not die on one bad file - but they must SAY they swallowed. Give `artifact_files`/`read_text_safe` a way to report unreadable entries (a count, or a list), have `scan_delivery` propagate it into the report `owed()` returns, and have `_close_owed_units` treat a non-zero unreadable count as `unknown` exactly as it treats `corrupt`.

The general rule this is an instance of: a helper that degrades silently converts every guard above it into a fail-open guard. The degradation has to reach the caller that is making a safety decision.

## Acceptance Criteria

- [ ] A delivery tree that cannot be read produces an `unknown` refusal reason from `_close_owed_units`, not an empty unit list.
- [ ] `release_cut.tag_check` refuses a tag when the delivery scan could not read part of the tree, and names what it could not read.
- [ ] A test makes part of the delivery tree unreadable and asserts the tag is refused - the mutant that restores the silent degradation reddens it.
- [ ] The corrupt-baseline and no-baseline branches keep their current behaviour, so the fix does not regress what the previous repair got right.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | round-2 independent review | Filed |
