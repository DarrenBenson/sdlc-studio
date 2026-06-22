# CR-0070: test-density backfill for repo_map github_sync lessons (review WS B1b)

> **Status:** Proposed
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

World-class review WS B1b. All 36 scripts have a test file but density is uneven; the highest-risk under-tested scripts are repo_map.py, github_sync.py, lessons.py (~2-3 tests/100 LOC vs validate.py's ~10).

## Acceptance Criteria

- [ ] raise test coverage on repo_map.py, github_sync.py, lessons.py toward the validate.py density bar
- [ ] new tests are substantive (behaviour, edge cases), reviewed for triviality
- [ ] no production behaviour change

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
