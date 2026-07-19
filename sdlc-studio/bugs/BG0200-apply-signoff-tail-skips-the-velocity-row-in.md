# BG0200: apply-signoff tail skips the velocity row in silence when the retro was not scaffolded by the close

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; both guards mutation-proven)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The apply-signoff tail reads the retro id from run-state `scaffolded_retro` and does nothing at all when it is absent - no row, no warning, and the close still prints success. A retro created with artifact.py new (the documented way to scaffold one, and what the operator has asked for) never sets that field, so the velocity row is skipped and nothing says so. This is the second half of BG0195: that fixed the case where the id was present but in the dashed form the resolver could not match; this is the case where no id reaches the tail at all. Both produce the same outcome - a close that reports success while the measurement it owes goes unrecorded. Hit at the RUN-01KXVD74 close, where the row had to be written by hand afterwards.

## Steps to Reproduce

1. Scaffold a retro with artifact.py new --type retro (run-state `scaffolded_retro` stays null). 2. Run sprint close --retro RETROxxxx --apply-signoff. 3. Observe the sign-off, epic derivation and handoff refresh all report, and NO velocity line appears. 4. Confirm VELOCITY.md has no row for that retro.

## Proposed Fix

Fall back to the --retro argument the close was invoked with (it is already resolved and validated by `_resolve_retro)` rather than reading only `scaffolded_retro`, and when no id can be resolved say so on the tail instead of returning silently. The existing failure branch already prints 'velocity not recorded (...)' - the absent-id path should reach it rather than skipping the block.

## Regression Test

`test_ApplySignoffTail_records_velocity_from_the_close_retro_argument` reproduces the reported
close: a retro scaffolded the documented way leaves run-state `scaffolded_retro` unset, and the
tail must still record the row. A sibling test asserts the tail says so out loud when no id
resolves from either source, so the silent-skip path cannot return uncovered.

Run it with:
`python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint.py -k ApplySignoffTailTests`
(a citation, not a machine-executed `Verify:` line - only a story's Verify line is run).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Filed |
| 2026-07-19 | sdlc-studio | Fixed; regression test cited |
