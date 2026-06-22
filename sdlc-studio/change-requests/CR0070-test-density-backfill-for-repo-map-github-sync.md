# CR-0070: test-density backfill for repo_map github_sync lessons (review WS B1b)

> **Status:** Complete
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

World-class review WS B1b. All 36 scripts have a test file but density is uneven; the highest-risk under-tested scripts are repo_map.py, github_sync.py, lessons.py (~2-3 tests/100 LOC vs validate.py's ~10).

## Acceptance Criteria

- [x] raise test coverage on repo_map.py, github_sync.py, lessons.py toward the validate.py density bar
- [x] new tests are substantive (behaviour, edge cases), reviewed for triviality
- [x] no production behaviour change (one docstring tidy in lessons.refresh_last_updated)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |

## Findings (documented, not fixed)

- `repo_map.compute_in_degree`: dotted Python imports (`from src.core import X`) do not resolve to `core.py` (splitext treats `.core` as an extension), so package imports under-count `in_degree`. The module disclaims real module resolution; a test pins the current behaviour. Candidate future CR.
- `lessons.refresh_last_updated`: docstring/behaviour drift (said "add if missing"; only rewrites when present) - docstring corrected here; behaviour unchanged (the template always carries the marker).
