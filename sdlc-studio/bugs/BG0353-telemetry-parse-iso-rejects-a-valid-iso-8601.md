# BG0353: telemetry._parse_iso rejects a valid ISO-8601 offset stamp, making a whole sprint report unreadable

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/telemetry.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction); agent; skill v5.0.0

## Summary

A timestamp carrying a UTC offset is silently rejected, and one unparseable stamp takes the entire sprint report with it - the report reads as having no data rather than as having one bad row.

## Steps to Reproduce

cd /home/darren/code/DarrenBenson/sdlc-studio/.claude/skills/sdlc-studio/scripts && python3 -c "import sys; sys.path.insert(0,'.'); import telemetry; print(`telemetry._parse_iso(`'2026-07-28T09:00:00+00:00'))"  ->  `None`.

## Proposed Fix

See the summary; each cited site names its own remedy.

## Acceptance Criteria

### AC1: a stamp carrying an explicit UTC offset reads as the instant it names

- **Given** a run state or series row stamped `2026-07-28T09:00:00+00:00` - the form
  `datetime.now(timezone.utc).isoformat()` writes, live in gate.py and review_prep.py
- **When** the measurement path reads it
- **Then** it parses to the same instant as the `Z` form, a non-UTC offset is normalised rather
  than read as wall-clock, and the gap or window it bounds is measured rather than dropped; a
  stamp with NO offset is still refused, because calling it UTC would invent the missing fact
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py::StampParsingTests
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction) | Filed |
| 2026-07-28 | Claude Fable 5 (RUN-01KYKVZM lane) | Acceptance criterion authored and fixed: the bug carried none, so `verify_ac` reported ac=0 and the unit could not prove itself |
