# CR-0073: doc-freshness advisory gate check LATEST claims vs reality (review WS B4)

> **Status:** Complete
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

World-class review WS B4. Nothing caught LATEST.md being factually wrong (it claimed 606 tests/66 advisories/RFC0013-deferred when reality was 622/0/shipped). Add a new advisory `doc-freshness` gate check that compares LATEST.md's claimed facts against reality - the recurring drift the skill exists to prevent.

## Acceptance Criteria

- [x] new `scripts/doc_freshness.py` compares LATEST.md's claimed version / test count / disclosure count against reality (SKILL.md version, the `def test_` census, `disclosure.check`)
- [x] registered in `gate.py` DEFAULT_CHECKS as **advisory** (non-blocking), skill-only (no-op for consuming projects)
- [x] tests + reference-scripts.md entry (doc-coverage); the check passes against the freshly-updated LATEST.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
