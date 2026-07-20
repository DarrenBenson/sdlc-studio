# CR-0370: forward-port ships untracked test-cache directories into the installed skill

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** tools/forward-port.sh
> **Date:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

forward-port.sh rsyncs the working tree and excludes .local and `__pycache__`, but not .`pytest_cache.` rsync copies untracked files, and .`pytest_cache` is gitignored rather than absent, so a dev machine that has run pytest ships its cache into the installed skill copy. Observed in a dry run: scripts/.`pytest_cache`/v/cache/nodeids was listed for transfer. Harmless to behaviour, but it puts machine-specific junk into the copy that consuming tools load, and --delete means it also churns on every port.

## Impact

Anyone forward-porting after running the test suite, which is everyone following the documented workflow - the gate runs pytest. The installed copy accumulates files that are not part of the skill.

## Acceptance Criteria

- [ ] Given a dev tree containing .`pytest_cache`, when forward-port runs, then no cache directory is transferred to the installed copy
- [ ] Given the exclude list, when it is extended, then .local and `__pycache__` remain excluded exactly as today
- [ ] Given an installed copy that already holds a stale cache directory, when forward-port runs, then it is not left behind as an orphan by the exclude

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Raised |
