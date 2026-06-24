# CR-0093: authoring closing consistency pass ac-scope ts-check reconcile integrity

> **Status:** Complete
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

**WS3 of RFC0019. Estimate: 3 points. Depends on CR0089.** The authoring loop's **closing
consistency check** - "the thing that would actually replace me as the structural coordinator"
(the field agent). When `--goal design`/`plan` finishes, run the deterministic checks over the
produced backlog and surface them in the closing report: `ac_scope` (CR0086, cross-epic AC
references), `reconcile` (drift 0) + `reconcile fields` (CR0082, index derived), `validate`
(0 errors), `integrity` (every epic link resolves), and `ts-check` (CR0085) where test-specs
exist. Structural findings block the "reviewable backlog" claim; advisory ones (ac_scope) are
reported, not blocking.

## Acceptance Criteria

- [x] the closing pass runs `ac_scope` + `reconcile`/`reconcile fields` + `validate` +
      `integrity` (+ `ts-check` where a test-spec exists) and emits a consolidated report
- [x] a structural failure (drift, dangling link, validate error) blocks the
      "reviewable backlog" sign-off; advisory findings (cross-epic AC) are reported only
- [x] reuses the shipped checkers (no new verification logic); runs at the `design`/`plan`
      closing gate
- [x] unit/flow tests cover a clean backlog (passes) and a seeded defect (flagged);
      CHANGELOG `[Unreleased]` entry (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
