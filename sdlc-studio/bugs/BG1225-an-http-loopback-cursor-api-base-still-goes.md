# BG1225: An http loopback Cursor API base still goes through an http_proxy in cleartext with the key on it

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_cursor.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py, changelog.d/BG1225.md
> **Evidence:** BG1213 builder report and round-1 verdict, scratchpad run6/BG1213-verdict-r1.txt.
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-05T10:07:06Z

## Summary

2026-11-05, BG1213's build and review (pre-existing). `meter_cursor.read_cloud` allows an http base only on a loopback IP after BG1213, but urllib's default ProxyHandler sends that request to the proxy named by `http_proxy` when `no_proxy` does not cover the host, so the Basic-auth key crosses the network in cleartext.

## Steps to Reproduce

1. Set `http_proxy` to a listening stub and `SDLC_STUDIO_CURSOR_API` to `http://127.0.0.1:<port>`, with no `no_proxy.`
2. Read the Cursor cloud meter: the stub proxy receives the Authorization header.

## Proposed Fix

Build the opener with an empty ProxyHandler for an http loopback base, so the request never leaves the machine.

## Acceptance Criteria

- [ ] **AC1** With `http_proxy` set and no `no_proxy`, an http loopback base is read directly and the proxy stub receives nothing; an https base still honours the proxy.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py::CursorCloudTests

## Impact

Low: it needs both an http override and a proxy in the environment, but the key then leaves the machine in cleartext.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | claude | Filed |
