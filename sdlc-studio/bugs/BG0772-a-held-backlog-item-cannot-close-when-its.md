# BG0772: A held backlog item cannot close when its closing story ships

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_backlog_sweep.py
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T13:09:43Z

## Summary

D0264 holds 47 backlog items open until the EP0263 story named in each item's 'Closes with:' field ships. `test_lean_backlog_sweep.py`::BacklogSweepTests::`test_held_items_stay_open_naming_their_closing_story` asserts every HELD item is non-terminal unconditionally, so closing one after its story is Done turns the push red. At RUN-01M3BK9Y's close 25 items whose stories had shipped (US0909, US0910/US0934, US0911, US0912, US0913, US0916, US0935, and EP0218 with US0909 and US0911) were closed as superseded and 25 subtests failed at the push boundary; the closure was reverted and waits on this.

## Steps to Reproduce

1. Supersede BG0685 (Closes with: US0909; US0909 is Done). 2. pytest .claude/skills/sdlc-studio/scripts/tests/`test_lean_backlog_sweep.py`: the BG0685 subtest fails 'held open under D0264'.

## Proposed Fix

Assert a held item non-terminal only while any story its Closes-with field names is not yet Done, with a mutant that closes an item whose story is still open; then re-apply the 25 closures (revert of the revert of 3efa27e9).

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: D0264 holds 47 backlog items open until the EP0263 story named in each item's 'Closes with:' field ships.
- [ ] **AC2** The proposed fix lands, pinned by a test: Assert a held item non-terminal only while any story its Closes-with field names is not yet Done, with a mutant that closes an item whose story is still open...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
