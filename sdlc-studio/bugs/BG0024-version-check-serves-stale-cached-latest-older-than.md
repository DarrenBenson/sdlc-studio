# BG0024: version_check serves stale cached latest older than installed reports up-to-date wrongly

> **Status:** Closed
> **Created:** 2026-06-21
> **Created-by:** sdlc-studio new
> **Severity:** Medium

## Summary

`version_check` reported `up-to-date (installed 2.4.0, latest 2.1.0)` - the cached `latest` (2.1.0)
was older than what's installed (2.4.0), an impossible state that nonetheless read as up-to-date.
Root cause: the TTL cache (`.local/version-check.json`, 24h) was 22.2h old and served its stale
`latest: 2.1.0` without re-fetching. `latest_release()` itself was correct (returns 2.4.0 live);
the cache, written the day before across several same-window releases, was the culprit.

## Steps to Reproduce

After cutting releases within the 24h TTL window: `version_check.py check` -> reports the
pre-window `latest`, older than installed, status "up-to-date".

## Proposed Fix

In `check()`, treat a fresh cache as stale when its `latest` is older than the installed version
(`_gt(installed, cached)`) and re-fetch - you cannot install newer-than-latest, so a release
shipped since the cache. Fixed; verified live (`latest` -> 2.4.0) + regression tests.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | sdlc | Created via `new` (deterministic) |
