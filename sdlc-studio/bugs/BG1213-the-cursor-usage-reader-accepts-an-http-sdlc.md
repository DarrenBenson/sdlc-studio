# BG1213: The Cursor usage reader accepts an http:// SDLC_STUDIO_CURSOR_API base, so an override would send the bearer key in cleartext

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_cursor.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py, changelog.d/BG1213.md
> **Evidence:** BG1210 round-1 verdict, scratchpad run5/BG1210-verdict-r1.txt.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T17:10:04Z

## Summary

2026-11-04, BG1210's review (pre-existing, from US0989's d4e1ca53). `meter_cursor.read` takes any `SDLC_STUDIO_CURSOR_API` base with no scheme check (`meter_cursor.py`:98), so an `http://` override sends `CURSOR_API_KEY` as a bearer header over plain HTTP. The default, `https://api.cursor.com`, is safe, and the PRD's Security NFR describes the call as an HTTPS GET.

## Steps to Reproduce

1. `SDLC_STUDIO_CURSOR_API=http://127.0.0.1:<port>` with a listening stub, both Cursor variables set and the Cursor meter selected.
2. The stub receives the Authorization header in cleartext.

## Proposed Fix

Refuse a base whose scheme is not https, except a loopback host for tests, with tokens None and a reason naming the variable.

## Acceptance Criteria

- [ ] **AC1** An http:// base on a non-loopback host is refused before any request, naming `SDLC_STUDIO_CURSOR_API.`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py

## Impact

A mistyped or test override leaks the operator's Cursor API key on the network.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
