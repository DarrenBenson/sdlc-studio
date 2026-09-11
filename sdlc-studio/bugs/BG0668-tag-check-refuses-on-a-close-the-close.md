# BG0668: tag-check refuses on a close the close-owed predicate says is not owed

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py
> **Evidence:** RUN-01M20RWX close-out, 2026-09-11: the v5.1.0 tag was refused on BG0663, a close-time repair terminal after RETRO0116 was written. Probed by writing the override into RETRO0116 and recomputing: close_repair_overrides gained the row, unaccounted stayed empty and is_owed returned False, while `owed` still held ('BG0663', 'bug') and tag-check still refused.
> **Created:** 2026-09-11
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`release_cut.py`'s tag guard reads the close-owed report's `owed` list, which deliberately keeps every uncovered terminal unit including those a recorded Close-repair-override fully accounts for. The predicate that answers whether a close is genuinely owed is `close_owed.blocking(report)[`'units'], which is what `is_owed` and the detect exit code both read. So a release can be refused a tag by a unit that `close_owed` itself reports as accounted for - and the remedy the refusal prints, recording the override, cannot clear it, because an overridden unit never leaves `owed`. This is BG0518's defect surviving one layer up: that bug fixed exactly this split in `close_owed` detect's own headline, and the release guard was not brought with it.

## Steps to Reproduce

1. Deliver a unit to a terminal status after the run's retro is written, so it is a close-time repair.
2. Record the override the tool prints: a `Close-repair-override` line in that retro naming the unit and a reason.
3. Run `close_owed.py` detect - it exits 0 and reports the close is not owed.
4. Run `release_cut.py` tag-check --commit HEAD - it refuses, naming that same unit as owing a close.
The two commands read one question and answer it differently, and only the second one blocks a release.

## Proposed Fix

In `_close_owed_units`, return the blocking predicate rather than the raw list: read `close_owed.blocking(report)[`'units'] instead of report['owed']. blocking() already falls back to `owed` when `unaccounted` is absent, so an older report shape is unchanged. Nothing else in the guard moves: an unreadable baseline, a degraded scan and a missing baseline keep their existing refusals, which are the fail-closed cases the function was rewritten for.

## Acceptance Criteria

- [ ] **AC1** Given a corpus whose only uncovered terminal unit is a close-time repair carrying a recorded Close-repair-override, when `tag_check` runs on the recorded green commit, then it does not refuse on that unit - the same corpus `close_owed.is_owed` reports False for
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::TagCheckReadsTheBlockingPredicateTests::test_an_overridden_close_repair_does_not_refuse_the_tag
- [ ] **AC2** Given a corpus holding a terminal unit no retro covers and no override names, when `tag_check` runs, then it still refuses and names that unit - the guard is narrowed to the predicate, not switched off
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::TagCheckReadsTheBlockingPredicateTests::test_a_unit_no_retro_or_override_covers_still_refuses
- [ ] **AC3** Given a close-owed report carrying no `unaccounted` key at all, when `_close_owed_units` reads it, then it falls back to `owed` and refuses exactly as it does today, so a report written by an older `close_owed` is judged no more leniently
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::TagCheckReadsTheBlockingPredicateTests::test_a_report_without_unaccounted_falls_back_to_owed

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-11 | sdlc-studio | Filed |
