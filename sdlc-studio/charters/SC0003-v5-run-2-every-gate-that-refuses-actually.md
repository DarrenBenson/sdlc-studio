# SC0003: v5 run 2: every gate that refuses actually refuses, and the criteria the README claims are run do run

> **Status:** Spent
> **Queue rank:** 2
> **Created:** 2026-08-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Appetite:** 480min/8units
> **Scope query:** --bugs Open

## Sprint Goal

No lane in the release gate reports a state it cannot back: the red criteria are repaired, and a gate that prints REFUSED returns non-zero.

## Scope rule

BG0535 as re-measured, BG0542, BG0543, BG0536, BG0557, plus CR0508 once refined.

The re-measurement matters more than the bug list. `gate.py --release` on 167e7e38, 2026-08-09,
1,778s: **53 red criteria of 1,876, not the 106 BG0535 records.** The recorded figure had never
been re-run, exactly as LATEST.md warned, and it is out by half.

The 53 are not broken features. Sampling the ten the gate names: `US0063::AC1` invokes
`audit_check.py`, which does not exist; `US0070::AC1` invokes `test_review_generate.py`, which
does not exist; `US0021::AC1`, `US0040::AC3`, `US0042::AC2` and `US0052::AC4` name test methods
that were renamed out of files that do still exist. This is stale-selector rot, so the unit of
work is a mechanical repair plus the guard that stops it recurring - CR0508 already describes
that guard: a `Verify:` selector naming a test that does not exist is accepted at write time.
Repairing 53 selectors without landing the guard buys one green run and nothing else.

Grouped with them are the three gates that print a refusal and do not perform one - BG0542
(`sprint plan` under `affects_check: block` exits 0 and writes the unit anyway), BG0543 (the
warning ratchet exits 0 on a stale baseline), BG0557 (`close --dry-run` reports a STOP the real
close does not) - because they are one defect class and a project consuming any of them is being
told it is protected by something that is not running. BG0536 rides here for its blast radius:
the fixture that took a caller-supplied root destroyed 23 mutation registrations in this
repository, and it ships in `scripts/tests/`.

## Seat review

_Not yet reviewed._

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Created via `new` (deterministic) |
