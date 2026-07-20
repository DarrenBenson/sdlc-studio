# BG0217: validate's placeholder warning uses a severity spelling the counters do not count

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

validate emits severity 'warn' for a pre-Ready story's placeholder AC, but every other warning in the file uses 'warning' and the summary counters count only 'warning'. So a Draft story with three placeholder ACs prints three WARN lines and then reports 'checked=1 errors=0 warnings=0'. Reproduced in a clean workspace. The per-line output and the JSON violations array are correct; anything reading the summary count, including a human skimming the last line, sees zero warnings where three were reported. A summary that contradicts the output above it is the same false-completeness class as a dry run that disagrees with its real run.

## Steps to Reproduce

1. Create a workspace with one story at Status Draft whose acceptance criteria are all placeholders. 2. Run validate.py check. 3. Three WARN lines print. 4. The final line reads checked=1 errors=0 warnings=0.

## Proposed Fix

Emit the same severity string the counters count, or count both spellings in one place. Prefer a single shared constant so a third spelling cannot be introduced. Add a test asserting the reported warning count equals the number of warning lines produced - the counter and the output must agree.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
