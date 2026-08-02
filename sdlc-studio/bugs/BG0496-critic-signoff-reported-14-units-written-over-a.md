# BG0496: critic signoff reported 14 units written over a record holding zero

> **Status:** Fixed
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Verification depth:** functional (reproduced through the shipped CLI before the fix - stdout said 14 written while the record held 0 rows; the mutant restoring the shipped count is KILLED, and the positive control asserts a signable unit is still counted)
> **Severity:** High
> **Points:** 2

## Summary

`critic.py signoff` over 14 units in a non-signable status printed both `signoff: 14 unit(s) SKIPPED and NOT written` on stderr AND `signoff: 14 unit(s) written` on stdout, over a `signoff-record.md` holding zero rows for them.

The skip path RETURNS rather than raising, so `_run_batch` saw no exception and counted the unit in `written`. The exit code (3) and the stderr list were already correct, which makes it worse rather than better: a reader who trusts the headline number is told the exact opposite of what happened, and the two lines disagree in the same output.

The comment directly above the skip reporting says this was already fixed once - 'The COUNT and the EXIT CODE must agree with the record. The first version named the skip on stderr and still printed N unit(s) written with rc 0'. The exit code half was fixed; the count half was not, and the comment reads as though both were.

## Steps to Reproduce

1. Put a unit in a status that is neither terminal nor awaiting sign-off (e.g. Ready).
2. `critic.py signoff --units <id> --principal X --author Y --note z`.
3. stdout says `1 unit(s) written`; stderr says `1 unit(s) SKIPPED and NOT written`; grep the signoff record for the id -> zero rows.

## Proposed Fix

Repaired in this run: `_run_batch` takes the skipped set and excludes it from `written` before printing, so the count is derived from what was actually recorded. Pin it with a test that asserts the printed count equals the number of rows in the record - LL0008, a deterministic tool must never report success it did not achieve.

## Impact

The sign-off record is the reviewer-of-record half of the two-role gate. A command that reports 14 sign-offs written when none landed is the precise false-clean the batch contract exists to prevent, and it was found only because the operator's close rule forced a batch sign-off over units in the wrong status.

## Acceptance Criteria

### AC1: the printed count equals what the record holds

- **Then** a batch in which every unit is skipped prints `0 unit(s) written`, asserted against
  the row count in `signoff-record.md` rather than against another number the test computes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SkippedCountTests::test_the_printed_count_matches_the_record
- **Verified:** yes (2026-08-02)

### AC2: a signable unit is still counted

- **Then** a unit awaiting the reviewer of record is written and counted, so the fix
  discriminates rather than reporting zero unconditionally
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::SkippedCountTests::test_a_signable_unit_is_still_counted
- **Verified:** yes (2026-08-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
