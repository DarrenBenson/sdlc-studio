# BG0353: telemetry._parse_iso rejects a valid ISO-8601 offset stamp, making a whole sprint report unreadable

> **Status:** Open
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

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ delivery lanes, dogfooding friction) | Filed |
